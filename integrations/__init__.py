"""
GriPro Integrations Package

External service integrations:
- Email (IMAP/SMTP) for project intake
- Telegram Bot for real-time client communication
- Specialized Bot Generator for custom agents
"""
from integrations.email_client import (
    PrimoEmailClient,
    get_email_client,
    ProjectRequest,
    ProjectIntakeWorkflow,
)
from integrations.telegram_bot import (
    PrimoTelegramBot,
    get_telegram_bot,
    ProjectConversation,
)

__all__ = [
    "PrimoEmailClient",
    "get_email_client",
    "ProjectRequest",
    "ProjectIntakeWorkflow",
    "PrimoTelegramBot",
    "get_telegram_bot",
    "ProjectConversation",
]
