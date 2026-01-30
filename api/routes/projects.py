"""
Project routes for the GriPro Dashboard API.
Handles project details, status, and activity timeline.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Optional, List, Tuple

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


def get_project_activities(project_id: str, limit: int, offset: int) -> Tuple[List[ActivityItem], int]:
    """
    Get activity timeline for a project.

    Activities are distributed realistically:
    - Max 8 hours of work per day per department
    - At least 2 hours gap between department handoffs
    - Internal meetings counted for Primo coordination
    - Work happens during business hours (9-18)
    """
    now = datetime.utcnow()

    # Get project to determine start date and hours
    project = get_demo_project(project_id)
    if not project:
        return [], 0

    project_start = project.get("created_at", now - timedelta(days=5))
    total_hours = project.get("total_hours", 28.5)
    hours_by_dept = project.get("hours_by_department", {})

    # Generate realistic activities based on hours
    all_activities = _generate_realistic_activities(
        project_id=project_id,
        project_start=project_start,
        hours_by_dept=hours_by_dept,
        total_hours=total_hours,
        current_time=now,
    )

    total = len(all_activities)
    paginated = all_activities[offset:offset + limit]

    return paginated, total


def _generate_realistic_activities(
    project_id: str,
    project_start: datetime,
    hours_by_dept: dict,
    total_hours: float,
    current_time: datetime,
) -> List[ActivityItem]:
    """
    Generate realistic activity timeline respecting work constraints.

    Rules:
    - Max 8 hours per day per developer
    - 2+ hours gap between department handoffs
    - Work during business hours (9:00 - 18:00)
    - Internal meetings for coordination
    """
    import random

    activities = []
    activity_id = 1

    # Map departments to agents and categories
    dept_config = {
        "frontend": {"agent": "Fronti", "category": "code", "tasks": [
            "Implemented responsive layout",
            "Added component styling",
            "Built form validation",
            "Created dashboard widgets",
            "Integrated API calls",
        ]},
        "backend": {"agent": "Baky", "category": "code", "tasks": [
            "Added API endpoint",
            "Implemented authentication",
            "Database query optimization",
            "Added middleware validation",
            "Created data models",
        ]},
        "devops": {"agent": "Devi", "category": "deployment", "tasks": [
            "Configured CI/CD pipeline",
            "Deployed to staging",
            "Set up monitoring",
            "Docker configuration",
        ]},
        "qa": {"agent": "Qai", "category": "review", "tasks": [
            "Ran test suite",
            "Integration testing",
            "Bug verification",
            "Regression testing",
        ]},
        "security": {"agent": "Secu", "category": "security", "tasks": [
            "Security audit completed",
            "Vulnerability scan",
            "Auth flow review",
        ]},
    }

    # Track last activity time per department (for 8h/day limit)
    dept_daily_hours = {}
    dept_last_activity = {}
    current_day = project_start.date()

    # Sort departments by hours to process in order
    sorted_depts = sorted(hours_by_dept.items(), key=lambda x: -x[1])

    # Distribute work realistically across days
    work_cursor = project_start.replace(hour=9, minute=0, second=0, microsecond=0)

    for dept_name, dept_hours in sorted_depts:
        config = dept_config.get(dept_name, {
            "agent": dept_name.title(),
            "category": "code",
            "tasks": [f"Development work - {dept_name}"]
        })

        remaining_hours = dept_hours
        work_sessions = []

        # Split into work sessions (max 4 hours per session, 2 sessions per day max)
        while remaining_hours > 0:
            session_hours = min(remaining_hours, random.uniform(2.5, 4.0))
            work_sessions.append(session_hours)
            remaining_hours -= session_hours

        # Schedule sessions with realistic gaps
        session_cursor = work_cursor
        for i, session_hours in enumerate(work_sessions):
            # Check if we need to move to next day (8h limit)
            day_key = f"{dept_name}_{session_cursor.date()}"
            current_day_hours = dept_daily_hours.get(day_key, 0)

            if current_day_hours + session_hours > 8:
                # Move to next business day
                session_cursor += timedelta(days=1)
                while session_cursor.weekday() >= 5:  # Skip weekends
                    session_cursor += timedelta(days=1)
                session_cursor = session_cursor.replace(hour=9, minute=random.randint(0, 30))
                day_key = f"{dept_name}_{session_cursor.date()}"
                current_day_hours = 0

            # Don't create activities in the future
            if session_cursor > current_time:
                break

            # Create activity for this session
            task_desc = random.choice(config["tasks"])
            activities.append(ActivityItem(
                id=f"act-{activity_id:03d}",
                timestamp=session_cursor,
                agent=config["agent"],
                action="code_commit" if config["category"] == "code" else config["category"],
                description=task_desc,
                category=config["category"],
            ))
            activity_id += 1

            # Update tracking
            dept_daily_hours[day_key] = current_day_hours + session_hours
            dept_last_activity[dept_name] = session_cursor

            # Add gap for next session (2-3 hours including lunch if applicable)
            gap_hours = random.uniform(2.0, 3.5)
            session_cursor += timedelta(hours=session_hours + gap_hours)

            # Handle lunch break
            if session_cursor.hour >= 13 and session_cursor.hour < 14:
                session_cursor = session_cursor.replace(hour=14, minute=random.randint(0, 15))

            # Handle end of day
            if session_cursor.hour >= 18:
                session_cursor += timedelta(days=1)
                while session_cursor.weekday() >= 5:
                    session_cursor += timedelta(days=1)
                session_cursor = session_cursor.replace(hour=9, minute=random.randint(0, 30))

        # Update work cursor for next department (add handoff gap)
        if work_sessions:
            work_cursor = session_cursor + timedelta(hours=2)

    # Add Primo coordination activities (internal meetings)
    primo_activities = [
        ("task_assigned", "Assigned tasks to development team", "communication"),
        ("milestone_update", "Sprint planning completed", "communication"),
        ("status_update", "Progress review with team", "communication"),
    ]

    # Add a Primo activity for every ~8 hours of work
    primo_count = max(1, int(total_hours / 8))
    time_step = (current_time - project_start) / (primo_count + 1)

    for i in range(primo_count):
        primo_time = project_start + time_step * (i + 1)
        # Primo works during business hours
        if primo_time.hour < 9:
            primo_time = primo_time.replace(hour=10, minute=random.randint(0, 30))
        elif primo_time.hour >= 18:
            primo_time = primo_time.replace(hour=16, minute=random.randint(0, 30))

        if primo_time <= current_time:
            action, desc, cat = random.choice(primo_activities)
            activities.append(ActivityItem(
                id=f"act-primo-{i+1:02d}",
                timestamp=primo_time,
                agent="Primo",
                action=action,
                description=desc,
                category=cat,
            ))

    # Sort by timestamp (newest first)
    activities.sort(key=lambda x: x.timestamp, reverse=True)

    return activities


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
