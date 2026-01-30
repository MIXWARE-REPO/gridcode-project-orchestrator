"""
Agent Registry Module
Manages registration and lookup of AI agents in the orchestration system.

Each agent has a unique name and an alias (nickname) for quick reference.
Agents can be looked up by either their full name or alias.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class AgentType(str, Enum):
    """Types of agents in the system."""

    PROJECT_MANAGER = "project_manager"
    FRONTEND = "frontend"
    BACKEND = "backend"
    SECURITY = "security"
    QA_TESTING = "qa_testing"
    DEVOPS = "devops"
    MARKETING = "marketing"
    SUPERVISOR = "supervisor"


@dataclass
class Agent:
    """
    Represents an AI agent in the orchestration system.

    Attributes:
        name: Full unique name of the agent (e.g., "primo").
        alias: Short nickname for quick reference (e.g., "Primo").
        agent_type: Type/role of the agent.
        prompt_file: Path to the agent's system prompt file.
        config: Additional configuration options.
        status: Whether the agent is active/available.
        dependencies: List of other agents this agent depends on.

    Example:
        >>> agent = Agent(
        ...     name="primo",
        ...     alias="Primo",
        ...     agent_type=AgentType.PROJECT_MANAGER,
        ...     prompt_file="prompts/primo.md"
        ... )
    """

    name: str
    alias: str
    agent_type: AgentType
    prompt_file: str
    config: dict = field(default_factory=dict)
    status: bool = True
    dependencies: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate agent after initialization."""
        if not self.name:
            raise ValueError("Agent name cannot be empty")
        if not self.alias:
            raise ValueError("Agent alias cannot be empty")


class AgentNotFoundError(Exception):
    """Raised when an agent cannot be found in the registry."""

    pass


class AgentAlreadyExistsError(Exception):
    """Raised when trying to register an agent that already exists."""

    pass


