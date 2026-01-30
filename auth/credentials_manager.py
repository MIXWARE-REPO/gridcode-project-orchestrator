"""
PRO Accounts Manager Module
Manages PRO account configurations for LLM providers.

NOTE: This system uses PRO accounts (flat-rate subscriptions) for:
- Claude PRO (Anthropic)
- Gemini Advanced (Google)
- ChatGPT PRO (OpenAI)

NO API keys are required - LLM interactions are delegated to
locally installed PRO applications.
"""

import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Provider(str, Enum):
    """Supported PRO account providers."""

    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OPENAI = "openai"


@dataclass
class AccountStatus:
    """
    Status of a PRO account configuration.

    Attributes:
        provider: Provider name (anthropic, google, openai).
        enabled: Whether the provider is enabled in config.
        configured: Whether the provider appears properly configured.
        app_name: Name of the local PRO application.
    """

    provider: str
    enabled: bool
    configured: bool
    app_name: str


class ProAccountsError(Exception):
    """Raised when PRO account configuration is invalid."""

    pass


class ProAccountsManager:
    """
    Manages PRO account configurations for LLM providers.

    This system uses flat-rate PRO subscriptions instead of API keys.
    LLM interactions are handled by locally installed desktop applications:
    - Claude Desktop (Anthropic PRO)
    - Gemini (Google Advanced)
    - ChatGPT Desktop (OpenAI PRO)

    The manager validates that PRO accounts are enabled and configured,
    but does NOT create API clients - that responsibility belongs to
    the LLMRouter which delegates to local applications.

    Example:
        >>> manager = ProAccountsManager()
        >>> manager.load_pro_accounts()
        >>>
        >>> # Check specific provider
        >>> status = manager.get_account_status("anthropic")
        >>> print(f"Claude PRO: {'enabled' if status.enabled else 'disabled'}")
        >>>
        >>> # Validate all accounts
        >>> all_valid = manager.validate_accounts()
        >>> print(f"All accounts configured: {all_valid}")
    """

    # Provider configurations
    PROVIDER_CONFIG = {
        Provider.ANTHROPIC: {
            "env_var": "ANTHROPIC_PRO_ENABLED",
            "app_name": "Claude Desktop",
            "description": "Claude PRO (Anthropic)",
        },
        Provider.GOOGLE: {
            "env_var": "GOOGLE_PRO_ENABLED",
            "app_name": "Gemini",
            "description": "Gemini Advanced (Google)",
        },
        Provider.OPENAI: {
            "env_var": "OPENAI_PRO_ENABLED",
            "app_name": "ChatGPT Desktop",
            "description": "ChatGPT PRO (OpenAI)",
        },
    }

    def __init__(self, env_path: Optional[str] = None) -> None:
        """
        Initialize the PRO Accounts Manager.

        Args:
            env_path: Optional path to .env file. If not provided,
                     searches in current directory and parent directories.
        """
        self._env_loaded = False
        self._account_status: dict[Provider, AccountStatus] = {}
        self._env_path = env_path

        logger.info("ProAccountsManager initialized")

    def load_pro_accounts(self) -> dict[str, bool]:
        """
        Load and validate PRO account configurations from environment.

        Reads the PRO_ENABLED flags from .env file and validates
        that at least one provider is enabled.

        Returns:
            Dictionary mapping provider names to their enabled status.

        Raises:
            ProAccountsError: If no PRO accounts are enabled.

        Example:
            >>> manager = ProAccountsManager()
            >>> accounts = manager.load_pro_accounts()
            >>> print(accounts)
            {'anthropic': True, 'google': True, 'openai': False}
        """
        # Load environment
        if self._env_path:
            loaded = load_dotenv(self._env_path)
        else:
            loaded = load_dotenv()

        if loaded:
            logger.info("Environment variables loaded from .env file")
        else:
            logger.warning("No .env file found. Using existing environment variables.")

        self._env_loaded = True

        # Check each provider
        enabled_status: dict[str, bool] = {}

        for provider, config in self.PROVIDER_CONFIG.items():
            env_var = config["env_var"]
            value = os.getenv(env_var, "false").lower().strip()
            is_enabled = value in ("true", "1", "yes", "on")

            enabled_status[provider.value] = is_enabled

            # Create status object
            self._account_status[provider] = AccountStatus(
                provider=provider.value,
                enabled=is_enabled,
                configured=is_enabled,  # For PRO, enabled = configured
                app_name=config["app_name"],
            )

            if is_enabled:
                logger.info(f"PRO account enabled: {config['description']}")
            else:
                logger.debug(f"PRO account disabled: {config['description']}")

        # Validate at least one is enabled
        enabled_count = sum(1 for v in enabled_status.values() if v)
        if enabled_count == 0:
            logger.warning("No PRO accounts enabled. Enable at least one provider.")

        logger.info(f"Loaded {enabled_count} PRO account(s)")
        return enabled_status

    def get_account_status(self, provider: str) -> AccountStatus:
        """
        Get the status of a specific PRO account.

        Args:
            provider: Provider name ("anthropic", "google", "openai").

        Returns:
            AccountStatus with provider details.

        Raises:
            ProAccountsError: If provider is invalid or accounts not loaded.

        Example:
            >>> manager = ProAccountsManager()
            >>> manager.load_pro_accounts()
            >>> status = manager.get_account_status("anthropic")
            >>> print(f"Provider: {status.provider}")
            >>> print(f"Enabled: {status.enabled}")
            >>> print(f"App: {status.app_name}")
        """
        if not self._env_loaded:
            raise ProAccountsError(
                "Accounts not loaded. Call load_pro_accounts() first."
            )

        # Normalize provider name
        try:
            provider_enum = Provider(provider.lower().strip())
        except ValueError:
            valid = [p.value for p in Provider]
            raise ProAccountsError(
                f"Invalid provider '{provider}'. Valid options: {valid}"
            )

        return self._account_status[provider_enum]

    def validate_accounts(self, require_all: bool = False) -> bool:
        """
        Validate that PRO accounts are properly configured.

        Args:
            require_all: If True, requires ALL providers to be enabled.
                        If False (default), requires at least ONE.

        Returns:
            True if validation passes, False otherwise.

        Raises:
            ProAccountsError: If accounts not loaded.

        Example:
            >>> manager = ProAccountsManager()
            >>> manager.load_pro_accounts()
            >>>
            >>> # At least one account enabled
            >>> is_valid = manager.validate_accounts()
            >>>
            >>> # All accounts must be enabled
            >>> all_valid = manager.validate_accounts(require_all=True)
        """
        if not self._env_loaded:
            raise ProAccountsError(
                "Accounts not loaded. Call load_pro_accounts() first."
            )

        enabled_count = sum(
            1 for status in self._account_status.values() if status.enabled
        )
        total_count = len(self._account_status)

        if require_all:
            is_valid = enabled_count == total_count
            if not is_valid:
                disabled = [
                    s.provider for s in self._account_status.values() if not s.enabled
                ]
                logger.warning(f"Missing PRO accounts: {disabled}")
        else:
            is_valid = enabled_count > 0
            if not is_valid:
                logger.error("No PRO accounts enabled")

        return is_valid

    def get_enabled_providers(self) -> list[str]:
        """
        Get list of enabled PRO providers.

        Returns:
            List of enabled provider names.

        Example:
            >>> manager = ProAccountsManager()
            >>> manager.load_pro_accounts()
            >>> providers = manager.get_enabled_providers()
            >>> print(providers)
            ['anthropic', 'google']
        """
        if not self._env_loaded:
            return []

        return [
            status.provider
            for status in self._account_status.values()
            if status.enabled
        ]

    def get_all_status(self) -> dict[str, AccountStatus]:
        """
        Get status of all PRO accounts.

        Returns:
            Dictionary mapping provider names to AccountStatus objects.

        Example:
            >>> manager = ProAccountsManager()
            >>> manager.load_pro_accounts()
            >>> all_status = manager.get_all_status()
            >>> for name, status in all_status.items():
            ...     print(f"{name}: {'✓' if status.enabled else '✗'}")
        """
        if not self._env_loaded:
            return {}

        return {
            status.provider: status for status in self._account_status.values()
        }

    def is_provider_enabled(self, provider: str) -> bool:
        """
        Quick check if a provider is enabled.

        Args:
            provider: Provider name.

        Returns:
            True if enabled, False otherwise.

        Example:
            >>> if manager.is_provider_enabled("anthropic"):
            ...     print("Claude PRO is available")
        """
        try:
            status = self.get_account_status(provider)
            return status.enabled
        except ProAccountsError:
            return False
