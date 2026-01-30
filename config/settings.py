"""
Settings Module
Centralized configuration management using Pydantic BaseSettings.

NOTE: This system uses PRO accounts (flat-rate subscriptions) for:
- Claude PRO (Anthropic)
- Gemini Advanced (Google)
- ChatGPT PRO (OpenAI)

No API keys are required. LLM interactions are delegated to locally
installed PRO desktop applications. This module only manages:
- PRO account enable/disable flags
- Database configuration (Supabase)
- Deployment settings (Hetzner)
- Environment configuration
"""

import logging
from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Uses Pydantic BaseSettings for automatic validation and type coercion.
    Variables are loaded from .env file and environment variables.

    Note:
        Claude/Gemini/ChatGPT PRO credentials are managed locally
        in their desktop applications, not through API keys.

    Attributes:
        environment: Current environment (development/production).
        debug: Enable debug mode.
        log_level: Logging level.
        hetzner_api_token: Hetzner Cloud API token (deployment only).
        hetzner_vps_id: Hetzner VPS instance ID (deployment only).
        local_session_path: Path for storing local session tokens.

    Example:
        >>> from config import get_settings
        >>> settings = get_settings()
        >>> if settings.is_production():
        ...     print("Running in production mode")
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─────────────────────────────────────────────────────────────────
    # Environment Configuration
    # ─────────────────────────────────────────────────────────────────
    environment: Literal["development", "production"] = Field(
        default="development",
        description="Application environment (development/production)",
    )

    debug: bool = Field(
        default=True,
        description="Enable debug mode",
    )

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )

    # ─────────────────────────────────────────────────────────────────
    # PRO Accounts Configuration (Flat-rate, no API keys)
    # ─────────────────────────────────────────────────────────────────
    anthropic_pro_enabled: bool = Field(
        default=True,
        description="Enable Claude PRO (Anthropic)",
    )

    google_pro_enabled: bool = Field(
        default=True,
        description="Enable Gemini Advanced (Google)",
    )

    openai_pro_enabled: bool = Field(
        default=True,
        description="Enable ChatGPT PRO (OpenAI)",
    )

    # ─────────────────────────────────────────────────────────────────
    # Supabase Database Configuration
    # ─────────────────────────────────────────────────────────────────
    supabase_url: Optional[str] = Field(
        default=None,
        description="Supabase project URL",
    )

    supabase_anon_key: Optional[str] = Field(
        default=None,
        description="Supabase anonymous key (public, not secret)",
    )

    # ─────────────────────────────────────────────────────────────────
    # Hetzner VPS Configuration (Deployment Only)
    # ─────────────────────────────────────────────────────────────────
    hetzner_api_token: Optional[str] = Field(
        default=None,
        description="Hetzner Cloud API token (required for deployment)",
    )

    hetzner_vps_id: Optional[str] = Field(
        default=None,
        description="Hetzner VPS instance ID (required for deployment)",
    )

    # ─────────────────────────────────────────────────────────────────
    # Primo Email Configuration (Dreamhost IMAP)
    # ─────────────────────────────────────────────────────────────────
    primo_email: str = Field(
        default="Henry.Primo@centual.eu",
        description="Primo's email address",
    )

    primo_email_password: Optional[str] = Field(
        default=None,
        description="Primo's email password",
    )

    primo_imap_host: str = Field(
        default="imap.dreamhost.com",
        description="IMAP server host",
    )

    primo_imap_port: int = Field(
        default=993,
        description="IMAP server port",
    )

    primo_smtp_host: str = Field(
        default="smtp.dreamhost.com",
        description="SMTP server host",
    )

    primo_smtp_port: int = Field(
        default=465,
        description="SMTP server port",
    )

    # ─────────────────────────────────────────────────────────────────
    # Telegram Bot Configuration
    # ─────────────────────────────────────────────────────────────────
    telegram_bot_token: Optional[str] = Field(
        default=None,
        description="Telegram Bot token from BotFather",
    )

    telegram_bot_username: str = Field(
        default="GriProPrimoBot",
        description="Telegram Bot username",
    )

    # ─────────────────────────────────────────────────────────────────
    # Local Session Storage
    # ─────────────────────────────────────────────────────────────────
    local_session_path: Path = Field(
        default=Path.home() / ".gridcode" / "sessions",
        description="Path for storing local session tokens",
    )

    local_cache_path: Path = Field(
        default=Path.home() / ".gridcode" / "cache",
        description="Path for local cache storage",
    )

    # ─────────────────────────────────────────────────────────────────
    # Validators
    # ─────────────────────────────────────────────────────────────────
    @field_validator("environment", mode="before")
    @classmethod
    def normalize_environment(cls, v: str) -> str:
        """Normalize environment value to lowercase."""
        if isinstance(v, str):
            normalized = v.lower().strip()
            if normalized in ("dev", "development"):
                return "development"
            if normalized in ("prod", "production"):
                return "production"
        return v

    @field_validator("log_level", mode="before")
    @classmethod
    def normalize_log_level(cls, v: str) -> str:
        """Normalize log level to uppercase."""
        if isinstance(v, str):
            return v.upper().strip()
        return v

    @model_validator(mode="after")
    def ensure_paths_exist(self) -> "Settings":
        """Create local storage directories if they don't exist."""
        self.local_session_path.mkdir(parents=True, exist_ok=True)
        self.local_cache_path.mkdir(parents=True, exist_ok=True)
        return self

    # ─────────────────────────────────────────────────────────────────
    # Methods
    # ─────────────────────────────────────────────────────────────────
    def is_production(self) -> bool:
        """
        Check if running in production environment.

        Returns:
            True if environment is 'production', False otherwise.

        Example:
            >>> settings = get_settings()
            >>> if settings.is_production():
            ...     # Use production configuration
            ...     pass
        """
        return self.environment == "production"

    def is_development(self) -> bool:
        """
        Check if running in development environment.

        Returns:
            True if environment is 'development', False otherwise.
        """
        return self.environment == "development"

    def get_log_level(self) -> int:
        """
        Get the logging level as a logging constant.

        Returns:
            Integer constant from logging module (e.g., logging.INFO).

        Example:
            >>> settings = get_settings()
            >>> logging.basicConfig(level=settings.get_log_level())
        """
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        return level_map[self.log_level]

    def validate_critical_vars(self, require_hetzner: bool = False) -> dict[str, bool]:
        """
        Validate that critical environment variables are set.

        Args:
            require_hetzner: If True, also validates Hetzner credentials
                            (required for deployment operations).

        Returns:
            Dictionary with variable names and their validation status.

        Raises:
            ValueError: If critical variables are missing when required.

        Example:
            >>> settings = get_settings()
            >>> # For local development
            >>> settings.validate_critical_vars()
            {'environment': True, 'log_level': True}
            >>>
            >>> # For deployment
            >>> settings.validate_critical_vars(require_hetzner=True)
        """
        status: dict[str, bool] = {
            "environment": bool(self.environment),
            "log_level": bool(self.log_level),
        }

        if require_hetzner:
            status["hetzner_api_token"] = bool(self.hetzner_api_token)
            status["hetzner_vps_id"] = bool(self.hetzner_vps_id)

            missing = [k for k, v in status.items() if not v]
            if missing:
                raise ValueError(
                    f"Missing critical variables for deployment: {', '.join(missing)}. "
                    f"Please set them in your .env file."
                )

        return status

    def has_hetzner_config(self) -> bool:
        """
        Check if Hetzner deployment credentials are configured.

        Returns:
            True if both HETZNER_API_TOKEN and HETZNER_VPS_ID are set.
        """
        return bool(self.hetzner_api_token and self.hetzner_vps_id)

    def has_supabase_config(self) -> bool:
        """
        Check if Supabase database is configured.

        Returns:
            True if both SUPABASE_URL and SUPABASE_ANON_KEY are set.
        """
        return bool(self.supabase_url and self.supabase_anon_key)

    def has_email_config(self) -> bool:
        """
        Check if Primo email is configured.

        Returns:
            True if PRIMO_EMAIL_PASSWORD is set.
        """
        return bool(self.primo_email_password)

    def has_telegram_config(self) -> bool:
        """
        Check if Telegram bot is configured.

        Returns:
            True if TELEGRAM_BOT_TOKEN is set.
        """
        return bool(self.telegram_bot_token)

    def get_enabled_providers(self) -> list[str]:
        """
        Get list of enabled PRO providers.

        Returns:
            List of enabled provider names.

        Example:
            >>> settings = get_settings()
            >>> providers = settings.get_enabled_providers()
            >>> print(providers)
            ['anthropic', 'google', 'openai']
        """
        providers = []
        if self.anthropic_pro_enabled:
            providers.append("anthropic")
        if self.google_pro_enabled:
            providers.append("google")
        if self.openai_pro_enabled:
            providers.append("openai")
        return providers

    def validate_pro_accounts(self) -> dict[str, bool]:
        """
        Get status of all PRO account configurations.

        Returns:
            Dictionary mapping provider names to enabled status.

        Example:
            >>> settings = get_settings()
            >>> status = settings.validate_pro_accounts()
            >>> print(status)
            {'anthropic': True, 'google': True, 'openai': False}
        """
        return {
            "anthropic": self.anthropic_pro_enabled,
            "google": self.google_pro_enabled,
            "openai": self.openai_pro_enabled,
        }


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings instance.

    Uses LRU cache to ensure settings are loaded only once.
    The settings are validated on first access.

    Returns:
        Validated Settings instance.

    Raises:
        pydantic.ValidationError: If validation fails.

    Example:
        >>> settings = get_settings()
        >>> print(settings.environment)
        'development'
        >>> print(settings.get_log_level())
        20  # logging.INFO
    """
    return Settings()
