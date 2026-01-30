"""
Timeline Normalizer Module - GriPro

Converts raw development hours into realistic human-like timelines.
Ensures the dashboard shows believable work schedules.

Key Rules:
- Maximum 8 hours per day per developer
- Minimum 2 hours gap between task handoffs
- Internal meetings between Primo and devs counted
- Work distributed across realistic business hours
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple
from uuid import uuid4


class WorkdayConfig:
    """Configuration for realistic workday simulation."""
    WORK_START_HOUR = 9       # 9:00 AM
    WORK_END_HOUR = 18        # 6:00 PM
    LUNCH_START = 13          # 1:00 PM
    LUNCH_END = 14            # 2:00 PM
    MAX_HOURS_PER_DAY = 8     # Maximum billable hours per day
    MIN_TASK_GAP_HOURS = 2    # Minimum gap between task handoffs
    INTERNAL_MEET_DURATION = 0.5  # 30 min internal sync


class TaskStatus(Enum):
    """Status of a normalized task."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


@dataclass
class WorkSlot:
    """A slot of work within a day."""
    start: datetime
    end: datetime
    department: str
    task_description: str
    hours: float

    @property
    def duration_hours(self) -> float:
        return (self.end - self.start).total_seconds() / 3600


@dataclass
class DeveloperDay:
    """A developer's work schedule for a single day."""
    date: datetime
    department: str
    slots: List[WorkSlot] = field(default_factory=list)
    total_hours: float = 0.0

    def can_add_hours(self, hours: float) -> bool:
        """Check if more hours can be added to this day."""
        return (self.total_hours + hours) <= WorkdayConfig.MAX_HOURS_PER_DAY

    def get_next_available_time(self) -> datetime:
        """Get the next available time slot."""
        if not self.slots:
            return self.date.replace(
                hour=WorkdayConfig.WORK_START_HOUR,
                minute=0,
                second=0,
                microsecond=0
            )

        last_slot = self.slots[-1]
        next_time = last_slot.end + timedelta(minutes=15)  # 15 min buffer

        # Skip lunch if needed
        if next_time.hour >= WorkdayConfig.LUNCH_START and next_time.hour < WorkdayConfig.LUNCH_END:
            next_time = next_time.replace(hour=WorkdayConfig.LUNCH_END, minute=0)

        return next_time


@dataclass
class NormalizedTask:
    """A task with normalized timeline."""
    id: str
    department: str
    description: str
    raw_hours: float
    normalized_hours: float
    start_time: datetime
    end_time: datetime
    status: TaskStatus = TaskStatus.COMPLETED
    includes_handoff: bool = True
    handoff_hours: float = 0.0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "department": self.department,
            "description": self.description,
            "hours": self.normalized_hours,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "status": self.status.value,
            "duration_display": self._format_duration(),
        }

    def _format_duration(self) -> str:
        """Format duration for display."""
        days = (self.end_time - self.start_time).days
        if days == 0:
            return f"{self.normalized_hours:.1f}h"
        elif days == 1:
            return f"1 day ({self.normalized_hours:.1f}h)"
        else:
            return f"{days} days ({self.normalized_hours:.1f}h)"


@dataclass
class NormalizedTimeline:
    """Complete normalized timeline for a project."""
    project_id: str
    project_name: str
    tasks: List[NormalizedTask] = field(default_factory=list)
    internal_meetings: List[dict] = field(default_factory=list)

    # Summary
    total_raw_hours: float = 0.0
    total_normalized_hours: float = 0.0
    total_calendar_days: int = 0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "project_id": self.project_id,
            "project_name": self.project_name,
            "summary": {
                "total_hours": self.total_normalized_hours,
                "calendar_days": self.total_calendar_days,
                "start_date": self.start_date.isoformat() if self.start_date else None,
                "end_date": self.end_date.isoformat() if self.end_date else None,
            },
            "tasks": [t.to_dict() for t in self.tasks],
            "internal_meetings": self.internal_meetings,
        }