class AgentRegistry:
    """
    Registry for managing AI agents in the orchestration system.

    Provides methods to register, lookup, and manage agents.
    Agents can be found by their full name or alias (case-insensitive).

    Default Agents:
        - primo (Primo): Project Manager - coordinates all agents
        - fronti_frontend (Fronti): Frontend development
        - baky_backend (Baky): Backend development
        - secu_security (Secu): Security analysis
        - qai_testing (Qai): QA and testing
        - devi_devops (Devi): DevOps and deployment
        - mark_marketing (Mark): Marketing and documentation
        - guru_supervisor (Guru): Knowledge supervisor

    Example:
        >>> registry = AgentRegistry()
        >>>
        >>> # Get agent by name or alias (case-insensitive)
        >>> primo = registry.get_agent("primo")
        >>> primo = registry.get_agent("Primo")  # Same result
        >>>
        >>> # List all agents
        >>> agents = registry.list_agents()
        >>> print(agents)
        ['primo', 'fronti_frontend', 'baky_backend', ...]
    """

    # Default agent configurations
    DEFAULT_AGENTS: dict[str, dict] = {
        "primo": {
            "alias": "Primo",
            "agent_type": AgentType.PROJECT_MANAGER,
            "prompt_file": "prompts/primo.md",
            "config": {
                "role": "Project Manager",
                "description": "Coordinates all agents, manages tasks and priorities",
                "can_delegate": True,
                "max_concurrent_tasks": 5,
            },
            "dependencies": [],
        },
        "fronti_frontend": {
            "alias": "Fronti",
            "agent_type": AgentType.FRONTEND,
            "prompt_file": "prompts/fronti.md",
            "config": {
                "role": "Frontend Developer",
                "description": "React, Next.js, UI/UX implementation",
                "technologies": ["react", "nextjs", "typescript", "tailwind"],
            },
            "dependencies": ["primo"],
        },
        "baky_backend": {
            "alias": "Baky",
            "agent_type": AgentType.BACKEND,
            "prompt_file": "prompts/baky.md",
            "config": {
                "role": "Backend Developer",
                "description": "Python, FastAPI, databases, APIs",
                "technologies": ["python", "fastapi", "postgresql", "redis"],
            },
            "dependencies": ["primo"],
        },
        "secu_security": {
            "alias": "Secu",
            "agent_type": AgentType.SECURITY,
            "prompt_file": "prompts/secu.md",
            "config": {
                "role": "Security Specialist",
                "description": "Security audits, vulnerability analysis, compliance",
                "focus_areas": ["owasp", "authentication", "encryption"],
            },
            "dependencies": ["primo"],
        },
        "qai_testing": {
            "alias": "Qai",
            "agent_type": AgentType.QA_TESTING,
            "prompt_file": "prompts/qai.md",
            "config": {
                "role": "QA Engineer",
                "description": "Testing, quality assurance, test automation",
                "test_types": ["unit", "integration", "e2e", "performance"],
            },
            "dependencies": ["primo"],
        },
        "devi_devops": {
            "alias": "Devi",
            "agent_type": AgentType.DEVOPS,
            "prompt_file": "prompts/devi.md",
            "config": {
                "role": "DevOps Engineer",
                "description": "CI/CD, deployment, infrastructure, monitoring",
                "platforms": ["docker", "hetzner", "github_actions"],
            },
            "dependencies": ["primo"],
        },
        "mark_marketing": {
            "alias": "Mark",
            "agent_type": AgentType.MARKETING,
            "prompt_file": "prompts/mark.md",
            "config": {
                "role": "Marketing & Documentation",
                "description": "Documentation, content, user guides, marketing copy",
                "outputs": ["docs", "readme", "tutorials", "blog_posts"],
            },
            "dependencies": ["primo"],
        },
        "guru_supervisor": {
            "alias": "Guru",
            "agent_type": AgentType.SUPERVISOR,
            "prompt_file": "prompts/guru.md",
            "config": {
                "role": "Knowledge Supervisor",
                "description": "Oversees quality, provides guidance, reviews decisions",
                "capabilities": ["review", "guidance", "knowledge_base"],
            },
            "dependencies": [],
        },
    }

    def __init__(self, load_defaults: bool = True) -> None:
        """
        Initialize the Agent Registry.

        Args:
            load_defaults: If True, loads default agents on initialization.

        Example:
            >>> # Load with default agents
            >>> registry = AgentRegistry()
            >>>
            >>> # Start with empty registry
            >>> registry = AgentRegistry(load_defaults=False)
        """
        self._agents: dict[str, Agent] = {}
        self._alias_map: dict[str, str] = {}  # lowercase alias → name

        if load_defaults:
            self._load_default_agents()

        logger.info(f"AgentRegistry initialized with {len(self._agents)} agents")

    def _load_default_agents(self) -> None:
        """Load default agents into the registry."""
        for name, config in self.DEFAULT_AGENTS.items():
            agent = Agent(
                name=name,
                alias=config["alias"],
                agent_type=config["agent_type"],
                prompt_file=config["prompt_file"],
                config=config.get("config", {}),
                status=True,
                dependencies=config.get("dependencies", []),
            )
            self._agents[name] = agent
            self._alias_map[config["alias"].lower()] = name

        logger.debug(f"Loaded {len(self._agents)} default agents")

    def register_agent(
        self,
        name: str,
        agent_config: dict,
        overwrite: bool = False,
    ) -> None:
        """
        Register a new agent in the registry.

        Args:
            name: Unique name for the agent.
            agent_config: Configuration dictionary with agent details.
                Required keys: alias, agent_type, prompt_file
                Optional keys: config, status, dependencies
            overwrite: If True, allows overwriting existing agents.

        Raises:
            AgentAlreadyExistsError: If agent exists and overwrite is False.
            ValueError: If required config keys are missing.

        Example:
            >>> registry = AgentRegistry()
            >>> registry.register_agent("custom_agent", {
            ...     "alias": "Custom",
            ...     "agent_type": AgentType.BACKEND,
            ...     "prompt_file": "prompts/custom.md",
            ...     "config": {"role": "Custom Role"},
            ... })
        """
        name = name.lower().strip()

        # Check if exists
        if name in self._agents and not overwrite:
            raise AgentAlreadyExistsError(
                f"Agent '{name}' already exists. Use overwrite=True to replace."
            )

        # Validate required fields
        required_fields = ["alias", "agent_type", "prompt_file"]
        missing = [f for f in required_fields if f not in agent_config]
        if missing:
            raise ValueError(f"Missing required config fields: {missing}")

        # Handle agent_type
        agent_type = agent_config["agent_type"]
        if isinstance(agent_type, str):
            agent_type = AgentType(agent_type)

        # Create agent
        agent = Agent(
            name=name,
            alias=agent_config["alias"],
            agent_type=agent_type,
            prompt_file=agent_config["prompt_file"],
            config=agent_config.get("config", {}),
            status=agent_config.get("status", True),
            dependencies=agent_config.get("dependencies", []),
        )

        # Remove old alias if overwriting
        if name in self._agents:
            old_alias = self._agents[name].alias.lower()
            self._alias_map.pop(old_alias, None)

        # Register
        self._agents[name] = agent
        self._alias_map[agent.alias.lower()] = name

        logger.info(f"Registered agent: {name} (alias: {agent.alias})")

    def get_agent(self, name_or_alias: str) -> Agent:
        """
        Get an agent by name or alias (case-insensitive).

        Args:
            name_or_alias: Agent name (e.g., "primo") or alias (e.g., "Primo").

        Returns:
            The Agent object.

        Raises:
            AgentNotFoundError: If no agent matches the name or alias.

        Example:
            >>> registry = AgentRegistry()
            >>>
            >>> # All these return the same agent
            >>> agent = registry.get_agent("primo")
            >>> agent = registry.get_agent("PRIMO")
            >>> agent = registry.get_agent("Primo")
        """
        key = name_or_alias.lower().strip()

        # Try direct name lookup
        if key in self._agents:
            logger.debug(f"Found agent by name: {key}")
            return self._agents[key]

        # Try alias lookup
        if key in self._alias_map:
            name = self._alias_map[key]
            logger.debug(f"Found agent by alias: {key} → {name}")
            return self._agents[name]

        # Not found
        available = list(self._agents.keys())
        raise AgentNotFoundError(
            f"Agent '{name_or_alias}' not found. "
            f"Available agents: {available}"
        )

    def get_by_alias(self, alias: str) -> Agent:
        """
        Get an agent by its alias only.

        Args:
            alias: Agent alias (e.g., "Primo", "Fronti").

        Returns:
            The Agent object.

        Raises:
            AgentNotFoundError: If no agent has this alias.

        Example:
            >>> registry = AgentRegistry()
            >>> fronti = registry.get_by_alias("Fronti")
        """
        key = alias.lower().strip()

        if key not in self._alias_map:
            aliases = [a.alias for a in self._agents.values()]
            raise AgentNotFoundError(
                f"No agent with alias '{alias}'. "
                f"Available aliases: {aliases}"
            )

        name = self._alias_map[key]
        return self._agents[name]

    def list_agents(self) -> list[str]:
        """
        List all registered agent names.

        Returns:
            List of agent names (not aliases).

        Example:
            >>> registry = AgentRegistry()
            >>> names = registry.list_agents()
            >>> print(names)
            ['primo', 'fronti_frontend', 'baky_backend', ...]
        """
        return list(self._agents.keys())

    def list_aliases(self) -> list[str]:
        """
        List all agent aliases.

        Returns:
            List of agent aliases.

        Example:
            >>> registry = AgentRegistry()
            >>> aliases = registry.list_aliases()
            >>> print(aliases)
            ['Primo', 'Fronti', 'Baky', ...]
        """
        return [agent.alias for agent in self._agents.values()]

    def get_agents_by_type(self, agent_type: str | AgentType) -> list[Agent]:
        """
        Get all agents of a specific type.

        Args:
            agent_type: Type to filter by (string or AgentType enum).

        Returns:
            List of agents matching the type.

        Example:
            >>> registry = AgentRegistry()
            >>>
            >>> # Get all backend agents
            >>> backends = registry.get_agents_by_type("backend")
            >>> backends = registry.get_agents_by_type(AgentType.BACKEND)
        """
        if isinstance(agent_type, str):
            agent_type = AgentType(agent_type.lower())

        matching = [
            agent for agent in self._agents.values()
            if agent.agent_type == agent_type
        ]

        logger.debug(f"Found {len(matching)} agents of type {agent_type.value}")
        return matching

    def remove_agent(self, name: str) -> None:
        """
        Remove an agent from the registry.

        Args:
            name: Name of the agent to remove.

        Raises:
            AgentNotFoundError: If agent doesn't exist.

        Example:
            >>> registry = AgentRegistry()
            >>> registry.remove_agent("custom_agent")
        """
        key = name.lower().strip()

        if key not in self._agents:
            raise AgentNotFoundError(f"Agent '{name}' not found")

        agent = self._agents[key]
        alias_key = agent.alias.lower()

        del self._agents[key]
        self._alias_map.pop(alias_key, None)

        logger.info(f"Removed agent: {name}")

    def validate_all_agents(self) -> dict[str, bool]:
        """
        Validate all registered agents.

        Checks:
        - Prompt file exists
        - Dependencies are registered
        - Agent is marked as active

        Returns:
            Dictionary mapping agent names to validation status.

        Example:
            >>> registry = AgentRegistry()
            >>> status = registry.validate_all_agents()
            >>> print(status)
            {'primo': True, 'fronti_frontend': True, ...}
        """
        results: dict[str, bool] = {}

        for name, agent in self._agents.items():
            valid = True
            issues: list[str] = []

            # Check status
            if not agent.status:
                issues.append("agent is inactive")
                valid = False

            # Check prompt file exists
            prompt_path = Path(agent.prompt_file)
            if not prompt_path.exists():
                issues.append(f"prompt file not found: {agent.prompt_file}")
                # Don't fail validation for missing prompts (may be created later)

            # Check dependencies are registered
            for dep in agent.dependencies:
                if dep not in self._agents:
                    issues.append(f"missing dependency: {dep}")
                    valid = False

            results[name] = valid

            if issues:
                logger.warning(f"Agent '{name}' issues: {', '.join(issues)}")
            else:
                logger.debug(f"Agent '{name}' validated successfully")

        valid_count = sum(1 for v in results.values() if v)
        logger.info(f"Validation complete: {valid_count}/{len(results)} agents valid")

        return results

    def get_agent_info(self, name_or_alias: str) -> dict:
        """
        Get detailed information about an agent.

        Args:
            name_or_alias: Agent name or alias.

        Returns:
            Dictionary with full agent details.

        Example:
            >>> registry = AgentRegistry()
            >>> info = registry.get_agent_info("Primo")
            >>> print(info['role'])
            'Project Manager'
        """
        agent = self.get_agent(name_or_alias)

        return {
            "name": agent.name,
            "alias": agent.alias,
            "type": agent.agent_type.value,
            "prompt_file": agent.prompt_file,
            "status": agent.status,
            "dependencies": agent.dependencies,
            **agent.config,
        }

    def __len__(self) -> int:
        """Return number of registered agents."""
        return len(self._agents)

    def __contains__(self, name_or_alias: str) -> bool:
        """Check if an agent exists by name or alias."""
        key = name_or_alias.lower().strip()
        return key in self._agents or key in self._alias_map

    def __iter__(self):
        """Iterate over all agents."""
        return iter(self._agents.values())
