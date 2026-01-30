"""
Telegram Bot Integration - GriPro

Provides real-time communication channel with clients via Telegram.
Connected via BotFather API.

Features:
- Project-specific conversations
- Correction confirmations
- Dynamic requirement adjustments
"""
from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, List, Optional
from uuid import uuid4

# Note: Requires python-telegram-bot package
# pip install python-telegram-bot


class ConversationState(Enum):
    """State of conversation with client."""
    IDLE = "idle"
    AWAITING_PROJECT_CODE = "awaiting_project_code"
    ACTIVE_CONVERSATION = "active_conversation"
    AWAITING_CORRECTION_CONFIRMATION = "awaiting_correction_confirmation"
    AWAITING_APPROVAL = "awaiting_approval"


@dataclass
class TelegramMessage:
    """A message in a Telegram conversation."""
    message_id: str
    chat_id: int
    user_id: int
    username: Optional[str]
    text: str
    timestamp: datetime
    direction: str  # "incoming" or "outgoing"
    is_correction_request: bool = False
    correction_confirmed: bool = False


@dataclass
class ProjectConversation:
    """Telegram conversation for a specific project."""
    project_id: str
    project_code: str
    chat_id: int
    user_id: int
    username: Optional[str]
    state: ConversationState = ConversationState.ACTIVE_CONVERSATION
    messages: List[TelegramMessage] = field(default_factory=list)
    pending_corrections: List[dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)

    def add_message(self, text: str, direction: str, is_correction: bool = False) -> TelegramMessage:
        """Add a message to the conversation."""
        msg = TelegramMessage(
            message_id=str(uuid4())[:8],
            chat_id=self.chat_id,
            user_id=self.user_id,
            username=self.username,
            text=text,
            timestamp=datetime.utcnow(),
            direction=direction,
            is_correction_request=is_correction,
        )
        self.messages.append(msg)
        self.last_activity = datetime.utcnow()
        return msg

    def request_correction_confirmation(self, correction_text: str) -> dict:
        """Request client confirmation for a correction."""
        correction = {
            "id": str(uuid4())[:8],
            "text": correction_text,
            "requested_at": datetime.utcnow().isoformat(),
            "confirmed": False,
            "confirmed_at": None,
        }
        self.pending_corrections.append(correction)
        self.state = ConversationState.AWAITING_CORRECTION_CONFIRMATION
        return correction

    def confirm_correction(self, correction_id: str) -> bool:
        """Confirm a pending correction."""
        for correction in self.pending_corrections:
            if correction["id"] == correction_id:
                correction["confirmed"] = True
                correction["confirmed_at"] = datetime.utcnow().isoformat()
                self.state = ConversationState.ACTIVE_CONVERSATION
                return True
        return False

    def get_conversation_history(self) -> List[dict]:
        """Get formatted conversation history."""
        return [
            {
                "timestamp": msg.timestamp.isoformat(),
                "direction": msg.direction,
                "text": msg.text,
                "is_correction": msg.is_correction_request,
            }
            for msg in self.messages
        ]

    def to_dict(self) -> dict:
        return {
            "project_id": self.project_id,
            "project_code": self.project_code,
            "chat_id": self.chat_id,
            "username": self.username,
            "state": self.state.value,
            "message_count": len(self.messages),
            "pending_corrections": len([c for c in self.pending_corrections if not c["confirmed"]]),
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
        }


class PrimoTelegramBot:
    """
    Telegram bot for Primo to communicate with clients.

    Commands:
    /start - Start conversation, link to project
    /status - Get project status
    /correction - Request a correction (requires confirmation)
    /confirm - Confirm a pending correction
    /history - Get conversation history
    /help - Show available commands
    """

    def __init__(self, token: Optional[str] = None):
        """
        Initialize the Telegram bot.

        Args:
            token: BotFather token (or from TELEGRAM_BOT_TOKEN env var)
        """
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN", "")
        self._conversations: Dict[int, ProjectConversation] = {}  # chat_id -> conversation
        self._project_chats: Dict[str, int] = {}  # project_id -> chat_id
        self._handlers: Dict[str, Callable] = {}
        self._running = False

        # Register default handlers
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default command handlers."""
        self._handlers = {
            "start": self._handle_start,
            "status": self._handle_status,
            "correction": self._handle_correction,
            "confirm": self._handle_confirm,
            "history": self._handle_history,
            "help": self._handle_help,
        }

    async def _handle_start(self, chat_id: int, user_id: int, username: str, args: List[str]) -> str:
        """Handle /start command."""
        if not args:
            return """Hola! Soy Henry Primo, tu Project Manager.

Para vincular tu proyecto, usa:
/start CODIGO-PROYECTO

Ejemplo: /start GRIP-A1B2

