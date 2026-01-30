"""
Email Client Module - GriPro

IMAP integration for Primo to receive and respond to project requests.
Connects to Dreamhost email server.

Email: Henry.Primo@centual.eu
"""
from __future__ import annotations

import email
import imaplib
import smtplib
import re
from dataclasses import dataclass, field
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Optional
from email.header import decode_header
import os


@dataclass
class EmailConfig:
    """Email server configuration for Dreamhost."""
    # IMAP Settings (incoming)
    IMAP_HOST: str = "imap.dreamhost.com"
    IMAP_PORT: int = 993
    IMAP_SSL: bool = True

    # SMTP Settings (outgoing)
    SMTP_HOST: str = "smtp.dreamhost.com"
    SMTP_PORT: int = 465
    SMTP_SSL: bool = True

    # Account credentials
    EMAIL: str = "Henry.Primo@centual.eu"
    PASSWORD: str = ""  # Set via environment variable

    @classmethod
    def from_env(cls) -> "EmailConfig":
        """Load config from environment variables."""
        return cls(
            PASSWORD=os.getenv("PRIMO_EMAIL_PASSWORD", ""),
        )


@dataclass
class ProjectRequest:
    """Parsed project request from email."""
    email_id: str
    from_email: str
    from_name: str
    subject: str
    body: str
    received_at: datetime

    # Extracted data
    client_nif: Optional[str] = None
    company_name: Optional[str] = None
    project_summary: Optional[str] = None
    requirements: List[str] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)

    # Status tracking
    is_processed: bool = False
    project_id: Optional[str] = None

    def extract_nif(self) -> Optional[str]:
        """Extract NIF/CIF from email body."""
        # Spanish NIF patterns: 8 digits + letter OR letter + 7 digits + letter
        nif_patterns = [
            r'\b[0-9]{8}[A-Z]\b',           # DNI: 12345678A
            r'\b[A-Z][0-9]{7}[A-Z0-9]\b',   # CIF: A1234567B
            r'\b[XYZ][0-9]{7}[A-Z]\b',      # NIE: X1234567A
        ]

        for pattern in nif_patterns:
            match = re.search(pattern, self.body.upper())
            if match:
                self.client_nif = match.group()
                return self.client_nif
        return None

    def to_dict(self) -> dict:
        return {
            "email_id": self.email_id,
            "from_email": self.from_email,
            "from_name": self.from_name,
            "subject": self.subject,
            "received_at": self.received_at.isoformat(),
            "client_nif": self.client_nif,
            "company_name": self.company_name,
            "project_summary": self.project_summary,
            "requirements": self.requirements,
            "is_processed": self.is_processed,
            "project_id": self.project_id,
        }


@dataclass
class EmailThread:
    """Thread of emails for a project conversation."""
    project_id: str
    client_email: str
    messages: List[dict] = field(default_factory=list)
    status: str = "active"  # active, requirements_defined, closed

    def add_message(self, direction: str, subject: str, body: str):
        """Add a message to the thread."""
        self.messages.append({
            "direction": direction,  # "incoming" or "outgoing"
            "subject": subject,
            "body": body,
            "timestamp": datetime.utcnow().isoformat(),
        })