class TimelineNormalizer:
    """
    Normalizes raw development hours into realistic timelines.

    This ensures the client-facing dashboard shows believable work schedules
    that match what a human development team would produce.
    """

    def __init__(self, project_start: Optional[datetime] = None):
        """
        Initialize the normalizer.

        Args:
            project_start: When the project started (defaults to now)
        """
        self.project_start = project_start or datetime.utcnow()
        self._department_schedules: Dict[str, List[DeveloperDay]] = {}

    def _get_or_create_day(
        self,
        department: str,
        target_date: datetime,
    ) -> DeveloperDay:
        """Get or create a developer day for scheduling."""
        if department not in self._department_schedules:
            self._department_schedules[department] = []

        schedule = self._department_schedules[department]
        date_only = target_date.replace(hour=0, minute=0, second=0, microsecond=0)

        # Find existing day
        for day in schedule:
            if day.date.date() == date_only.date():
                return day

        # Create new day
        new_day = DeveloperDay(date=date_only, department=department)
        schedule.append(new_day)
        schedule.sort(key=lambda d: d.date)
        return new_day

    def _find_next_available_slot(
        self,
        department: str,
        hours_needed: float,
        after: datetime,
    ) -> Tuple[datetime, datetime]:
        """
        Find the next available time slot for a department.

        Respects:
        - 8 hour daily limit
        - Business hours (9-18, excluding lunch 13-14)
        - Minimum 2 hour gap after previous department's work
        """
        current_date = after.replace(hour=0, minute=0, second=0, microsecond=0)
        remaining_hours = hours_needed

        slots: List[Tuple[datetime, datetime]] = []
        safety_counter = 0
        max_iterations = 100  # Prevent infinite loop

        while remaining_hours > 0 and safety_counter < max_iterations:
            safety_counter += 1

            # Skip weekends
            while current_date.weekday() >= 5:
                current_date += timedelta(days=1)

            day = self._get_or_create_day(department, current_date)

            # Check if we can add hours to this day
            available_today = WorkdayConfig.MAX_HOURS_PER_DAY - day.total_hours

            if available_today > 0:
                hours_to_add = min(remaining_hours, available_today)
                start_time = day.get_next_available_time()

                # Ensure we don't start before 'after' time
                if start_time < after:
                    start_time = after
                    # Adjust to next business hour if needed
                    if start_time.hour < WorkdayConfig.WORK_START_HOUR:
                        start_time = start_time.replace(
                            hour=WorkdayConfig.WORK_START_HOUR,
                            minute=0
                        )

                # Calculate end time
                end_time = start_time + timedelta(hours=hours_to_add)

                # Add some realistic variation (±15 minutes)
                variation = random.randint(-15, 15)
                end_time += timedelta(minutes=variation)

                # Create work slot
                slot = WorkSlot(
                    start=start_time,
                    end=end_time,
                    department=department,
                    task_description="",
                    hours=hours_to_add,
                )
                day.slots.append(slot)
                day.total_hours += hours_to_add

                slots.append((start_time, end_time))
                remaining_hours -= hours_to_add

            # Move to next day
            current_date += timedelta(days=1)

        # Return overall start and end
        if slots:
            return slots[0][0], slots[-1][1]
        return after, after + timedelta(hours=hours_needed)

    def _add_handoff_gap(
        self,
        prev_end: datetime,
        min_gap_hours: float = None,
    ) -> datetime:
        """
        Add realistic gap between task handoffs.

        Args:
            prev_end: When the previous task ended
            min_gap_hours: Minimum gap (defaults to config)

        Returns:
            Start time for next task
        """
        if min_gap_hours is None:
            min_gap_hours = WorkdayConfig.MIN_TASK_GAP_HOURS

        # Add base gap
        next_start = prev_end + timedelta(hours=min_gap_hours)

        # Add some randomness (0-30 minutes)
        next_start += timedelta(minutes=random.randint(0, 30))

        # Ensure within business hours
        if next_start.hour >= WorkdayConfig.WORK_END_HOUR:
            # Move to next business day
            next_start += timedelta(days=1)
            next_start = next_start.replace(
                hour=WorkdayConfig.WORK_START_HOUR,
                minute=random.randint(0, 30)
            )

        # Skip weekends
        while next_start.weekday() >= 5:
            next_start += timedelta(days=1)

        return next_start

    def _create_internal_meeting(
        self,
        department: str,
        after: datetime,
        meeting_type: str = "sync",
    ) -> dict:
        """
        Create an internal meeting record.

        These represent Primo <-> Dev team interactions.
        """
        # Meetings typically happen at specific times
        meeting_hours = [9, 10, 14, 15, 16]
        meeting_hour = random.choice(meeting_hours)

        meeting_start = after.replace(
            hour=meeting_hour,
            minute=random.choice([0, 15, 30]),
            second=0,
            microsecond=0
        )

        # If meeting would be before 'after', move to next day
        if meeting_start <= after:
            meeting_start += timedelta(days=1)
            while meeting_start.weekday() >= 5:
                meeting_start += timedelta(days=1)

        duration_minutes = random.choice([15, 30, 30, 45])  # Weighted toward 30 min

        return {
            "id": f"meet-{uuid4().hex[:8]}",
            "type": meeting_type,
            "department": department,
            "start": meeting_start.isoformat(),
            "duration_minutes": duration_minutes,
            "description": f"Internal sync - {department}",
        }

    def normalize_project(
        self,
        project_id: str,
        project_name: str,
        tasks: List[dict],
    ) -> NormalizedTimeline:
        """
        Normalize a project's tasks into a realistic timeline.

        Args:
            project_id: Project identifier
            project_name: Project name
            tasks: List of tasks with keys:
                   - department: str
                   - description: str
                   - hours: float (raw hours from calculator)
                   - order: int (optional, execution order)

        Returns:
            Normalized timeline with realistic scheduling
        """
        # Sort tasks by order if provided
        sorted_tasks = sorted(tasks, key=lambda t: t.get("order", 0))

        timeline = NormalizedTimeline(
            project_id=project_id,
            project_name=project_name,
        )

        current_time = self.project_start
        prev_department = None

        for task_def in sorted_tasks:
            department = task_def["department"]
            raw_hours = task_def["hours"]
            description = task_def.get("description", "Development work")

            # Add handoff gap if switching departments
            if prev_department and prev_department != department:
                # Create internal meeting for handoff
                meeting = self._create_internal_meeting(
                    department=department,
                    after=current_time,
                    meeting_type="handoff",
                )
                timeline.internal_meetings.append(meeting)

                # Add handoff gap
                current_time = self._add_handoff_gap(current_time)

            # Find slot for this task
            start_time, end_time = self._find_next_available_slot(
                department=department,
                hours_needed=raw_hours,
                after=current_time,
            )

            # Create normalized task
            normalized_task = NormalizedTask(
                id=task_def.get("id", f"task-{uuid4().hex[:8]}"),
                department=department,
                description=description,
                raw_hours=raw_hours,
                normalized_hours=raw_hours,  # Hours stay the same, timeline expands
                start_time=start_time,
                end_time=end_time,
                status=TaskStatus.COMPLETED,
                includes_handoff=prev_department != department if prev_department else False,
            )

            timeline.tasks.append(normalized_task)
            timeline.total_raw_hours += raw_hours
            timeline.total_normalized_hours += raw_hours

            # Update tracking
            current_time = end_time
            prev_department = department

        # Set timeline bounds
        if timeline.tasks:
            timeline.start_date = timeline.tasks[0].start_time
            timeline.end_date = timeline.tasks[-1].end_time
            timeline.total_calendar_days = (
                timeline.end_date - timeline.start_date
            ).days + 1

        return timeline

    def get_activity_timeline(
        self,
        normalized_timeline: NormalizedTimeline,
        include_meetings: bool = True,
    ) -> List[dict]:
        """
        Generate activity feed from normalized timeline.

        This creates the data for the dashboard's activity timeline.
        """
        activities = []

        # Add task activities
        for task in normalized_timeline.tasks:
            # Task start activity
            activities.append({
                "id": f"act-start-{task.id}",
                "timestamp": task.start_time.isoformat(),
                "agent": self._department_to_agent(task.department),
                "action": "task_started",
                "description": f"Started: {task.description}",
                "category": self._department_to_category(task.department),
            })

            # Task completion activity
            activities.append({
                "id": f"act-end-{task.id}",
                "timestamp": task.end_time.isoformat(),
                "agent": self._department_to_agent(task.department),
                "action": "task_completed",
                "description": f"Completed: {task.description}",
                "category": self._department_to_category(task.department),
            })

        # Add meetings
        if include_meetings:
            for meeting in normalized_timeline.internal_meetings:
                activities.append({
                    "id": meeting["id"],
                    "timestamp": meeting["start"],
                    "agent": "Primo",
                    "action": "meeting",
                    "description": meeting["description"],
                    "category": "communication",
                })

        # Sort by timestamp
        activities.sort(key=lambda a: a["timestamp"])

        return activities

    def _department_to_agent(self, department: str) -> str:
        """Map department to agent name for display."""
        mapping = {
            "fronti_frontend": "Fronti",
            "baky_backend": "Baky",
            "devi_devops": "Devi",
            "qai_testing": "Qai",
            "secu_security": "Secu",
            "mark_documentation": "Mark",
        }
        return mapping.get(department, department.split("_")[0].title())

    def _department_to_category(self, department: str) -> str:
        """Map department to activity category."""
        mapping = {
            "fronti_frontend": "code",
            "baky_backend": "code",
            "devi_devops": "deployment",
            "qai_testing": "review",
            "secu_security": "security",
            "mark_documentation": "communication",
        }
        return mapping.get(department, "code")


