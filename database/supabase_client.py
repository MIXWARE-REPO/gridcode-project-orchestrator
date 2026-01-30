"""
Supabase Client Module
Manages all database operations with Supabase PostgreSQL.

Provides async methods for:
- Project management (CRUD)
- Agent state persistence
- Activity logging
- Chat history
- Audit trail
"""

import asyncio
import logging
import os
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, Optional, TypeVar
from uuid import uuid4

from supabase import Client, create_client
from supabase.lib.client_options import ClientOptions

logger = logging.getLogger(__name__)

T = TypeVar("T")


class DatabaseError(Exception):
    """Base exception for database operations."""

    pass


class ConnectionError(DatabaseError):
    """Raised when database connection fails."""

    pass


class NotFoundError(DatabaseError):
    """Raised when a record is not found."""

    pass


class ValidationError(DatabaseError):
    """Raised when data validation fails."""

    pass


def with_retry(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
) -> Callable:
    """
    Decorator for automatic retry with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts.
        delay: Initial delay between retries in seconds.
        backoff: Multiplier for delay after each retry.
        exceptions: Tuple of exceptions to catch and retry.

    Returns:
        Decorated function with retry logic.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None
            current_delay = delay

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Retry {attempt + 1}/{max_retries} for {func.__name__}: {e}"
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"Max retries reached for {func.__name__}: {e}"
                        )

            raise DatabaseError(
                f"Operation failed after {max_retries} retries"
            ) from last_exception

        return wrapper

    return decorator


class SupabaseManager:
    """
    Manages all database operations with Supabase.

    Provides async methods for project management, agent state persistence,
    activity logging, chat history, and audit trails.

    Tables expected in Supabase:
        - projects: Project metadata and configuration
        - agent_states: Current state of each agent per project
        - activities: Activity log entries
        - chat_messages: Chat history
        - audit_log: Audit trail for compliance

    Example:
        >>> async def main():
        ...     db = SupabaseManager()
        ...     await db.connect()
        ...
        ...     # Create a project
        ...     project_id = await db.create_project(
        ...         name="My App",
        ...         specs={"description": "A cool app"}
        ...     )
        ...
        ...     # Log activity
        ...     await db.log_activity(
        ...         project_id=project_id,
        ...         agent="Primo",
        ...         action="project_created",
        ...         description="Project initialized"
        ...     )
    """

    def __init__(
        self,
        url: Optional[str] = None,
        key: Optional[str] = None,
    ) -> None:
        """
        Initialize Supabase Manager.

        Args:
            url: Supabase project URL. Uses SUPABASE_URL env var if not provided.
            key: Supabase API key. Uses SUPABASE_KEY env var if not provided.

        Raises:
            ConnectionError: If URL or key are not provided and not in environment.
        """
        self._url = url or os.getenv("SUPABASE_URL")
        self._key = key or os.getenv("SUPABASE_ANON_KEY")

        if not self._url or not self._key:
            raise ConnectionError(
                "Supabase credentials not found. "
                "Set SUPABASE_URL and SUPABASE_ANON_KEY environment variables."
            )

        self._client: Optional[Client] = None
        self._connected = False

        logger.info("SupabaseManager initialized")

    async def connect(self) -> None:
        """
        Establish connection to Supabase.

        Creates the Supabase client and validates the connection
        by performing a simple query.

        Raises:
            ConnectionError: If connection fails.

        Example:
            >>> db = SupabaseManager()
            >>> await db.connect()
            >>> print("Connected!")
        """
        try:
            options = ClientOptions(
                postgrest_client_timeout=10,
                storage_client_timeout=10,
            )
            self._client = create_client(self._url, self._key, options=options)
            self._connected = True
            logger.info("Connected to Supabase successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            raise ConnectionError(f"Failed to connect to Supabase: {e}") from e

    async def disconnect(self) -> None:
        """Close the Supabase connection."""
        self._client = None
        self._connected = False
        logger.info("Disconnected from Supabase")

    def _ensure_connected(self) -> Client:
        """Ensure client is connected and return it."""
        if not self._connected or not self._client:
            raise ConnectionError("Not connected to Supabase. Call connect() first.")
        return self._client

    def _generate_id(self) -> str:
        """Generate a unique ID for records."""
        return str(uuid4())

    def _now(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now(timezone.utc).isoformat()

    # ─────────────────────────────────────────────────────────────────
    # Project Methods
    # ─────────────────────────────────────────────────────────────────

    @with_retry(max_retries=3)
    async def create_project(
        self,
        name: str,
        specs: dict[str, Any],
        owner_id: Optional[str] = None,
    ) -> str:
        """
        Create a new project.

        Args:
            name: Project name.
            specs: Project specifications and configuration.
            owner_id: Optional owner/user ID.

        Returns:
            The generated project ID.

        Raises:
            ValidationError: If name is empty.
            DatabaseError: If creation fails.

        Example:
            >>> project_id = await db.create_project(
            ...     name="E-commerce App",
            ...     specs={
            ...         "description": "Online store",
            ...         "tech_stack": ["nextjs", "fastapi", "postgresql"],
            ...         "deadline": "2025-03-01"
            ...     }
            ... )
        """
        if not name or not name.strip():
            raise ValidationError("Project name cannot be empty")

        client = self._ensure_connected()
        project_id = self._generate_id()

        data = {
            "id": project_id,
            "name": name.strip(),
            "specs": specs,
            "owner_id": owner_id,
            "status": "active",
            "phase": "planning",
            "progress": 0,
            "created_at": self._now(),
            "updated_at": self._now(),
        }

        try:
            result = client.table("projects").insert(data).execute()
            logger.info(f"Created project: {project_id} ({name})")
            return project_id
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            raise DatabaseError(f"Failed to create project: {e}") from e

    @with_retry(max_retries=3)
    async def get_project(self, project_id: str) -> dict[str, Any]:
        """
        Get a project by ID.

        Args:
            project_id: The project's unique ID.

        Returns:
            Project data as dictionary.

        Raises:
            NotFoundError: If project doesn't exist.

        Example:
            >>> project = await db.get_project("abc-123")
            >>> print(project["name"])
        """
        client = self._ensure_connected()

        try:
            result = (
                client.table("projects")
                .select("*")
                .eq("id", project_id)
                .single()
                .execute()
            )

            if not result.data:
                raise NotFoundError(f"Project not found: {project_id}")

            return result.data
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get project {project_id}: {e}")
            raise DatabaseError(f"Failed to get project: {e}") from e

    @with_retry(max_retries=3)
    async def update_project(
        self,
        project_id: str,
        data: dict[str, Any],
    ) -> None:
        """
        Update a project.

        Args:
            project_id: The project's unique ID.
            data: Fields to update.

        Raises:
            NotFoundError: If project doesn't exist.
            DatabaseError: If update fails.

        Example:
            >>> await db.update_project("abc-123", {
            ...     "status": "in_progress",
            ...     "phase": "development",
            ...     "progress": 25
            ... })
        """
        client = self._ensure_connected()

        # Add updated timestamp
        data["updated_at"] = self._now()

        try:
            result = (
                client.table("projects")
                .update(data)
                .eq("id", project_id)
                .execute()
            )

            if not result.data:
                raise NotFoundError(f"Project not found: {project_id}")

            logger.info(f"Updated project: {project_id}")
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to update project {project_id}: {e}")
            raise DatabaseError(f"Failed to update project: {e}") from e

    @with_retry(max_retries=3)
    async def list_projects(
        self,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        List all projects.

        Args:
            status: Optional status filter ("active", "completed", "archived").
            limit: Maximum number of projects to return.

        Returns:
            List of project dictionaries.

        Example:
            >>> projects = await db.list_projects(status="active")
            >>> for p in projects:
            ...     print(p["name"])
        """
        client = self._ensure_connected()

        try:
            query = client.table("projects").select("*")

            if status:
                query = query.eq("status", status)

            result = (
                query.order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            return result.data or []
        except Exception as e:
            logger.error(f"Failed to list projects: {e}")
            raise DatabaseError(f"Failed to list projects: {e}") from e

    @with_retry(max_retries=3)
    async def delete_project(self, project_id: str) -> None:
        """
        Delete a project (soft delete - marks as archived).

        Args:
            project_id: The project's unique ID.

        Raises:
            NotFoundError: If project doesn't exist.

        Example:
            >>> await db.delete_project("abc-123")
        """
        await self.update_project(project_id, {"status": "archived"})
        logger.info(f"Archived project: {project_id}")

    # ─────────────────────────────────────────────────────────────────
    # Agent State Methods
    # ─────────────────────────────────────────────────────────────────

    @with_retry(max_retries=3)
    async def update_agent_state(
        self,
        project_id: str,
        agent_name: str,
        state: dict[str, Any],
    ) -> None:
        """
        Update or create agent state for a project.

        Args:
            project_id: The project's unique ID.
            agent_name: Name of the agent (e.g., "Primo", "Fronti").
            state: Agent's current state data.

        Example:
            >>> await db.update_agent_state(
            ...     project_id="abc-123",
            ...     agent_name="Fronti",
            ...     state={
            ...         "current_task": "Implementing login page",
            ...         "progress": 60,
            ...         "blocked": False
            ...     }
            ... )
        """
        client = self._ensure_connected()

        data = {
            "project_id": project_id,
            "agent_name": agent_name,
            "state": state,
            "updated_at": self._now(),
        }

        try:
            # Upsert: insert or update if exists
            result = (
                client.table("agent_states")
                .upsert(data, on_conflict="project_id,agent_name")
                .execute()
            )

            logger.debug(f"Updated state for {agent_name} in project {project_id}")
        except Exception as e:
            logger.error(f"Failed to update agent state: {e}")
            raise DatabaseError(f"Failed to update agent state: {e}") from e

    @with_retry(max_retries=3)
    async def get_agent_state(
        self,
        project_id: str,
        agent_name: str,
    ) -> dict[str, Any]:
        """
        Get agent state for a project.

        Args:
            project_id: The project's unique ID.
            agent_name: Name of the agent.

        Returns:
            Agent's state data.

        Raises:
            NotFoundError: If agent state doesn't exist.

        Example:
            >>> state = await db.get_agent_state("abc-123", "Fronti")
            >>> print(state["current_task"])
        """
        client = self._ensure_connected()

        try:
            result = (
                client.table("agent_states")
                .select("*")
                .eq("project_id", project_id)
                .eq("agent_name", agent_name)
                .single()
                .execute()
            )

            if not result.data:
                raise NotFoundError(
                    f"Agent state not found: {agent_name} in project {project_id}"
                )

            return result.data.get("state", {})
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get agent state: {e}")
            raise DatabaseError(f"Failed to get agent state: {e}") from e

    @with_retry(max_retries=3)
    async def get_project_progress(self, project_id: str) -> dict[str, Any]:
        """
        Get overall project progress.

        Calculates progress based on agent states and project phase.

        Args:
            project_id: The project's unique ID.

        Returns:
            Dictionary with progress info:
            - progress: Overall percentage (0-100)
            - phase: Current phase name
            - agents: Status of each agent

        Example:
            >>> progress = await db.get_project_progress("abc-123")
            >>> print(f"Progress: {progress['progress']}%")
            >>> print(f"Phase: {progress['phase']}")
        """
        client = self._ensure_connected()

        try:
            # Get project info
            project = await self.get_project(project_id)

            # Get all agent states
            result = (
                client.table("agent_states")
                .select("agent_name, state")
                .eq("project_id", project_id)
                .execute()
            )

            agents = {}
            total_progress = 0
            agent_count = 0

            for row in result.data or []:
                agent_name = row["agent_name"]
                state = row.get("state", {})
                agent_progress = state.get("progress", 0)

                agents[agent_name] = {
                    "progress": agent_progress,
                    "status": state.get("status", "idle"),
                    "current_task": state.get("current_task"),
                }

                total_progress += agent_progress
                agent_count += 1

            avg_progress = (
                int(total_progress / agent_count) if agent_count > 0 else 0
            )

            return {
                "progress": project.get("progress", avg_progress),
                "phase": project.get("phase", "unknown"),
                "status": project.get("status", "active"),
                "agents": agents,
                "updated_at": project.get("updated_at"),
            }
        except Exception as e:
            logger.error(f"Failed to get project progress: {e}")
            raise DatabaseError(f"Failed to get project progress: {e}") from e

    # ─────────────────────────────────────────────────────────────────
    # Activity Methods
    # ─────────────────────────────────────────────────────────────────

    @with_retry(max_retries=3)
    async def log_activity(
        self,
        project_id: str,
        agent: str,
        action: str,
        description: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Log an activity for a project.

        Args:
            project_id: The project's unique ID.
            agent: Agent that performed the action.
            action: Type of action (e.g., "task_started", "file_created").
            description: Human-readable description.
            metadata: Optional additional data.

        Example:
            >>> await db.log_activity(
            ...     project_id="abc-123",
            ...     agent="Fronti",
            ...     action="component_created",
            ...     description="Created LoginForm component",
            ...     metadata={"file": "src/components/LoginForm.tsx"}
            ... )
        """
        client = self._ensure_connected()

        data = {
            "id": self._generate_id(),
            "project_id": project_id,
            "agent": agent,
            "action": action,
            "description": description,
            "metadata": metadata or {},
            "created_at": self._now(),
        }

        try:
            client.table("activities").insert(data).execute()
            logger.debug(f"Logged activity: {agent} - {action}")
        except Exception as e:
            logger.error(f"Failed to log activity: {e}")
            raise DatabaseError(f"Failed to log activity: {e}") from e

    @with_retry(max_retries=3)
    async def get_activities(
        self,
        project_id: str,
        limit: int = 50,
        agent: Optional[str] = None,
        action: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Get activities for a project.

        Args:
            project_id: The project's unique ID.
            limit: Maximum number of activities to return.
            agent: Optional filter by agent name.
            action: Optional filter by action type.

        Returns:
            List of activity records (newest first).

        Example:
            >>> activities = await db.get_activities("abc-123", limit=10)
            >>> for a in activities:
            ...     print(f"{a['agent']}: {a['description']}")
        """
        client = self._ensure_connected()

        try:
            query = (
                client.table("activities")
                .select("*")
                .eq("project_id", project_id)
            )

            if agent:
                query = query.eq("agent", agent)
            if action:
                query = query.eq("action", action)

            result = (
                query.order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get activities: {e}")
            raise DatabaseError(f"Failed to get activities: {e}") from e

    @with_retry(max_retries=3)
    async def get_activity_timeline(
        self,
        project_id: str,
        days: int = 7,
    ) -> list[dict[str, Any]]:
        """
        Get activity timeline grouped by date.

        Args:
            project_id: The project's unique ID.
            days: Number of days to include.

        Returns:
            List of activities with date grouping.

        Example:
            >>> timeline = await db.get_activity_timeline("abc-123")
            >>> for entry in timeline:
            ...     print(f"{entry['date']}: {len(entry['activities'])} activities")
        """
        client = self._ensure_connected()

        try:
            # Get activities from last N days
            from_date = datetime.now(timezone.utc)
            from_date = from_date.replace(
                hour=0, minute=0, second=0, microsecond=0
            )

            result = (
                client.table("activities")
                .select("*")
                .eq("project_id", project_id)
                .order("created_at", desc=True)
                .limit(500)
                .execute()
            )

            # Group by date
            grouped: dict[str, list] = {}
            for activity in result.data or []:
                date_str = activity["created_at"][:10]  # YYYY-MM-DD
                if date_str not in grouped:
                    grouped[date_str] = []
                grouped[date_str].append(activity)

            # Convert to timeline format
            timeline = [
                {"date": date, "activities": activities}
                for date, activities in sorted(grouped.items(), reverse=True)
            ][:days]

            return timeline
        except Exception as e:
            logger.error(f"Failed to get activity timeline: {e}")
            raise DatabaseError(f"Failed to get activity timeline: {e}") from e

    # ─────────────────────────────────────────────────────────────────
    # Chat Methods
    # ─────────────────────────────────────────────────────────────────

    @with_retry(max_retries=3)
    async def save_chat_message(
        self,
        project_id: str,
        from_user: bool,
        message: str,
        agent: Optional[str] = None,
    ) -> None:
        """
        Save a chat message.

        Args:
            project_id: The project's unique ID.
            from_user: True if message is from user, False if from agent.
            message: The message content.
            agent: Agent name if message is from an agent.

        Example:
            >>> # User message
            >>> await db.save_chat_message(
            ...     project_id="abc-123",
            ...     from_user=True,
            ...     message="Can you add a dark mode toggle?"
            ... )
            >>>
            >>> # Agent response
            >>> await db.save_chat_message(
            ...     project_id="abc-123",
            ...     from_user=False,
            ...     message="I'll implement dark mode...",
            ...     agent="Primo"
            ... )
        """
        client = self._ensure_connected()

        data = {
            "id": self._generate_id(),
            "project_id": project_id,
            "from_user": from_user,
            "agent": agent,
            "message": message,
            "created_at": self._now(),
        }

        try:
            client.table("chat_messages").insert(data).execute()
            logger.debug(f"Saved chat message for project {project_id}")
        except Exception as e:
            logger.error(f"Failed to save chat message: {e}")
            raise DatabaseError(f"Failed to save chat message: {e}") from e

    @with_retry(max_retries=3)
    async def get_chat_history(
        self,
        project_id: str,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Get chat history for a project.

        Args:
            project_id: The project's unique ID.
            limit: Maximum number of messages to return.

        Returns:
            List of chat messages (oldest first for conversation flow).

        Example:
            >>> messages = await db.get_chat_history("abc-123")
            >>> for msg in messages:
            ...     sender = "User" if msg["from_user"] else msg["agent"]
            ...     print(f"{sender}: {msg['message']}")
        """
        client = self._ensure_connected()

        try:
            result = (
                client.table("chat_messages")
                .select("*")
                .eq("project_id", project_id)
                .order("created_at", desc=False)
                .limit(limit)
                .execute()
            )

            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get chat history: {e}")
            raise DatabaseError(f"Failed to get chat history: {e}") from e

    @with_retry(max_retries=3)
    async def clear_chat_history(self, project_id: str) -> None:
        """
        Clear all chat messages for a project.

        Args:
            project_id: The project's unique ID.

        Example:
            >>> await db.clear_chat_history("abc-123")
        """
        client = self._ensure_connected()

        try:
            client.table("chat_messages").delete().eq(
                "project_id", project_id
            ).execute()
            logger.info(f"Cleared chat history for project {project_id}")
        except Exception as e:
            logger.error(f"Failed to clear chat history: {e}")
            raise DatabaseError(f"Failed to clear chat history: {e}") from e

    # ─────────────────────────────────────────────────────────────────
    # Audit Methods
    # ─────────────────────────────────────────────────────────────────

    @with_retry(max_retries=3)
    async def log_audit(
        self,
        project_id: str,
        action: str,
        details: dict[str, Any],
        user_id: Optional[str] = None,
    ) -> None:
        """
        Log an audit entry.

        Use for compliance-critical actions that need tracking.

        Args:
            project_id: The project's unique ID.
            action: Type of action performed.
            details: Detailed information about the action.
            user_id: Optional user who performed the action.

        Example:
            >>> await db.log_audit(
            ...     project_id="abc-123",
            ...     action="deployment_started",
            ...     details={
            ...         "environment": "production",
            ...         "version": "1.2.0",
            ...         "initiated_by": "Devi"
            ...     }
            ... )
        """
        client = self._ensure_connected()

        data = {
            "id": self._generate_id(),
            "project_id": project_id,
            "action": action,
            "details": details,
            "user_id": user_id,
            "created_at": self._now(),
        }

        try:
            client.table("audit_log").insert(data).execute()
            logger.info(f"Audit log: {action} for project {project_id}")
        except Exception as e:
            logger.error(f"Failed to log audit: {e}")
            raise DatabaseError(f"Failed to log audit: {e}") from e

    @with_retry(max_retries=3)
    async def get_audit_log(
        self,
        project_id: str,
        limit: int = 100,
        action: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Get audit log entries for a project.

        Args:
            project_id: The project's unique ID.
            limit: Maximum number of entries to return.
            action: Optional filter by action type.

        Returns:
            List of audit log entries (newest first).

        Example:
            >>> audit = await db.get_audit_log("abc-123")
            >>> for entry in audit:
            ...     print(f"{entry['action']}: {entry['details']}")
        """
        client = self._ensure_connected()

        try:
            query = (
                client.table("audit_log")
                .select("*")
                .eq("project_id", project_id)
            )

            if action:
                query = query.eq("action", action)

            result = (
                query.order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get audit log: {e}")
            raise DatabaseError(f"Failed to get audit log: {e}") from e

    # ─────────────────────────────────────────────────────────────────
    # Context Manager Support
    # ─────────────────────────────────────────────────────────────────

    async def __aenter__(self) -> "SupabaseManager":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.disconnect()