class PrimoEmailClient:
    """
    Email client for Primo to receive and manage project requests.

    Workflow:
    1. Check inbox for new project requests
    2. Parse email to extract NIF, requirements, company info
    3. Create project in system with NIF as dashboard password
    4. Reply to client to clarify requirements
    5. Continue conversation until requirements are fully defined
    """

    def __init__(self, config: Optional[EmailConfig] = None):
        self.config = config or EmailConfig.from_env()
        self._imap: Optional[imaplib.IMAP4_SSL] = None
        self._threads: Dict[str, EmailThread] = {}

    def connect_imap(self) -> bool:
        """Connect to IMAP server."""
        try:
            if self.config.IMAP_SSL:
                self._imap = imaplib.IMAP4_SSL(
                    self.config.IMAP_HOST,
                    self.config.IMAP_PORT
                )
            else:
                self._imap = imaplib.IMAP4(
                    self.config.IMAP_HOST,
                    self.config.IMAP_PORT
                )

            self._imap.login(self.config.EMAIL, self.config.PASSWORD)
            return True
        except Exception as e:
            print(f"[Primo Email] Connection failed: {e}")
            return False

    def disconnect(self):
        """Disconnect from IMAP server."""
        if self._imap:
            try:
                self._imap.logout()
            except:
                pass
            self._imap = None

    def _decode_header_value(self, value: str) -> str:
        """Decode email header value."""
        if not value:
            return ""

        decoded_parts = decode_header(value)
        result = []
        for part, charset in decoded_parts:
            if isinstance(part, bytes):
                result.append(part.decode(charset or 'utf-8', errors='replace'))
            else:
                result.append(part)
        return ' '.join(result)

    def _get_email_body(self, msg: email.message.Message) -> str:
        """Extract plain text body from email."""
        body = ""

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or 'utf-8'
                        body = payload.decode(charset, errors='replace')
                        break
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or 'utf-8'
                body = payload.decode(charset, errors='replace')

        return body

    def check_inbox(self, folder: str = "INBOX", unread_only: bool = True) -> List[ProjectRequest]:
        """
        Check inbox for new project requests.

        Args:
            folder: Mailbox folder to check
            unread_only: Only return unread emails

        Returns:
            List of ProjectRequest objects
        """
        if not self._imap:
            if not self.connect_imap():
                return []

        requests = []

        try:
            self._imap.select(folder)

            # Search criteria
            criteria = "(UNSEEN)" if unread_only else "ALL"
            _, message_numbers = self._imap.search(None, criteria)

            for num in message_numbers[0].split():
                _, msg_data = self._imap.fetch(num, "(RFC822)")
                email_body = msg_data[0][1]
                msg = email.message_from_bytes(email_body)

                # Parse email
                from_header = self._decode_header_value(msg.get("From", ""))
                subject = self._decode_header_value(msg.get("Subject", ""))
                date_str = msg.get("Date", "")

                # Extract email address and name
                from_match = re.search(r'([^<]*)<([^>]+)>', from_header)
                if from_match:
                    from_name = from_match.group(1).strip()
                    from_email = from_match.group(2).strip()
                else:
                    from_name = ""
                    from_email = from_header.strip()

                # Parse date
                try:
                    received_at = email.utils.parsedate_to_datetime(date_str)
                except:
                    received_at = datetime.utcnow()

                # Create ProjectRequest
                request = ProjectRequest(
                    email_id=num.decode() if isinstance(num, bytes) else str(num),
                    from_email=from_email,
                    from_name=from_name,
                    subject=subject,
                    body=self._get_email_body(msg),
                    received_at=received_at,
                )

                # Extract NIF if present
                request.extract_nif()

                requests.append(request)

        except Exception as e:
            print(f"[Primo Email] Error checking inbox: {e}")

        return requests

    def send_reply(
        self,
        to_email: str,
        subject: str,
        body: str,
        in_reply_to: Optional[str] = None,
    ) -> bool:
        """
        Send email reply to client.

        Args:
            to_email: Recipient email
            subject: Email subject
            body: Email body (plain text)
            in_reply_to: Original message ID for threading

        Returns:
            True if sent successfully
        """
        try:
            msg = MIMEMultipart()
            msg["From"] = f"Henry Primo <{self.config.EMAIL}>"
            msg["To"] = to_email
            msg["Subject"] = subject

            if in_reply_to:
                msg["In-Reply-To"] = in_reply_to
                msg["References"] = in_reply_to

            msg.attach(MIMEText(body, "plain", "utf-8"))

            # Connect to SMTP
            if self.config.SMTP_SSL:
                server = smtplib.SMTP_SSL(
                    self.config.SMTP_HOST,
                    self.config.SMTP_PORT
                )
            else:
                server = smtplib.SMTP(
                    self.config.SMTP_HOST,
                    self.config.SMTP_PORT
                )
                server.starttls()

            server.login(self.config.EMAIL, self.config.PASSWORD)
            server.send_message(msg)
            server.quit()

            return True

        except Exception as e:
            print(f"[Primo Email] Error sending email: {e}")
            return False

    def send_project_confirmation(
        self,
        to_email: str,
        project_name: str,
        project_code: str,
        nif: str,
        dashboard_url: str = "https://dashboard.centual.eu",
    ) -> bool:
        """
        Send project creation confirmation with dashboard access.

        The NIF serves as the dashboard password.
        """
        subject = f"[GriPro] Proyecto Confirmado: {project_name}"

        body = f"""Hola,

Tu proyecto ha sido registrado en nuestro sistema.

DATOS DE ACCESO AL DASHBOARD:
- URL: {dashboard_url}
- Codigo de Proyecto: {project_code}
- Contrasena: {nif}

En el dashboard podras:
- Ver el avance del proyecto en tiempo real
- Comunicarte conmigo directamente via chat
- Ver las actividades del equipo de desarrollo
- Consultar el desglose de horas

Ya estoy trabajando en el analisis inicial. Te contacto pronto con el plan de trabajo propuesto.

Saludos,
Henry Primo
Project Manager
Grid Code Corporation

---
Este correo fue enviado automaticamente.
Para consultas urgentes, responde a este email o usa el chat del dashboard.
"""

        return self.send_reply(to_email, subject, body)

    def send_requirements_clarification(
        self,
        to_email: str,
        project_name: str,
        questions: List[str],
    ) -> bool:
        """Send email to clarify requirements."""
        subject = f"Re: {project_name} - Aclaraciones necesarias"

        questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])

        body = f"""Hola,

Estuve revisando el requerimiento de {project_name} y necesito aclarar algunos puntos antes de armar el plan de trabajo:

{questions_text}

Con esta info puedo definir mejor el equipo y los tiempos.

Quedo atento.

Saludos,
Henry Primo
Project Manager
"""

        return self.send_reply(to_email, subject, body)

    def get_thread(self, project_id: str) -> Optional[EmailThread]:
        """Get email thread for a project."""
        return self._threads.get(project_id)

    def create_thread(self, project_id: str, client_email: str) -> EmailThread:
        """Create new email thread for project."""
        thread = EmailThread(project_id=project_id, client_email=client_email)
        self._threads[project_id] = thread
        return thread


