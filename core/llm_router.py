"""
LLM Router Module
Routes tasks to appropriate LLM providers based on task type.

NOTE: This system uses PRO accounts (flat-rate subscriptions).
Actual LLM calls are delegated to locally installed PRO applications:
- Claude Desktop (Anthropic)
- Gemini Advanced (Google)
- ChatGPT PRO (OpenAI)
"""

import logging
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

from config import get_settings

logger = logging.getLogger(__name__)


class Provider(str, Enum):
    """Available LLM providers."""

    CLAUDE = "claude"
    GEMINI = "gemini"
    OPENAI = "openai"


class TaskType(str, Enum):
    """Supported task types for routing."""

    CODE_GENERATION = "code_generation"
    QA_TESTING = "qa_testing"
    CONTENT_WRITING = "content_writing"
    ANALYSIS = "analysis"
    SECURITY = "security"
    DEPLOYMENT = "deployment"
    GENERAL = "general"


@dataclass
class LLMResponse:
    """
    Response from an LLM provider.

    Attributes:
        content: The generated text response.
        provider: Which provider generated the response.
        task_type: The type of task that was requested.
        success: Whether the call was successful.
        error: Error message if the call failed.
    """

    content: str
    provider: Provider
    task_type: TaskType
    success: bool = True
    error: Optional[str] = None


@dataclass
class ProviderConfig:
    """
    Configuration for an LLM provider.

    Attributes:
        name: Provider identifier.
        app_name: Name of the local application.
        executable_names: Possible executable names to search for.
        strengths: Task types this provider excels at.
        priority: Default priority (lower = higher priority).
    """

    name: Provider
    app_name: str
    executable_names: list[str]
    strengths: list[TaskType]
    priority: int = 1


class BaseLLMAdapter(ABC):
    """Base adapter for LLM providers."""

    @abstractmethod
    def call(self, prompt: str, system: Optional[str] = None) -> str:
        """
        Send a prompt to the LLM.

        Args:
            prompt: The user prompt.
            system: Optional system prompt.

        Returns:
            The LLM response text.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is available."""
        pass


class LocalAppAdapter(BaseLLMAdapter):
    """
    Adapter for locally installed PRO applications.

    This adapter delegates actual LLM calls to the local PRO apps.
    The implementation depends on how the local apps expose their APIs.
    """

    def __init__(self, provider: Provider, config: ProviderConfig) -> None:
        self.provider = provider
        self.config = config
        self._available: Optional[bool] = None

    def call(self, prompt: str, system: Optional[str] = None) -> str:
        """
        Delegate call to local PRO application.

        Note:
            This is a placeholder. Actual implementation depends on
            how each PRO app exposes its functionality (CLI, local API, etc.)

        Args:
            prompt: The user prompt.
            system: Optional system prompt.

        Returns:
            The LLM response text.

        Raises:
            NotImplementedError: Until local app integration is configured.
        """
        logger.info(f"Delegating to {self.config.app_name} (PRO account)")

        # Placeholder for actual implementation
        # Each PRO app has different integration methods:
        # - Claude Desktop: May use local server or CLI
        # - Gemini: Browser automation or API
        # - ChatGPT: Browser automation or local server

        raise NotImplementedError(
            f"Local app integration for {self.config.app_name} not yet configured. "
            f"Implement the specific adapter for your PRO app setup."
        )

    def is_available(self) -> bool:
        """
        Check if the local PRO app is installed and accessible.

        Returns:
            True if the app appears to be installed.
        """
        if self._available is not None:
            return self._available

        # Check for executable in PATH
        for exe_name in self.config.executable_names:
            if shutil.which(exe_name):
                self._available = True
                logger.debug(f"{self.config.app_name} found: {exe_name}")
                return True

        # Check common installation paths (Windows)
        common_paths = [
            Path.home() / "AppData" / "Local" / "Programs",
            Path("C:/Program Files"),
            Path("C:/Program Files (x86)"),
        ]

        for base_path in common_paths:
            for exe_name in self.config.executable_names:
                if (base_path / self.config.app_name / exe_name).exists():
                    self._available = True
                    return True

        self._available = False
        return False


