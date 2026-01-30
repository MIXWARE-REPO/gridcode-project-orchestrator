"""
Pydantic schemas for API request/response models.
Compatible with Python 3.8+
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# === Enums ===

class ProjectStatus(str, Enum):
    """Project status states."""
    DISCOVERY = "discovery"
    DESIGN = "design"
    IMPLEMENTATION = "implementation"
    VALIDATION = "validation"
    OPERATION = "operation"
    COMPLETED = "completed"
    PAUSED = "paused"


class AgentStatus(str, Enum):
    """Agent work status."""
    IDLE = "idle"
    WORKING = "working"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class MessageRole(str, Enum):
    """Chat message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


# === Auth Schemas ===

class LoginRequest(BaseModel):
    """Login request with project code."""
    project_code: str = Field(..., min_length=6, max_length=20)
    email: Optional[str] = None


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    project_id: str
    project_name: str


class TokenPayload(BaseModel):
    """JWT token payload."""
    project_id: str
    client_email: Optional[str]
    client_name: Optional[str]
    exp: datetime
    iat: datetime


# === Project Schemas ===

class AgentInfo(BaseModel):
    """Agent status information."""
    name: str
    alias: str
    status: AgentStatus
    current_task: Optional[str] = None
    progress: int = Field(ge=0, le=100)
    last_activity: Optional[datetime] = None


class ProjectPhase(BaseModel):
    """Project phase information."""
    number: int
    name: str
    status: str  # pending, in_progress, completed
    progress: int = Field(ge=0, le=100)
    description: str


class ProjectSummary(BaseModel):
    """Brief project summary."""
    id: str
    name: str
    code: str
    status: ProjectStatus
    progress: int = Field(ge=0, le=100)
    current_phase: str
    created_at: datetime


class ProjectDetail(BaseModel):
    """Full project details."""
    id: str
    name: str
    code: str
    description: Optional[str]
    status: ProjectStatus
    progress: int = Field(ge=0, le=100)
    current_phase: str
    phases: List[ProjectPhase]
    agents: List[AgentInfo]
    created_at: datetime
    updated_at: datetime
    estimated_completion: Optional[datetime] = None

    # Hours tracking
    total_hours: float = 0
    hours_by_department: Dict[str, float] = Field(default_factory=dict)


class ActivityItem(BaseModel):
    """Activity timeline item."""
    id: str
    timestamp: datetime
    agent: str
    action: str
    description: str
    category: str  # code, review, deployment, communication
    metadata: Optional[dict] = None


class ActivitiesResponse(BaseModel):
    """Paginated activities response."""
    items: List[ActivityItem]
    total: int
    offset: int
    limit: int
    has_more: bool


# === Chat Schemas ===

class ChatMessage(BaseModel):
    """Single chat message."""
    id: str
    role: MessageRole
    content: str
    timestamp: datetime
    metadata: Optional[dict] = None


class ChatRequest(BaseModel):
    """Chat message request."""
    message: str = Field(..., min_length=1, max_length=4000)
    project_id: str
    context: Optional[dict] = None  # Additional context for Primo


class ChatResponse(BaseModel):
    """Chat message response from Primo."""
    message: str
    timestamp: datetime
    suggestions: Optional[List[str]] = None  # Quick reply suggestions
    attachments: Optional[List[dict]] = None  # Files, links, etc.


class ChatHistory(BaseModel):
    """Chat history response."""
    messages: List[ChatMessage]
    total: int
    has_more: bool


# === WebSocket Schemas ===

class WSMessage(BaseModel):
    """WebSocket message format."""
    type: str  # state_update, agent_status, activity_new, chat_message
    data: dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# === Error Schemas ===

class ErrorResponse(BaseModel):
    """API error response."""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
