"""
GriPro Orchestrator Module
Main orchestration engine that integrates all system components.

This is the CORE module that connects:
- AgentRegistry: Agent management and lookup
- LLMRouter: LLM provider selection and routing
- SupabaseManager: State persistence and data storage
- ProAccountsManager: PRO account validation

All task execution, workflow management, and agent communication
flows through this orchestrator.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from auth import ProAccountsManager, ProAccountsError
from config import get_settings
from core.agent_registry import Agent, AgentRegistry, AgentType, AgentNotFoundError
from core.llm_router import LLMRouter, LLMResponse, TaskType, Provider
from database import SupabaseManager, DatabaseError, NotFoundError

logger = logging.getLogger(__name__)


class WorkflowType(str, Enum):
    """Types of automated workflows."""

    FULL = "full"
    PLANNING = "planning"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    DOCUMENTATION = "documentation"


class TaskStatus(str, Enum):
    """Status of a task execution."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskResult:
    """
    Result of a task execution.

    Attributes:
        status: Execution status.
        result: Output content from the task.
        agent: Agent that executed the task.
        provider: LLM provider used.
        timestamp: When the task completed.
        error: Error message if failed.
        metadata: Additional task metadata.
    """

    status: TaskStatus
    result: str
    agent: str
    provider: str
    timestamp: str
    error: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowState:
    """
    State of a workflow execution.

    Attributes:
        workflow_type: Type of workflow being executed.
        current_phase: Current phase in the workflow.
        completed_phases: List of completed phases.
        progress: Overall progress percentage.
        agents_involved: Agents participating in the workflow.
    """

    workflow_type: WorkflowType
    current_phase: str
    completed_phases: list[str] = field(default_factory=list)
    progress: int = 0
    agents_involved: list[str] = field(default_factory=list)


class OrchestratorError(Exception):
    """Base exception for orchestrator operations."""

    pass


class WorkflowError(OrchestratorError):
    """Raised when a workflow execution fails."""

    pass


