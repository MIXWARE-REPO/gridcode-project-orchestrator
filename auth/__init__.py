"""
Authentication Module
Manage PRO account configurations for LLM providers.

NOTE: This system uses PRO accounts (flat-rate subscriptions).
No API keys required - LLM calls are delegated to local PRO apps.
"""

from auth.credentials_manager import (
    AccountStatus,
    ProAccountsError,
    ProAccountsManager,
    Provider,
)

__all__ = [
    "ProAccountsManager",
    "ProAccountsError",
    "AccountStatus",
    "Provider",
]
