"""
Orchestrator Module
Re-exports the main GriProOrchestrator from core module.

The orchestrator is the central component that integrates:
- AgentRegistry: Agent management
- LLMRouter: LLM provider routing
- SupabaseManager: Data persistence
- ProAccountsManager: PRO account validation

Usage:
    from orchestrator import GriProOrchestrator

    async with GriProOrchestrator() as orch:
        result = await orch.execute_task(...)
"""

from core.gripro_orchestrator import (
    GriProOrchestrator,
    OrchestratorError,
    TaskResult,
    TaskStatus,
    WorkflowError,
    WorkflowState,
    WorkflowType,
)

__all__ = [
    "GriProOrchestrator",
    "OrchestratorError",
    "TaskResult",
    "TaskStatus",
    "WorkflowError",
    "WorkflowState",
    "WorkflowType",
]