# Convenience function
def normalize_timeline(
    project_id: str,
    project_name: str,
    tasks: List[dict],
    project_start: Optional[datetime] = None,
) -> dict:
    """
    Quick timeline normalization.

    Args:
        project_id: Project ID
        project_name: Project name
        tasks: List of task dicts with department, hours, description
        project_start: When project started

    Returns:
        Normalized timeline as dictionary
    """
    normalizer = TimelineNormalizer(project_start)
    timeline = normalizer.normalize_project(project_id, project_name, tasks)
    return timeline.to_dict()


if __name__ == "__main__":
    # Example usage
    from datetime import datetime

    # Simulate a project that would take 24 raw hours
    tasks = [
        {"department": "fronti_frontend", "hours": 8, "description": "Build UI components", "order": 1},
        {"department": "baky_backend", "hours": 10, "description": "API endpoints", "order": 2},
        {"department": "fronti_frontend", "hours": 4, "description": "Integration", "order": 3},
        {"department": "qai_testing", "hours": 2, "description": "Testing", "order": 4},
    ]

    # Start project 5 days ago
    start = datetime.utcnow() - timedelta(days=5)

    normalizer = TimelineNormalizer(project_start=start)
    timeline = normalizer.normalize_project(
        project_id="PROJ-001",
        project_name="Demo Dashboard",
        tasks=tasks,
    )

    print(f"Project: {timeline.project_name}")
    print(f"Total Hours: {timeline.total_normalized_hours}")
    print(f"Calendar Days: {timeline.total_calendar_days}")
    print(f"Start: {timeline.start_date}")
    print(f"End: {timeline.end_date}")
    print()
    print("Tasks:")
    for task in timeline.tasks:
        print(f"  - {task.department}: {task.description}")
        print(f"    {task.start_time} -> {task.end_time} ({task.normalized_hours}h)")
    print()
    print(f"Internal Meetings: {len(timeline.internal_meetings)}")
    for meeting in timeline.internal_meetings:
        print(f"  - {meeting['type']}: {meeting['description']} at {meeting['start']}")
