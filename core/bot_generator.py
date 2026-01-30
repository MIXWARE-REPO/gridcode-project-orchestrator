"""
Specialized Bot Generator - GriPro

Allows Primo to create custom specialized bots for specific domains:
- Language translators
- OCPP (Electric Vehicle charging protocol)
- Rust specialists
- E-commerce integrations
- API integrators
- And more...

Each bot is:
1. Created in a separate repository (prompts/specialists/)
2. Documented with its specialty and orbit
3. Assigned to a department
4. Triggers Guru review every 15 days
"""
from __future__ import annotations

import os
import yaml
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional
from uuid import uuid4


class BotSpecialty(Enum):
    """Predefined bot specialty categories."""
    TRANSLATOR = "translator"           # Language translation
    PROTOCOL = "protocol"               # Protocols (OCPP, MQTT, etc.)
    LANGUAGE = "language"               # Programming language specific
    ECOMMERCE = "ecommerce"             # E-commerce platforms
    API_INTEGRATOR = "api_integrator"   # External API integrations
    DATABASE = "database"               # Database specialists
    SECURITY = "security"               # Security specialists
    INFRASTRUCTURE = "infrastructure"   # Cloud/DevOps
    CUSTOM = "custom"                   # Custom specialty


@dataclass
class BotLibrary:
    """Library or framework the bot should use."""
    name: str
    version: Optional[str] = None
    documentation_url: Optional[str] = None
    notes: str = ""


@dataclass
class SpecializedBot:
    """Definition of a specialized bot."""
    id: str
    name: str
    alias: str
    specialty: BotSpecialty
    department: str  # Parent department (fronti_frontend, baky_backend, etc.)

    # Description and scope
    description: str
    orbit: str  # Scope of competency
    responsibilities: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)

    # Technical requirements
    libraries: List[BotLibrary] = field(default_factory=list)
    required_skills: List[str] = field(default_factory=list)
    documentation_sources: List[str] = field(default_factory=list)

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = "primo"
    last_guru_review: Optional[datetime] = None
    next_guru_review: Optional[datetime] = None
    is_active: bool = True

    def __post_init__(self):
        """Set next Guru review date."""
        if self.next_guru_review is None:
            self.next_guru_review = datetime.utcnow() + timedelta(days=15)

    def needs_guru_review(self) -> bool:
        """Check if bot needs Guru review."""
        if self.next_guru_review is None:
            return True
        return datetime.utcnow() >= self.next_guru_review

    def record_guru_review(self):
        """Record that Guru reviewed this bot."""
        self.last_guru_review = datetime.utcnow()
        self.next_guru_review = datetime.utcnow() + timedelta(days=15)

    def to_prompt(self) -> str:
        """Generate the prompt file content for this bot."""
        libs_text = "\n".join([
            f"- **{lib.name}**{f' v{lib.version}' if lib.version else ''}: {lib.notes}"
            for lib in self.libraries
        ])

        docs_text = "\n".join([f"- {doc}" for doc in self.documentation_sources])

        responsibilities_text = "\n".join([f"- {r}" for r in self.responsibilities])

        limitations_text = "\n".join([f"- {l}" for l in self.limitations])

        prompt = f"""# {self.name} - Specialized Bot

## Identity

**ID:** {self.id}
**Alias:** {self.alias}
**Department:** {self.department}
**Specialty:** {self.specialty.value}
**Created:** {self.created_at.strftime('%Y-%m-%d')}

## Description

{self.description}

## Orbit of Competency

{self.orbit}

## Responsibilities

{responsibilities_text}

## Limitations

{limitations_text}

## Required Libraries and Frameworks

{libs_text}

## Documentation Sources

{docs_text}

## Communication Style

- Be precise and technical
- Reference documentation when explaining decisions
- Admit uncertainty - escalate to senior specialists when needed
- Follow department conventions and coding standards

## Quality Standards

This bot is subject to Guru review every 15 days.
Last review: {self.last_guru_review.strftime('%Y-%m-%d') if self.last_guru_review else 'Pending'}
Next review: {self.next_guru_review.strftime('%Y-%m-%d') if self.next_guru_review else 'Pending'}

## Integration

Reports to: {self.department}
Escalates to: Guru (for best practices and trends)
Coordinates with: Primo (for project requirements)
"""
        return prompt

    def to_yaml(self) -> str:
        """Generate YAML configuration for this bot."""
        config = {
            "bot": {
                "id": self.id,
                "name": self.name,
                "alias": self.alias,
                "specialty": self.specialty.value,
                "department": self.department,
                "description": self.description,
                "orbit": self.orbit,
                "responsibilities": self.responsibilities,
                "limitations": self.limitations,
                "libraries": [
                    {
                        "name": lib.name,
                        "version": lib.version,
                        "documentation_url": lib.documentation_url,
                        "notes": lib.notes,
                    }
                    for lib in self.libraries
                ],
                "required_skills": self.required_skills,
                "documentation_sources": self.documentation_sources,
                "metadata": {
                    "created_at": self.created_at.isoformat(),
                    "created_by": self.created_by,
                    "last_guru_review": self.last_guru_review.isoformat() if self.last_guru_review else None,
                    "next_guru_review": self.next_guru_review.isoformat() if self.next_guru_review else None,
                    "is_active": self.is_active,
                },
            }
        }
        return yaml.dump(config, default_flow_style=False, allow_unicode=True)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "alias": self.alias,
            "specialty": self.specialty.value,
            "department": self.department,
            "description": self.description,
            "orbit": self.orbit,
            "is_active": self.is_active,
            "needs_guru_review": self.needs_guru_review(),
            "created_at": self.created_at.isoformat(),
        }