# Singleton instance
_email_client: Optional[PrimoEmailClient] = None


def get_email_client() -> PrimoEmailClient:
    """Get the singleton email client instance."""
    global _email_client
    if _email_client is None:
        _email_client = PrimoEmailClient()
    return _email_client


# Project intake workflow
class ProjectIntakeWorkflow:
    """
    Workflow for processing new project requests via email.

    Steps:
    1. Receive email with project request
    2. Extract NIF (becomes dashboard password)
    3. Parse requirements
    4. If unclear, email client for clarification
    5. Once requirements clear, create project and send confirmation
    6. Primo begins analysis (min 4h for architecture/infrastructure)
    """

    def __init__(self):
        self.email_client = get_email_client()

    def process_new_request(self, request: ProjectRequest) -> dict:
        """
        Process a new project request.

        Returns:
            Status dict with next steps
        """
        result = {
            "status": "pending",
            "request_id": request.email_id,
            "client_email": request.from_email,
            "nif_extracted": request.client_nif is not None,
            "needs_clarification": False,
            "clarification_questions": [],
            "project_created": False,
            "project_id": None,
        }

        # Check if NIF was extracted
        if not request.client_nif:
            result["needs_clarification"] = True
            result["clarification_questions"].append(
                "Por favor, incluye el NIF/CIF de tu empresa para poder registrar el proyecto."
            )

        # Analyze requirements completeness
        analysis = self._analyze_requirements(request.body)

        if analysis["missing"]:
            result["needs_clarification"] = True
            result["clarification_questions"].extend(analysis["questions"])

        # If needs clarification, send email
        if result["needs_clarification"]:
            self.email_client.send_requirements_clarification(
                to_email=request.from_email,
                project_name=request.subject,
                questions=result["clarification_questions"],
            )
            result["status"] = "awaiting_clarification"
        else:
            # Create project
            project = self._create_project(request)
            result["status"] = "project_created"
            result["project_created"] = True
            result["project_id"] = project["id"]

            # Send confirmation
            self.email_client.send_project_confirmation(
                to_email=request.from_email,
                project_name=project["name"],
                project_code=project["code"],
                nif=request.client_nif,
            )

        return result

    def _analyze_requirements(self, body: str) -> dict:
        """Analyze if requirements are complete enough."""
        missing = []
        questions = []

        # Check for key elements
        body_lower = body.lower()

        # Check for objective/goal
        if not any(word in body_lower for word in ["objetivo", "meta", "necesito", "quiero", "busco"]):
            missing.append("objective")
            questions.append("Cual es el objetivo principal del proyecto? Que problema queres resolver?")

        # Check for scope indicators
        if not any(word in body_lower for word in ["pagina", "app", "sistema", "plataforma", "api"]):
            missing.append("scope")
            questions.append("Que tipo de solucion necesitas? (web, app movil, sistema interno, API, etc.)")

        # Check for users/audience
        if not any(word in body_lower for word in ["usuario", "cliente", "publico", "interno"]):
            missing.append("audience")
            questions.append("Quienes van a usar este sistema? (clientes finales, empleados, ambos?)")

        return {
            "missing": missing,
            "questions": questions,
            "completeness": 1 - (len(missing) / 3),
        }

    def _create_project(self, request: ProjectRequest) -> dict:
        """Create a new project from request."""
        import uuid

        project_id = str(uuid.uuid4())[:8]

        # Generate project code from company info
        company_prefix = "GRIP"
        if request.client_nif:
            company_prefix = request.client_nif[:3].upper()

        project_code = f"{company_prefix}-{project_id[:4].upper()}"

        project = {
            "id": project_id,
            "code": project_code,
            "name": request.subject or "Nuevo Proyecto",
            "client_email": request.from_email,
            "client_nif": request.client_nif,
            "dashboard_password": request.client_nif,  # NIF as password
            "requirements_raw": request.body,
            "status": "intake",
            "created_at": datetime.utcnow().isoformat(),
            "created_by": "primo",
        }

        return project