Si no tenes el codigo, revisalo en el email de confirmacion o en el dashboard."""

        project_code = args[0].upper()

        # TODO: Validate project code against database
        # For now, accept any format XXXX-YYYY

        # Create conversation
        conversation = ProjectConversation(
            project_id=project_code.lower().replace("-", "_"),
            project_code=project_code,
            chat_id=chat_id,
            user_id=user_id,
            username=username,
        )

        self._conversations[chat_id] = conversation
        self._project_chats[conversation.project_id] = chat_id

        return f"""Proyecto {project_code} vinculado.

Ya podes:
- Preguntarme sobre el estado del proyecto
- Pedir aclaraciones
- Solicitar correcciones (con /correction)

Escribime lo que necesites."""

    async def _handle_status(self, chat_id: int, user_id: int, username: str, args: List[str]) -> str:
        """Handle /status command."""
        conversation = self._conversations.get(chat_id)
        if not conversation:
            return "Primero vinculate a un proyecto con /start CODIGO-PROYECTO"

        # TODO: Get real project status from database
        return f"""Estado de {conversation.project_code}:

Fase: Implementacion
Avance: 45%

El equipo de frontend esta con el dashboard.
Backend terminando las APIs.

Alguna duda especifica?"""

    async def _handle_correction(self, chat_id: int, user_id: int, username: str, args: List[str]) -> str:
        """Handle /correction command - request a project correction."""
        conversation = self._conversations.get(chat_id)
        if not conversation:
            return "Primero vinculate a un proyecto con /start CODIGO-PROYECTO"

        if not args:
            return """Para solicitar una correccion, describe que necesitas cambiar:

/correction [descripcion del cambio]

Ejemplo:
/correction El color del boton de login debe ser azul, no verde"""

        correction_text = " ".join(args)

        # Create correction request
        correction = conversation.request_correction_confirmation(correction_text)

        conversation.add_message(
            text=f"Correccion solicitada: {correction_text}",
            direction="incoming",
            is_correction=True,
        )

        return f"""Correccion registrada (ID: {correction['id']}):

"{correction_text}"

IMPORTANTE: Para que esta correccion se aplique, necesito tu CONFIRMACION explicita.

Responde con:
/confirm {correction['id']}

Esto es para asegurarme de que entendi bien lo que necesitas."""

    async def _handle_confirm(self, chat_id: int, user_id: int, username: str, args: List[str]) -> str:
        """Handle /confirm command - confirm a correction."""
        conversation = self._conversations.get(chat_id)
        if not conversation:
            return "Primero vinculate a un proyecto con /start CODIGO-PROYECTO"

        if not args:
            # Show pending corrections
            pending = [c for c in conversation.pending_corrections if not c["confirmed"]]
            if not pending:
                return "No hay correcciones pendientes de confirmar."

            pending_list = "\n".join([
                f"- {c['id']}: {c['text'][:50]}..."
                for c in pending
            ])
            return f"""Correcciones pendientes:

{pending_list}

Para confirmar: /confirm [ID]"""

        correction_id = args[0]
        if conversation.confirm_correction(correction_id):
            conversation.add_message(
                text=f"Correccion {correction_id} CONFIRMADA",
                direction="incoming",
            )
            return f"""CONFIRMACION RECIBIDA

Correccion {correction_id} confirmada y en cola para implementar.

El equipo va a trabajar en esto. Te aviso cuando este listo."""
        else:
            return f"No encontre la correccion {correction_id}. Usa /confirm sin parametros para ver las pendientes."

    async def _handle_history(self, chat_id: int, user_id: int, username: str, args: List[str]) -> str:
        """Handle /history command."""
        conversation = self._conversations.get(chat_id)
        if not conversation:
            return "Primero vinculate a un proyecto con /start CODIGO-PROYECTO"

        if not conversation.messages:
            return "No hay mensajes en el historial todavia."

        # Show last 10 messages
        recent = conversation.messages[-10:]
        history_text = "\n\n".join([
            f"[{msg.timestamp.strftime('%d/%m %H:%M')}] {'Tu' if msg.direction == 'incoming' else 'Primo'}: {msg.text[:100]}..."
            for msg in recent
        ])

        return f"""Ultimos mensajes:

{history_text}

Total mensajes: {len(conversation.messages)}"""

    async def _handle_help(self, chat_id: int, user_id: int, username: str, args: List[str]) -> str:
        """Handle /help command."""
        return """Comandos disponibles:

/start [CODIGO] - Vincular proyecto
/status - Ver estado del proyecto
/correction [texto] - Solicitar correccion
/confirm [ID] - Confirmar correccion
/history - Ver historial de mensajes
/help - Mostrar esta ayuda