class LLMRouter:
    """
    Routes tasks to appropriate LLM providers based on task type.

    Uses locally installed PRO applications (Claude Desktop, Gemini Advanced,
    ChatGPT PRO) rather than API keys. Each task type is routed to the
    provider best suited for that type of work.

    Routing Table:
        - code_generation → Claude (best for code)
        - qa_testing → Gemini (good at analysis)
        - content_writing → Gemini (creative tasks)
        - analysis → Claude (deep reasoning)
        - security → Claude (precise analysis)
        - deployment → Gemini (procedural tasks)
        - general → Claude (default)

    Example:
        >>> router = LLMRouter()
        >>> provider = router.get_provider("code_generation")
        >>> print(provider)
        'claude'
        >>>
        >>> # Check available providers
        >>> status = router.validate_providers()
        >>> print(status)
        {'claude': True, 'gemini': True, 'openai': False}
    """

    # Default routing table: task_type → preferred provider
    DEFAULT_ROUTING: dict[TaskType, Provider] = {
        TaskType.CODE_GENERATION: Provider.CLAUDE,
        TaskType.QA_TESTING: Provider.GEMINI,
        TaskType.CONTENT_WRITING: Provider.GEMINI,
        TaskType.ANALYSIS: Provider.CLAUDE,
        TaskType.SECURITY: Provider.CLAUDE,
        TaskType.DEPLOYMENT: Provider.GEMINI,
        TaskType.GENERAL: Provider.CLAUDE,
    }

    # Fallback order when preferred provider is unavailable
    FALLBACK_ORDER: list[Provider] = [
        Provider.CLAUDE,
        Provider.GEMINI,
        Provider.OPENAI,
    ]

    # Provider configurations
    PROVIDER_CONFIGS: dict[Provider, ProviderConfig] = {
        Provider.CLAUDE: ProviderConfig(
            name=Provider.CLAUDE,
            app_name="Claude",
            executable_names=["claude.exe", "claude", "Claude.exe"],
            strengths=[
                TaskType.CODE_GENERATION,
                TaskType.ANALYSIS,
                TaskType.SECURITY,
            ],
            priority=1,
        ),
        Provider.GEMINI: ProviderConfig(
            name=Provider.GEMINI,
            app_name="Gemini",
            executable_names=["gemini.exe", "gemini", "Gemini.exe"],
            strengths=[
                TaskType.QA_TESTING,
                TaskType.CONTENT_WRITING,
                TaskType.DEPLOYMENT,
            ],
            priority=2,
        ),
        Provider.OPENAI: ProviderConfig(
            name=Provider.OPENAI,
            app_name="ChatGPT",
            executable_names=["chatgpt.exe", "chatgpt", "ChatGPT.exe"],
            strengths=[TaskType.GENERAL],
            priority=3,
        ),
    }

    def __init__(
        self,
        routing_table: Optional[dict[TaskType, Provider]] = None,
        fallback_order: Optional[list[Provider]] = None,
    ) -> None:
        """
        Initialize the LLM Router.

        Args:
            routing_table: Custom routing table. Uses DEFAULT_ROUTING if None.
            fallback_order: Custom fallback order. Uses FALLBACK_ORDER if None.

        Example:
            >>> # Use default routing
            >>> router = LLMRouter()
            >>>
            >>> # Custom routing
            >>> custom_routing = {TaskType.CODE_GENERATION: Provider.OPENAI}
            >>> router = LLMRouter(routing_table=custom_routing)
        """
        self.settings = get_settings()
        self.routing_table = routing_table or self.DEFAULT_ROUTING.copy()
        self.fallback_order = fallback_order or self.FALLBACK_ORDER.copy()

        # Initialize adapters
        self._adapters: dict[Provider, LocalAppAdapter] = {}
        for provider, config in self.PROVIDER_CONFIGS.items():
            self._adapters[provider] = LocalAppAdapter(provider, config)

        # Cache for provider availability
        self._availability_cache: Optional[dict[Provider, bool]] = None

        logger.info("LLMRouter initialized")
        logger.debug(f"Routing table: {self.routing_table}")

    def _normalize_task_type(self, task_type: str) -> TaskType:
        """
        Normalize task type string to TaskType enum.

        Args:
            task_type: Task type as string or TaskType.

        Returns:
            TaskType enum value.

        Raises:
            ValueError: If task type is not recognized.
        """
        if isinstance(task_type, TaskType):
            return task_type

        normalized = task_type.lower().strip().replace("-", "_").replace(" ", "_")

        try:
            return TaskType(normalized)
        except ValueError:
            logger.warning(f"Unknown task type '{task_type}', using GENERAL")
            return TaskType.GENERAL

    def get_provider(self, task_type: str) -> str:
        """
        Get the best provider for a given task type.

        Considers provider availability and uses fallback if the
        preferred provider is not available.

        Args:
            task_type: Type of task (e.g., "code_generation", "analysis").

        Returns:
            Provider name as string ("claude", "gemini", "openai").

        Example:
            >>> router = LLMRouter()
            >>> provider = router.get_provider("code_generation")
            >>> print(provider)
            'claude'
            >>>
            >>> provider = router.get_provider("content_writing")
            >>> print(provider)
            'gemini'
        """
        task = self._normalize_task_type(task_type)
        preferred = self.routing_table.get(task, Provider.CLAUDE)

        # Check if preferred provider is available
        if self._is_provider_available(preferred):
            logger.info(f"Task '{task.value}' → Provider '{preferred.value}'")
            return preferred.value

        # Find fallback
        fallback = self._find_fallback(preferred)
        if fallback:
            logger.warning(
                f"Provider '{preferred.value}' unavailable, "
                f"using fallback '{fallback.value}' for task '{task.value}'"
            )
            return fallback.value

        # No providers available
        logger.error("No LLM providers available")
        raise RuntimeError(
            "No LLM providers available. Please ensure at least one PRO app "
            "(Claude, Gemini, or ChatGPT) is installed and accessible."
        )

    def call_llm(
        self,
        task_type: str,
        prompt: str,
        system: Optional[str] = None,
    ) -> LLMResponse:
        """
        Call the appropriate LLM for a given task.

        Routes the request to the best available provider based on
        task type and provider availability.

        Args:
            task_type: Type of task (determines which provider to use).
            prompt: The user prompt to send.
            system: Optional system prompt for context.

        Returns:
            LLMResponse with the generated content.

        Example:
            >>> router = LLMRouter()
            >>> response = router.call_llm(
            ...     task_type="code_generation",
            ...     prompt="Write a Python function to calculate fibonacci",
            ...     system="You are a senior Python developer"
            ... )
            >>> print(response.content)
        """
        task = self._normalize_task_type(task_type)
        provider_name = self.get_provider(task_type)
        provider = Provider(provider_name)

        logger.info(f"Calling {provider.value} for task: {task.value}")
        logger.debug(f"Prompt length: {len(prompt)} chars")

        adapter = self._adapters[provider]

        try:
            content = adapter.call(prompt, system)
            return LLMResponse(
                content=content,
                provider=provider,
                task_type=task,
                success=True,
            )
        except NotImplementedError as e:
            logger.warning(f"Adapter not implemented: {e}")
            return LLMResponse(
                content="",
                provider=provider,
                task_type=task,
                success=False,
                error=str(e),
            )
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return LLMResponse(
                content="",
                provider=provider,
                task_type=task,
                success=False,
                error=str(e),
            )

    def validate_providers(self) -> dict[str, bool]:
        """
        Check which LLM providers are available.

        Scans for locally installed PRO applications and returns
        their availability status.

        Returns:
            Dictionary mapping provider names to availability status.

        Example:
            >>> router = LLMRouter()
            >>> status = router.validate_providers()
            >>> print(status)
            {'claude': True, 'gemini': True, 'openai': False}
            >>>
            >>> # Check specific provider
            >>> if status['claude']:
            ...     print("Claude is available")
        """
        # Invalidate cache
        self._availability_cache = None

        status: dict[str, bool] = {}
        for provider in Provider:
            available = self._is_provider_available(provider)
            status[provider.value] = available

        available_list = [k for k, v in status.items() if v]
        unavailable_list = [k for k, v in status.items() if not v]

        if available_list:
            logger.info(f"Available providers: {', '.join(available_list)}")
        if unavailable_list:
            logger.warning(f"Unavailable providers: {', '.join(unavailable_list)}")

        return status

    def _is_provider_available(self, provider: Provider) -> bool:
        """Check if a specific provider is available."""
        if self._availability_cache is None:
            self._availability_cache = {}
            for p in Provider:
                self._availability_cache[p] = self._adapters[p].is_available()

        return self._availability_cache.get(provider, False)

    def _find_fallback(self, excluded: Provider) -> Optional[Provider]:
        """Find the first available fallback provider."""
        for provider in self.fallback_order:
            if provider != excluded and self._is_provider_available(provider):
                return provider
        return None

    def get_routing_table(self) -> dict[str, str]:
        """
        Get the current routing table as string keys/values.

        Returns:
            Dictionary mapping task types to provider names.

        Example:
            >>> router = LLMRouter()
            >>> table = router.get_routing_table()
            >>> print(table)
            {'code_generation': 'claude', 'qa_testing': 'gemini', ...}
        """
        return {
            task.value: provider.value
            for task, provider in self.routing_table.items()
        }

    def set_route(self, task_type: str, provider: str) -> None:
        """
        Override routing for a specific task type.

        Args:
            task_type: Task type to configure.
            provider: Provider to use for this task type.

        Raises:
            ValueError: If task type or provider is invalid.

        Example:
            >>> router = LLMRouter()
            >>> router.set_route("code_generation", "openai")
            >>> print(router.get_provider("code_generation"))
            'openai'
        """
        task = self._normalize_task_type(task_type)

        try:
            prov = Provider(provider.lower())
        except ValueError:
            raise ValueError(
                f"Invalid provider '{provider}'. "
                f"Valid options: {[p.value for p in Provider]}"
            )

        self.routing_table[task] = prov
        logger.info(f"Route updated: {task.value} → {prov.value}")