class BotGenerator:
    """
    Generator for specialized bots.

    Usage by Primo:
    1. Define bot specialty and requirements
    2. Generate bot prompt and configuration
    3. Register bot in the system
    4. Trigger Guru for initial review
    """

    def __init__(self, prompts_dir: str = "prompts/specialists"):
        self.prompts_dir = prompts_dir
        self._bots: Dict[str, SpecializedBot] = {}
        self._guru_queue: List[str] = []  # Bot IDs pending Guru review

    def create_bot(
        self,
        name: str,
        alias: str,
        specialty: BotSpecialty,
        department: str,
        description: str,
        orbit: str,
        responsibilities: List[str],
        limitations: List[str],
        libraries: Optional[List[dict]] = None,
        required_skills: Optional[List[str]] = None,
        documentation_sources: Optional[List[str]] = None,
    ) -> SpecializedBot:
        """
        Create a new specialized bot.

        Args:
            name: Full name (e.g., "OCPP Protocol Specialist")
            alias: Short alias (e.g., "OCPP")
            specialty: Type of specialty
            department: Parent department ID
            description: What the bot does
            orbit: Scope of competency
            responsibilities: List of responsibilities
            limitations: List of limitations
            libraries: Libraries to use
            required_skills: Skills required
            documentation_sources: Documentation URLs

        Returns:
            Created SpecializedBot
        """
        bot_id = f"bot_{alias.lower()}_{uuid4().hex[:4]}"

        # Parse libraries
        bot_libraries = []
        if libraries:
            for lib in libraries:
                bot_libraries.append(BotLibrary(
                    name=lib.get("name", ""),
                    version=lib.get("version"),
                    documentation_url=lib.get("documentation_url"),
                    notes=lib.get("notes", ""),
                ))

        bot = SpecializedBot(
            id=bot_id,
            name=name,
            alias=alias,
            specialty=specialty,
            department=department,
            description=description,
            orbit=orbit,
            responsibilities=responsibilities,
            limitations=limitations,
            libraries=bot_libraries,
            required_skills=required_skills or [],
            documentation_sources=documentation_sources or [],
        )

        self._bots[bot_id] = bot
        self._guru_queue.append(bot_id)

        return bot

    def save_bot(self, bot: SpecializedBot) -> dict:
        """
        Save bot to filesystem.

        Creates:
        - prompts/specialists/{alias}.md - The prompt
        - prompts/specialists/{alias}.yaml - Configuration

        Returns:
            Dict with file paths
        """
        # Ensure directory exists
        os.makedirs(self.prompts_dir, exist_ok=True)

        alias_lower = bot.alias.lower().replace(" ", "_")

        # Save prompt
        prompt_path = os.path.join(self.prompts_dir, f"{alias_lower}.md")
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(bot.to_prompt())

        # Save config
        config_path = os.path.join(self.prompts_dir, f"{alias_lower}.yaml")
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(bot.to_yaml())

        return {
            "prompt_path": prompt_path,
            "config_path": config_path,
            "bot_id": bot.id,
        }

    def get_bot(self, bot_id: str) -> Optional[SpecializedBot]:
        """Get a bot by ID."""
        return self._bots.get(bot_id)

    def get_bots_by_department(self, department: str) -> List[SpecializedBot]:
        """Get all bots in a department."""
        return [
            bot for bot in self._bots.values()
            if bot.department == department and bot.is_active
        ]

    def get_bots_needing_review(self) -> List[SpecializedBot]:
        """Get all bots that need Guru review."""
        return [
            bot for bot in self._bots.values()
            if bot.needs_guru_review() and bot.is_active
        ]

    def get_guru_queue(self) -> List[SpecializedBot]:
        """Get bots in the Guru review queue."""
        return [
            self._bots[bot_id]
            for bot_id in self._guru_queue
            if bot_id in self._bots
        ]

    def complete_guru_review(self, bot_id: str, approved: bool = True) -> bool:
        """
        Record completion of Guru review.

        Args:
            bot_id: Bot that was reviewed
            approved: Whether the review passed

        Returns:
            True if successful
        """
        bot = self._bots.get(bot_id)
        if not bot:
            return False

        bot.record_guru_review()

        if bot_id in self._guru_queue:
            self._guru_queue.remove(bot_id)

        if not approved:
            bot.is_active = False

        return True

    def deactivate_bot(self, bot_id: str) -> bool:
        """Deactivate a bot."""
        bot = self._bots.get(bot_id)
        if bot:
            bot.is_active = False
            return True
        return False

    def list_all_bots(self) -> List[dict]:
        """List all bots."""
        return [bot.to_dict() for bot in self._bots.values()]