Tambien podes escribirme directamente con cualquier pregunta sobre el proyecto."""

    async def process_message(
        self,
        chat_id: int,
        user_id: int,
        username: str,
        text: str,
    ) -> str:
        """
        Process an incoming message.

        Args:
            chat_id: Telegram chat ID
            user_id: Telegram user ID
            username: Username (if available)
            text: Message text

        Returns:
            Response text
        """
        # Check if it's a command
        if text.startswith("/"):
            parts = text[1:].split()
            command = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []

            handler = self._handlers.get(command)
            if handler:
                return await handler(chat_id, user_id, username, args)
            else:
                return f"Comando no reconocido: /{command}. Usa /help para ver los comandos disponibles."

        # Regular message - record in conversation
        conversation = self._conversations.get(chat_id)
        if not conversation:
            return """Hola! Para empezar, vincula tu proyecto:

/start CODIGO-PROYECTO

Si no tenes el codigo, revisalo en el email de confirmacion."""

        # Record message
        conversation.add_message(text=text, direction="incoming")

        # Check state
        if conversation.state == ConversationState.AWAITING_CORRECTION_CONFIRMATION:
            # Check if they're confirming with text
            if any(word in text.lower() for word in ["si", "confirmo", "correcto", "ok", "dale"]):
                pending = [c for c in conversation.pending_corrections if not c["confirmed"]]
                if pending:
                    conversation.confirm_correction(pending[0]["id"])
                    return "Perfecto, correccion confirmada. El equipo lo va a implementar."

            return """Tengo una correccion pendiente de confirmar.

Responde /confirm [ID] para confirmar, o escribe la correccion correcta si me equivoque."""

        # Generate contextual response
        # TODO: This would call the LLM with Primo's personality
        response = self._generate_response(conversation, text)

        # Record response
        conversation.add_message(text=response, direction="outgoing")

        return response

    def _generate_response(self, conversation: ProjectConversation, user_message: str) -> str:
        """
        Generate Primo's response to a user message.

        In production, this would call the LLM with Primo's prompt.
        """
        message_lower = user_message.lower()

        # Basic pattern matching (replace with LLM in production)
        if any(word in message_lower for word in ["avance", "progreso", "como va", "estado"]):
            return f"""El proyecto {conversation.project_code} va bien.

Estamos al 45% ahora. Frontend avanzando con el dashboard, backend con las APIs.

Algo especifico que quieras saber?"""

        elif any(word in message_lower for word in ["problema", "error", "bug", "falla"]):
            return """No tenemos problemas criticos reportados.

Si encontraste algo, contame y lo revisamos. Si es un cambio de requerimiento, usa /correction."""

        elif any(word in message_lower for word in ["cambiar", "modificar", "corregir"]):
            return """Si necesitas un cambio, usalo con el comando /correction:

/correction [descripcion del cambio]

Asi queda registrado y te pido confirmacion antes de implementarlo."""

        elif any(word in message_lower for word in ["gracias", "genial", "perfecto"]):
            return "Dale, cualquier cosa me decis."

        else:
            return """Entendido. Si necesitas:
- Ver estado: /status
- Pedir cambio: /correction
- Ver historial: /history

O escribime directamente con tu consulta."""

    def send_message(self, chat_id: int, text: str) -> bool:
        """
        Send a proactive message to a chat.

        Args:
            chat_id: Telegram chat ID
            text: Message text

        Returns:
            True if sent successfully
        """
        # TODO: Implement actual Telegram API call
        # This would use the telegram.Bot class from python-telegram-bot

        conversation = self._conversations.get(chat_id)
        if conversation:
            conversation.add_message(text=text, direction="outgoing")

        return True

    def send_to_project(self, project_id: str, text: str) -> bool:
        """
        Send message to the chat associated with a project.

        Args:
            project_id: Project identifier
            text: Message text

        Returns:
            True if sent successfully
        """
        chat_id = self._project_chats.get(project_id)
        if chat_id:
            return self.send_message(chat_id, text)
        return False

    def get_project_conversation(self, project_id: str) -> Optional[ProjectConversation]:
        """Get conversation for a project."""
        chat_id = self._project_chats.get(project_id)
        if chat_id:
            return self._conversations.get(chat_id)
        return None

    def get_all_conversations(self) -> List[dict]:
        """Get summary of all conversations."""
        return [conv.to_dict() for conv in self._conversations.values()]

    def export_conversation(self, project_id: str) -> Optional[dict]:
        """Export full conversation data for a project."""
        conversation = self.get_project_conversation(project_id)
        if not conversation:
            return None

        return {
            "project_id": conversation.project_id,
            "project_code": conversation.project_code,
            "messages": conversation.get_conversation_history(),
            "corrections": conversation.pending_corrections,
            "exported_at": datetime.utcnow().isoformat(),
        }


# Singleton instance
_telegram_bot: Optional[PrimoTelegramBot] = None


def get_telegram_bot() -> PrimoTelegramBot:
    """Get the singleton Telegram bot instance."""
    global _telegram_bot
    if _telegram_bot is None:
        _telegram_bot = PrimoTelegramBot()
    return _telegram_bot