class GriProOrchestrator:
    """
    Main orchestration engine for the GriPro system.

    Integrates all system components to provide unified task execution,
    workflow management, and agent communication capabilities.

    Components:
        - AgentRegistry: Manages agent definitions and lookup
        - LLMRouter: Routes tasks to appropriate LLM providers
        - SupabaseManager: Persists state and data to database
        - ProAccountsManager: Validates PRO account configurations

    Example:
        >>> async def main():
        ...     orchestrator = GriProOrchestrator()
        ...     await orchestrator.initialize()
        ...
        ...     # Execute a task
        ...     result = await orchestrator.execute_task(
        ...         project_id="proj_001",
        ...         agent_name="primo",
        ...         task_description="Create project plan"
        ...     )
        ...
        ...     # Run full workflow
        ...     await orchestrator.run_workflow(
        ...         project_id="proj_001",
        ...         workflow_type="full"
        ...     )
    """

    # Mapping from AgentType to TaskType for routing
    AGENT_TASK_MAP: dict[AgentType, TaskType] = {
        AgentType.PROJECT_MANAGER: TaskType.ANALYSIS,
        AgentType.FRONTEND: TaskType.CODE_GENERATION,
        AgentType.BACKEND: TaskType.CODE_GENERATION,
        AgentType.SECURITY: TaskType.SECURITY,
        AgentType.QA_TESTING: TaskType.QA_TESTING,
        AgentType.DEVOPS: TaskType.DEPLOYMENT,
        AgentType.MARKETING: TaskType.CONTENT_WRITING,
        AgentType.SUPERVISOR: TaskType.ANALYSIS,
    }

    # Workflow phase definitions
    WORKFLOW_PHASES: dict[WorkflowType, list[tuple[str, str]]] = {
        WorkflowType.FULL: [
            ("planning", "primo"),
            ("frontend", "fronti_frontend"),
            ("backend", "baky_backend"),
            ("testing", "qai_testing"),
            ("security", "secu_security"),
            ("deployment", "devi_devops"),
            ("documentation", "mark_marketing"),
            ("review", "guru_supervisor"),
        ],
        WorkflowType.PLANNING: [
            ("planning", "primo"),
            ("review", "guru_supervisor"),
        ],
        WorkflowType.DEVELOPMENT: [
            ("frontend", "fronti_frontend"),
            ("backend", "baky_backend"),
            ("testing", "qai_testing"),
        ],
        WorkflowType.TESTING: [
            ("testing", "qai_testing"),
            ("security", "secu_security"),
        ],
        WorkflowType.DEPLOYMENT: [
            ("deployment", "devi_devops"),
        ],
        WorkflowType.DOCUMENTATION: [
            ("documentation", "mark_marketing"),
        ],
    }

    def __init__(self) -> None:
        """
        Initialize the GriPro Orchestrator.

        Creates instances of all component managers but does NOT
        establish connections. Call initialize() to fully set up.
        """
        self.settings = get_settings()

        # Component managers (lazy initialization)
        self._agent_registry: Optional[AgentRegistry] = None
        self._llm_router: Optional[LLMRouter] = None
        self._supabase: Optional[SupabaseManager] = None
        self._pro_accounts: Optional[ProAccountsManager] = None

        # State
        self._initialized = False
        self._active_workflows: dict[str, WorkflowState] = {}

        logger.info("GriProOrchestrator created (not yet initialized)")

    async def initialize(self) -> None:
        """
        Initialize all orchestrator components.

        Sets up:
        - AgentRegistry with default agents
        - LLMRouter with routing table
        - SupabaseManager connection
        - ProAccountsManager validation

        Raises:
            OrchestratorError: If initialization fails.

        Example:
            >>> orchestrator = GriProOrchestrator()
            >>> await orchestrator.initialize()
            >>> print("Orchestrator ready!")
        """
        if self._initialized:
            logger.warning("Orchestrator already initialized")
            return

        logger.info("Initializing GriProOrchestrator...")

        try:
            # 1. Initialize PRO Accounts Manager
            self._pro_accounts = ProAccountsManager()
            accounts = self._pro_accounts.load_pro_accounts()
            enabled_count = sum(1 for v in accounts.values() if v)

            if enabled_count == 0:
                raise OrchestratorError(
                    "No PRO accounts enabled. Enable at least one provider in .env"
                )

            logger.info(f"PRO accounts loaded: {enabled_count} enabled")

            # 2. Initialize Agent Registry
            self._agent_registry = AgentRegistry(load_defaults=True)
            logger.info(
                f"Agent Registry loaded: {len(self._agent_registry)} agents"
            )

            # 3. Initialize LLM Router
            self._llm_router = LLMRouter()
            providers = self._llm_router.validate_providers()
            logger.info(f"LLM Router initialized: {providers}")

            # 4. Initialize Supabase Manager
            if self.settings.has_supabase_config():
                self._supabase = SupabaseManager(
                    url=self.settings.supabase_url,
                    key=self.settings.supabase_anon_key,
                )
                await self._supabase.connect()
                logger.info("Supabase connected")
            else:
                logger.warning(
                    "Supabase not configured. Running without persistence."
                )
                self._supabase = None

            self._initialized = True
            logger.info("GriProOrchestrator initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            raise OrchestratorError(f"Initialization failed: {e}") from e

    async def shutdown(self) -> None:
        """
        Gracefully shutdown the orchestrator.

        Closes database connections and cleans up resources.
        """
        logger.info("Shutting down GriProOrchestrator...")

        if self._supabase:
            await self._supabase.disconnect()

        self._initialized = False
        logger.info("GriProOrchestrator shutdown complete")

    def _ensure_initialized(self) -> None:
        """Ensure orchestrator is initialized."""
        if not self._initialized:
            raise OrchestratorError(
                "Orchestrator not initialized. Call initialize() first."
            )

    def _now(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now(timezone.utc).isoformat()

    # ─────────────────────────────────────────────────────────────────
    # Task Orchestration
    # ─────────────────────────────────────────────────────────────────

    async def execute_task(
        self,
        project_id: str,
        agent_name: str,
        task_description: str,
        system_prompt: Optional[str] = None,
    ) -> TaskResult:
        """
        Execute a task using a specific agent.

        Flow:
        1. Lookup agent in AgentRegistry (by name or alias)
        2. Determine appropriate TaskType for the agent
        3. Use LLMRouter to select optimal LLM provider
        4. Execute task with selected PRO account
        5. Persist result to Supabase
        6. Return TaskResult

        Args:
            project_id: Project identifier.
            agent_name: Agent name or alias (e.g., "primo" or "Primo").
            task_description: Description of the task to execute.
            system_prompt: Optional custom system prompt.

        Returns:
            TaskResult with execution details.

        Raises:
            OrchestratorError: If task execution fails.

        Example:
            >>> result = await orchestrator.execute_task(
            ...     project_id="proj_001",
            ...     agent_name="Primo",
            ...     task_description="Create a detailed project plan for e-commerce app"
            ... )
            >>> print(f"Status: {result.status}")
            >>> print(f"Agent: {result.agent}")
        """
        self._ensure_initialized()

        logger.info(
            f"Executing task: project={project_id}, agent={agent_name}"
        )

        try:
            # 1. Get agent from registry
            agent = self._agent_registry.get_agent(agent_name)
            logger.debug(f"Found agent: {agent.name} ({agent.alias})")

            # 2. Determine task type based on agent type
            task_type = self.AGENT_TASK_MAP.get(
                agent.agent_type, TaskType.GENERAL
            )
            logger.debug(f"Task type: {task_type.value}")

            # 3. Get optimal LLM provider
            provider = self._llm_router.get_provider(task_type.value)
            logger.debug(f"Selected provider: {provider}")

            # 4. Build system prompt
            if not system_prompt:
                system_prompt = self._build_system_prompt(agent, task_description)

            # 5. Execute via LLM Router
            llm_response = self._llm_router.call_llm(
                task_type=task_type.value,
                prompt=task_description,
                system=system_prompt,
            )

            # 6. Create result
            timestamp = self._now()

            if llm_response.success:
                result = TaskResult(
                    status=TaskStatus.COMPLETED,
                    result=llm_response.content,
                    agent=agent.alias,
                    provider=provider,
                    timestamp=timestamp,
                    metadata={
                        "agent_name": agent.name,
                        "agent_type": agent.agent_type.value,
                        "task_type": task_type.value,
                    },
                )
            else:
                result = TaskResult(
                    status=TaskStatus.FAILED,
                    result="",
                    agent=agent.alias,
                    provider=provider,
                    timestamp=timestamp,
                    error=llm_response.error,
                    metadata={
                        "agent_name": agent.name,
                        "task_type": task_type.value,
                    },
                )

            # 7. Persist to database
            if self._supabase:
                await self._persist_task_result(project_id, agent, result)

            logger.info(
                f"Task completed: status={result.status.value}, "
                f"agent={result.agent}, provider={result.provider}"
            )

            return result

        except AgentNotFoundError as e:
            logger.error(f"Agent not found: {e}")
            raise OrchestratorError(f"Agent not found: {agent_name}") from e
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            raise OrchestratorError(f"Task execution failed: {e}") from e

    async def run_workflow(
        self,
        project_id: str,
        workflow_type: str,
        initial_context: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Run an automated workflow across multiple agents.

        Workflow Types:
        - FULL: Complete project lifecycle (all phases)
        - PLANNING: Primo creates plan, Guru reviews
        - DEVELOPMENT: Frontend + Backend + Testing
        - TESTING: QA + Security analysis
        - DEPLOYMENT: DevOps preparation
        - DOCUMENTATION: Marketing/docs generation

        Args:
            project_id: Project identifier.
            workflow_type: Type of workflow to execute.
            initial_context: Optional initial context/requirements.

        Returns:
            Dictionary with workflow results by phase.

        Raises:
            WorkflowError: If workflow execution fails.

        Example:
            >>> results = await orchestrator.run_workflow(
            ...     project_id="proj_001",
            ...     workflow_type="full",
            ...     initial_context="E-commerce app with React and FastAPI"
            ... )
            >>> for phase, result in results.items():
            ...     print(f"{phase}: {result['status']}")
        """
        self._ensure_initialized()

        # Normalize workflow type
        try:
            wf_type = WorkflowType(workflow_type.lower())
        except ValueError:
            valid = [w.value for w in WorkflowType]
            raise WorkflowError(
                f"Invalid workflow type '{workflow_type}'. Valid: {valid}"
            )

        logger.info(f"Starting workflow: {wf_type.value} for project {project_id}")

        # Get workflow phases
        phases = self.WORKFLOW_PHASES.get(wf_type, [])
        if not phases:
            raise WorkflowError(f"No phases defined for workflow: {wf_type.value}")

        # Initialize workflow state
        workflow_state = WorkflowState(
            workflow_type=wf_type,
            current_phase="initializing",
            agents_involved=[agent for _, agent in phases],
        )
        self._active_workflows[project_id] = workflow_state

        results: dict[str, Any] = {}
        context = initial_context or ""

        try:
            # Log workflow start
            if self._supabase:
                await self._supabase.log_activity(
                    project_id=project_id,
                    agent="Orchestrator",
                    action="workflow_started",
                    description=f"Started {wf_type.value} workflow",
                    metadata={"phases": [p[0] for p in phases]},
                )

            # Execute each phase
            for i, (phase_name, agent_name) in enumerate(phases):
                workflow_state.current_phase = phase_name
                workflow_state.progress = int((i / len(phases)) * 100)

                logger.info(f"Executing phase: {phase_name} with {agent_name}")

                # Build phase-specific task
                task_description = self._build_phase_task(
                    phase_name, agent_name, context
                )

                # Execute task
                try:
                    result = await self.execute_task(
                        project_id=project_id,
                        agent_name=agent_name,
                        task_description=task_description,
                    )

                    results[phase_name] = {
                        "status": result.status.value,
                        "agent": result.agent,
                        "provider": result.provider,
                        "timestamp": result.timestamp,
                        "error": result.error,
                    }

                    # Update context with result for next phase
                    if result.status == TaskStatus.COMPLETED and result.result:
                        context += f"\n\n[{phase_name} output]:\n{result.result[:500]}"

                    workflow_state.completed_phases.append(phase_name)

                except OrchestratorError as e:
                    logger.error(f"Phase {phase_name} failed: {e}")
                    results[phase_name] = {
                        "status": TaskStatus.FAILED.value,
                        "agent": agent_name,
                        "error": str(e),
                    }
                    # Continue with next phase despite failure

            # Workflow completed
            workflow_state.progress = 100
            workflow_state.current_phase = "completed"

            # Log workflow completion
            if self._supabase:
                await self._supabase.log_activity(
                    project_id=project_id,
                    agent="Orchestrator",
                    action="workflow_completed",
                    description=f"Completed {wf_type.value} workflow",
                    metadata={"results": results},
                )

            logger.info(f"Workflow {wf_type.value} completed for {project_id}")

            return results

        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            raise WorkflowError(f"Workflow execution failed: {e}") from e
        finally:
            # Clean up workflow state
            self._active_workflows.pop(project_id, None)

    async def handle_agent_communication(
        self,
        project_id: str,
        from_agent: str,
        to_agent: str,
        message: str,
    ) -> dict[str, Any]:
        """
        Handle communication between agents.

        Allows agents to send messages and requests to each other,
        facilitating collaboration on complex tasks.

        Args:
            project_id: Project identifier.
            from_agent: Sending agent name or alias.
            to_agent: Receiving agent name or alias.
            message: Message content.

        Returns:
            Response from the receiving agent.

        Example:
            >>> response = await orchestrator.handle_agent_communication(
            ...     project_id="proj_001",
            ...     from_agent="Primo",
            ...     to_agent="Fronti",
            ...     message="Please implement the login component"
            ... )
        """
        self._ensure_initialized()

        logger.info(f"Agent communication: {from_agent} → {to_agent}")

        # Validate agents exist
        sender = self._agent_registry.get_agent(from_agent)
        receiver = self._agent_registry.get_agent(to_agent)

        # Build context for receiving agent
        context = (
            f"You are {receiver.alias}, receiving a message from {sender.alias}.\n"
            f"Message from {sender.alias}: {message}\n\n"
            f"Please respond appropriately based on your role as {receiver.config.get('role', receiver.agent_type.value)}."
        )

        # Execute as task for receiving agent
        result = await self.execute_task(
            project_id=project_id,
            agent_name=receiver.name,
            task_description=context,
        )

        # Log communication
        if self._supabase:
            await self._supabase.log_activity(
                project_id=project_id,
                agent=sender.alias,
                action="agent_communication",
                description=f"Message to {receiver.alias}",
                metadata={
                    "from": sender.alias,
                    "to": receiver.alias,
                    "message_preview": message[:100],
                },
            )

        return {
            "from": sender.alias,
            "to": receiver.alias,
            "message": message,
            "response": result.result,
            "status": result.status.value,
            "timestamp": result.timestamp,
        }

    # ─────────────────────────────────────────────────────────────────
    # State Management
    # ─────────────────────────────────────────────────────────────────

    async def get_project_status(self, project_id: str) -> dict[str, Any]:
        """
        Get comprehensive project status.

        Args:
            project_id: Project identifier.

        Returns:
            Dictionary with project details, progress, and agent states.

        Example:
            >>> status = await orchestrator.get_project_status("proj_001")
            >>> print(f"Progress: {status['progress']}%")
        """
        self._ensure_initialized()

        if not self._supabase:
            return {"error": "Database not configured"}

        try:
            # Get project info
            project = await self._supabase.get_project(project_id)

            # Get progress
            progress = await self._supabase.get_project_progress(project_id)

            # Get recent activities
            activities = await self._supabase.get_activities(
                project_id, limit=10
            )

            # Check active workflow
            active_workflow = self._active_workflows.get(project_id)

            return {
                "project": project,
                "progress": progress,
                "recent_activities": activities,
                "active_workflow": (
                    {
                        "type": active_workflow.workflow_type.value,
                        "phase": active_workflow.current_phase,
                        "progress": active_workflow.progress,
                    }
                    if active_workflow
                    else None
                ),
            }

        except NotFoundError:
            raise OrchestratorError(f"Project not found: {project_id}")
        except Exception as e:
            logger.error(f"Failed to get project status: {e}")
            raise OrchestratorError(f"Failed to get project status: {e}") from e

    async def get_agent_state(
        self,
        project_id: str,
        agent_name: str,
    ) -> dict[str, Any]:
        """
        Get state of a specific agent in a project.

        Args:
            project_id: Project identifier.
            agent_name: Agent name or alias.

        Returns:
            Agent's current state.
        """
        self._ensure_initialized()

        agent = self._agent_registry.get_agent(agent_name)

        if not self._supabase:
            return {"agent": agent.alias, "state": {}}

        try:
            state = await self._supabase.get_agent_state(project_id, agent.alias)
            return {"agent": agent.alias, "state": state}
        except NotFoundError:
            return {"agent": agent.alias, "state": {}}

    async def update_agent_state(
        self,
        project_id: str,
        agent_name: str,
        state: dict[str, Any],
    ) -> None:
        """
        Update state of a specific agent.

        Args:
            project_id: Project identifier.
            agent_name: Agent name or alias.
            state: New state data.
        """
        self._ensure_initialized()

        agent = self._agent_registry.get_agent(agent_name)

        if self._supabase:
            await self._supabase.update_agent_state(
                project_id, agent.alias, state
            )

    # ─────────────────────────────────────────────────────────────────
    # Utilities
    # ─────────────────────────────────────────────────────────────────

    async def validate_project(self, project_id: str) -> bool:
        """
        Validate that a project exists and is accessible.

        Args:
            project_id: Project identifier.

        Returns:
            True if project is valid.
        """
        self._ensure_initialized()

        if not self._supabase:
            logger.warning("Cannot validate project without database")
            return True  # Assume valid if no DB

        try:
            await self._supabase.get_project(project_id)
            return True
        except NotFoundError:
            return False

    async def list_available_agents(self) -> list[dict[str, Any]]:
        """
        List all available agents with their details.

        Returns:
            List of agent information dictionaries.

        Example:
            >>> agents = await orchestrator.list_available_agents()
            >>> for agent in agents:
            ...     print(f"{agent['alias']}: {agent['role']}")
        """
        self._ensure_initialized()

        agents = []
        for agent in self._agent_registry:
            agents.append({
                "name": agent.name,
                "alias": agent.alias,
                "type": agent.agent_type.value,
                "role": agent.config.get("role", ""),
                "description": agent.config.get("description", ""),
                "status": "active" if agent.status else "inactive",
            })

        return agents

    async def create_project(
        self,
        name: str,
        specs: dict[str, Any],
    ) -> str:
        """
        Create a new project.

        Args:
            name: Project name.
            specs: Project specifications.

        Returns:
            Generated project ID.
        """
        self._ensure_initialized()

        if not self._supabase:
            raise OrchestratorError("Cannot create project without database")

        project_id = await self._supabase.create_project(name, specs)

        # Log creation
        await self._supabase.log_activity(
            project_id=project_id,
            agent="Orchestrator",
            action="project_created",
            description=f"Created project: {name}",
        )

        return project_id

    # ─────────────────────────────────────────────────────────────────
    # Private Helpers
    # ─────────────────────────────────────────────────────────────────

    def _build_system_prompt(self, agent: Agent, task: str) -> str:
        """Build system prompt for an agent."""
        role = agent.config.get("role", agent.agent_type.value)
        description = agent.config.get("description", "")

        return (
            f"You are {agent.alias}, a {role} in the GriPro system.\n"
            f"{description}\n\n"
            f"Respond professionally and focus on your area of expertise.\n"
            f"Be concise but thorough."
        )

    def _build_phase_task(
        self,
        phase: str,
        agent_name: str,
        context: str,
    ) -> str:
        """Build task description for a workflow phase."""
        agent = self._agent_registry.get_agent(agent_name)

        phase_tasks = {
            "planning": "Create a detailed project plan with milestones, tasks, and timeline.",
            "frontend": "Design and implement the frontend components and user interface.",
            "backend": "Implement the backend API, business logic, and data models.",
            "testing": "Create comprehensive test cases and verify functionality.",
            "security": "Perform security analysis and identify potential vulnerabilities.",
            "deployment": "Prepare deployment configuration and infrastructure setup.",
            "documentation": "Write user documentation, API docs, and guides.",
            "review": "Review all work, provide feedback, and ensure quality standards.",
        }

        base_task = phase_tasks.get(phase, f"Execute {phase} phase tasks.")

        return (
            f"Phase: {phase}\n"
            f"Agent: {agent.alias} ({agent.config.get('role', '')})\n\n"
            f"Task: {base_task}\n\n"
            f"Context:\n{context if context else 'No additional context provided.'}"
        )

    async def _persist_task_result(
        self,
        project_id: str,
        agent: Agent,
        result: TaskResult,
    ) -> None:
        """Persist task result to database."""
        if not self._supabase:
            return

        # Update agent state
        await self._supabase.update_agent_state(
            project_id=project_id,
            agent_name=agent.alias,
            state={
                "last_task": result.timestamp,
                "last_status": result.status.value,
                "provider_used": result.provider,
            },
        )

        # Log activity
        await self._supabase.log_activity(
            project_id=project_id,
            agent=agent.alias,
            action="task_completed" if result.status == TaskStatus.COMPLETED else "task_failed",
            description=f"Task executed via {result.provider}",
            metadata=result.metadata,
        )

    # ─────────────────────────────────────────────────────────────────
    # Context Manager Support
    # ─────────────────────────────────────────────────────────────────

    async def __aenter__(self) -> "GriProOrchestrator":
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.shutdown()
