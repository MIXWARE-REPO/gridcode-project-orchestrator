"""
Project routes for the GriPro Dashboard API.
Handles project details, status, and activity timeline.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.models.schemas import (
    ActivitiesResponse,
    ActivityItem,
    AgentInfo,
    AgentStatus,
    ProjectDetail,
    ProjectPhase,
    ProjectStatus,
    ProjectSummary,
    TokenPayload,
)
from api.routes.auth import get_current_project

router = APIRouter(prefix="/projects", tags=["Projects"])


# Demo data for development (replace with Supabase queries in production)
def get_demo_project(project_id: str) -> Optional[dict]:
    """Get demo project data."""
    demo_projects = {
        "proj-001-uuid": {
            "id": "proj-001-uuid",
            "name": "E-Commerce Platform",
            "code": "GRIP-001",
            "description": "Full-stack e-commerce platform with React frontend and FastAPI backend",
            "status": ProjectStatus.IMPLEMENTATION,
            "progress": 65,
            "current_phase": "Implementation",
            "created_at": datetime.utcnow() - timedelta(days=30),
            "updated_at": datetime.utcnow() - timedelta(hours=2),
            "estimated_completion": datetime.utcnow() + timedelta(days=15),
            "total_hours": 156.5,
            "hours_by_department": {
                "frontend": 45.0,
                "backend": 62.5,
                "devops": 18.0,
                "qa": 22.0,
                "security": 9.0,
            },
        },
        "proj-002-uuid": {
            "id": "proj-002-uuid",
            "name": "Mobile Banking App",
            "code": "GRIP-002",
            "description": "Secure mobile banking application with biometric authentication",
            "status": ProjectStatus.DESIGN,
            "progress": 25,
            "current_phase": "Solution Design",
            "created_at": datetime.utcnow() - timedelta(days=10),
            "updated_at": datetime.utcnow() - timedelta(hours=5),
            "estimated_completion": datetime.utcnow() + timedelta(days=45),
            "total_hours": 42.0,
            "hours_by_department": {
                "frontend": 8.0,
                "backend": 15.0,
                "security": 12.0,
                "qa": 5.0,
                "devops": 2.0,
            },
        },
        "demo-project-uuid": {
            "id": "demo-project-uuid",
            "name": "Demo Project",
            "code": "DEMO-123",
            "description": "Interactive demo project to showcase GriPro capabilities",
            "status": ProjectStatus.IMPLEMENTATION,
            "progress": 45,
            "current_phase": "Implementation",
            "created_at": datetime.utcnow() - timedelta(days=5),
            "updated_at": datetime.utcnow() - timedelta(minutes=30),
            "estimated_completion": datetime.utcnow() + timedelta(days=20),
            "total_hours": 28.5,
            "hours_by_department": {
                "frontend": 10.0,
                "backend": 12.0,
                "devops": 3.5,
                "qa": 2.0,
                "security": 1.0,
            },
        },
    }
    return demo_projects.get(project_id)


def get_project_phases(status: ProjectStatus, progress: int) -> list[ProjectPhase]:
    """Generate project phases based on current status."""
    phases_config = [
        ("Discovery", "Understanding requirements and project scope"),
        ("Solution Design", "Architecture and technical planning"),
        ("Implementation", "Building the solution with our AI team"),
        ("Client Validation", "Testing and approval with stakeholders"),
        ("Operation", "Deployment and ongoing support"),
    ]

    status_map = {
        ProjectStatus.DISCOVERY: 0,
        ProjectStatus.DESIGN: 1,
        ProjectStatus.IMPLEMENTATION: 2,
        ProjectStatus.VALIDATION: 3,
        ProjectStatus.OPERATION: 4,
        ProjectStatus.COMPLETED: 5,
    }

    current_phase_idx = status_map.get(status, 2)

    phases = []
    for i, (name, description) in enumerate(phases_config):
        if i < current_phase_idx:
            phase_status = "completed"
            phase_progress = 100
        elif i == current_phase_idx:
            phase_status = "in_progress"
            # Calculate phase progress based on overall progress
            phase_progress = min(100, max(0, (progress - (i * 20)) * 5))
        else:
            phase_status = "pending"
            phase_progress = 0

        phases.append(ProjectPhase(
            number=i + 1,
            name=name,
            status=phase_status,
            progress=phase_progress,
            description=description,
        ))

    return phases


def get_project_agents(project_id: str) -> list[AgentInfo]:
    """Get agent status for a project."""
    # Demo agent status (replace with real agent state in production)
    now = datetime.utcnow()

    return [
        AgentInfo(
            name="primo",
            alias="Primo",
            status=AgentStatus.WORKING,
            current_task="Coordinating sprint tasks",
            progress=100,
            last_activity=now - timedelta(minutes=5),
        ),
        AgentInfo(
            name="fronti_frontend",
            alias="Fronti",
            status=AgentStatus.WORKING,
            current_task="Building dashboard components",
            progress=72,
            last_activity=now - timedelta(minutes=12),
        ),
        AgentInfo(
            name="baky_backend",
            alias="Baky",
            status=AgentStatus.WORKING,
            current_task="Implementing API endpoints",
            progress=68,
            last_activity=now - timedelta(minutes=8),
        ),
        AgentInfo(
            name="secu_security",
            alias="Secu",
            status=AgentStatus.IDLE,
            current_task=None,
            progress=100,
            last_activity=now - timedelta(hours=2),
        ),
        AgentInfo(
            name="qai_testing",
            alias="Qai",
            status=AgentStatus.IDLE,
            current_task=None,
            progress=45,
            last_activity=now - timedelta(hours=1),
        ),
        AgentInfo(
            name="devi_devops",
            alias="Devi",
            status=AgentStatus.COMPLETED,
            current_task=None,
            progress=100,
            last_activity=now - timedelta(hours=4),
        ),
        AgentInfo(
            name="mark_marketing",
            alias="Mark",
            status=AgentStatus.IDLE,
            current_task=None,
            progress=30,
            last_activity=now - timedelta(days=1),
        ),
    ]


def get_project_activities(project_id: str, limit: int, offset: int) -> tuple[list[ActivityItem], int]:
    """Get activity timeline for a project."""
    now = datetime.utcnow()

    # Demo activities (replace with Supabase query in production)
    all_activities = [
        ActivityItem(
            id="act-001",
            timestamp=now - timedelta(minutes=5),
            agent="Primo",
            action="task_assigned",
            description="Assigned dashboard component task to Fronti",
            category="communication",
        ),
        ActivityItem(
            id="act-002",
            timestamp=now - timedelta(minutes=12),
            agent="Fronti",
            action="code_commit",
            description="Implemented ProjectHeader component with responsive design",
            category="code",
        ),
        ActivityItem(
            id="act-003",
            timestamp=now - timedelta(minutes=30),
            agent="Baky",
            action="code_commit",
            description="Added /api/projects endpoints with Pydantic validation",
            category="code",
        ),
        ActivityItem(
            id="act-004",
            timestamp=now - timedelta(hours=1),
            agent="Qai",
            action="test_run",
            description="Ran integration tests: 45 passed, 3 pending",
            category="review",
        ),
        ActivityItem(
            id="act-005",
            timestamp=now - timedelta(hours=2),
            agent="Secu",
            action="security_review",
            description="Completed security audit of authentication flow",
            category="review",
        ),
        ActivityItem(
            id="act-006",
            timestamp=now - timedelta(hours=4),
            agent="Devi",
            action="deployment",
            description="Deployed staging environment to Hetzner VPS",
            category="deployment",
        ),
        ActivityItem(
            id="act-007",
            timestamp=now - timedelta(hours=6),
            agent="Primo",
            action="milestone_update",
            description="Sprint 3 planning completed, tasks distributed",
            category="communication",
        ),
        ActivityItem(
            id="act-008",
            timestamp=now - timedelta(hours=12),
            agent="Fronti",
            action="code_commit",
            description="Added Tailwind CSS configuration and base styles",
            category="code",
        ),
        ActivityItem(
            id="act-009",
            timestamp=now - timedelta(days=1),
            agent="Baky",
            action="code_commit",
            description="Set up FastAPI project structure with modular routing",
            category="code",
        ),
        ActivityItem(
            id="act-010",
            timestamp=now - timedelta(days=1, hours=2),
            agent="Guru",
            action="quality_review",
            description="Approved architecture design for implementation phase",
            category="review",
        ),
    ]

    total = len(all_activities)
    paginated = all_activities[offset:offset + limit]

    return paginated, total


@router.get("/current", response_model=ProjectDetail)
async def get_current_project_details(
    token: TokenPayload = Depends(get_current_project),
):
    """Get full details of the current authenticated project."""
    project = get_demo_project(token.project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return ProjectDetail(
        id=project["id"],
        name=project["name"],
        code=project["code"],
        description=project.get("description"),
        status=project["status"],
        progress=project["progress"],
        current_phase=project["current_phase"],
        phases=get_project_phases(project["status"], project["progress"]),
        agents=get_project_agents(project["id"]),
        created_at=project["created_at"],
        updated_at=project["updated_at"],
        estimated_completion=project.get("estimated_completion"),
        total_hours=project.get("total_hours", 0),
        hours_by_department=project.get("hours_by_department", {}),
    )


@router.get("/current/summary", response_model=ProjectSummary)
async def get_current_project_summary(
    token: TokenPayload = Depends(get_current_project),
):
    """Get brief summary of the current project."""
    project = get_demo_project(token.project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return ProjectSummary(
        id=project["id"],
        name=project["name"],
        code=project["code"],
        status=project["status"],
        progress=project["progress"],
        current_phase=project["current_phase"],
        created_at=project["created_at"],
    )


@router.get("/current/activities", response_model=ActivitiesResponse)
async def get_current_project_activities(
    token: TokenPayload = Depends(get_current_project),
    limit: int = Query(default=10, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
):
    """Get activity timeline for the current project."""
    project = get_demo_project(token.project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    activities, total = get_project_activities(token.project_id, limit, offset)

    return ActivitiesResponse(
        items=activities,
        total=total,
        offset=offset,
        limit=limit,
        has_more=(offset + limit) < total,
    )


@router.get("/current/hours")
async def get_current_project_hours(
    token: TokenPayload = Depends(get_current_project),
):
    """Get hours breakdown by department for the current project."""
    project = get_demo_project(token.project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return {
        "total_hours": project.get("total_hours", 0),
        "by_department": project.get("hours_by_department", {}),
        "last_updated": project["updated_at"].isoformat(),
    }