# Pre-defined bot templates
BOT_TEMPLATES = {
    "ocpp": {
        "name": "OCPP Protocol Specialist",
        "alias": "OCPP",
        "specialty": BotSpecialty.PROTOCOL,
        "department": "baky_backend",
        "description": "Specialist in Open Charge Point Protocol for EV charging stations. Handles OCPP 1.6 and OCPP 2.0.1 implementations.",
        "orbit": "Electric vehicle charging infrastructure, charge point management, OCPP server/client implementation, charging session management.",
        "responsibilities": [
            "Implement OCPP server (Central System)",
            "Implement OCPP client (Charge Point)",
            "Handle OCPP message flows (Boot, Heartbeat, Authorize, StartTransaction, etc.)",
            "WebSocket connection management",
            "OCPP security profiles",
        ],
        "limitations": [
            "Does not handle hardware integration directly",
            "Payment processing escalates to e-commerce specialist",
            "Complex load balancing escalates to infrastructure",
        ],
        "libraries": [
            {"name": "ocpp", "version": "0.20.0", "documentation_url": "https://github.com/mobilityhouse/ocpp", "notes": "Python OCPP library"},
            {"name": "websockets", "version": "12.0", "documentation_url": "https://websockets.readthedocs.io/", "notes": "WebSocket implementation"},
        ],
        "documentation_sources": [
            "https://www.openchargealliance.org/protocols/ocpp-16/",
            "https://www.openchargealliance.org/protocols/ocpp-201/",
        ],
    },
    "rust": {
        "name": "Rust Language Specialist",
        "alias": "Rustacean",
        "specialty": BotSpecialty.LANGUAGE,
        "department": "baky_backend",
        "description": "Specialist in Rust programming language for high-performance, memory-safe systems.",
        "orbit": "Rust language features, memory safety, concurrency, systems programming, WebAssembly compilation.",
        "responsibilities": [
            "Write idiomatic Rust code",
            "Implement memory-safe algorithms",
            "Handle async/await patterns",
            "Cargo package management",
            "FFI with C/C++",
        ],
        "limitations": [
            "UI/frontend escalates to frontend team",
            "Database schemas escalate to DB engineer",
        ],
        "libraries": [
            {"name": "tokio", "version": "1.x", "documentation_url": "https://tokio.rs/", "notes": "Async runtime"},
            {"name": "serde", "version": "1.x", "documentation_url": "https://serde.rs/", "notes": "Serialization"},
            {"name": "actix-web", "version": "4.x", "documentation_url": "https://actix.rs/", "notes": "Web framework"},
        ],
        "documentation_sources": [
            "https://doc.rust-lang.org/book/",
            "https://doc.rust-lang.org/std/",
        ],
    },
    "shopify": {
        "name": "Shopify Integration Specialist",
        "alias": "Shopify",
        "specialty": BotSpecialty.ECOMMERCE,
        "department": "baky_backend",
        "description": "Specialist in Shopify platform integrations, apps, and storefront customization.",
        "orbit": "Shopify Admin API, Storefront API, Shopify apps, webhooks, Liquid templating, checkout customization.",
        "responsibilities": [
            "Shopify Admin API integrations",
            "Storefront API for headless commerce",
            "Custom Shopify apps",
            "Webhook handling",
            "Liquid template customization",
        ],
        "limitations": [
            "UI design escalates to frontend/UX",
            "Payment gateway setup escalates to e-commerce lead",
        ],
        "libraries": [
            {"name": "@shopify/shopify-api", "documentation_url": "https://shopify.dev/docs/api/admin", "notes": "Official Shopify API client"},
            {"name": "@shopify/hydrogen", "documentation_url": "https://hydrogen.shopify.dev/", "notes": "Headless commerce framework"},
        ],
        "documentation_sources": [
            "https://shopify.dev/docs",
            "https://shopify.dev/docs/api/admin-graphql",
        ],
    },
    "translator_es_en": {
        "name": "Spanish-English Translator",
        "alias": "Traductor",
        "specialty": BotSpecialty.TRANSLATOR,
        "department": "mark_documentation",
        "description": "Specialist in Spanish-English translation for technical documentation and UI content.",
        "orbit": "Technical translation, localization, i18n implementation, content adaptation for Spanish and English markets.",
        "responsibilities": [
            "Translate technical documentation",
            "Localize UI strings",
            "Adapt content for regional variations",
            "Maintain translation memory",
            "Implement i18n frameworks",
        ],
        "limitations": [
            "Legal/compliance text requires human review",
            "Marketing copy requires approval",
        ],
        "libraries": [
            {"name": "i18next", "documentation_url": "https://www.i18next.com/", "notes": "Internationalization framework"},
            {"name": "react-intl", "documentation_url": "https://formatjs.io/docs/react-intl/", "notes": "React i18n"},
        ],
        "documentation_sources": [
            "https://www.i18next.com/",
            "https://developer.mozilla.org/en-US/docs/Mozilla/Localization",
        ],
    },
}


def create_bot_from_template(template_name: str, generator: BotGenerator) -> Optional[SpecializedBot]:
    """Create a bot from a predefined template."""
    template = BOT_TEMPLATES.get(template_name)
    if not template:
        return None

    return generator.create_bot(
        name=template["name"],
        alias=template["alias"],
        specialty=template["specialty"],
        department=template["department"],
        description=template["description"],
        orbit=template["orbit"],
        responsibilities=template["responsibilities"],
        limitations=template["limitations"],
        libraries=template.get("libraries"),
        required_skills=template.get("required_skills"),
        documentation_sources=template.get("documentation_sources"),
    )


# Singleton instance
_bot_generator: Optional[BotGenerator] = None


def get_bot_generator() -> BotGenerator:
    """Get the singleton bot generator instance."""
    global _bot_generator
    if _bot_generator is None:
        _bot_generator = BotGenerator()
    return _bot_generator
