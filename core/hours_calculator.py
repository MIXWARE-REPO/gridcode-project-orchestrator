"""
Hours Calculator Module - GriPro

Calculates work hours based on lines of code and specialization level.
Based on industry-standard software productivity metrics.

References:
- Brooks, F.P. (1975). "The Mythical Man-Month"
- Jones, C. (2008). "Applied Software Measurement"
- McConnell, S. (2004). "Code Complete"
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import uuid4


class SpecializationLevel(Enum):
    """
    Specialization levels with their LOC ratios.

    Level 1: Generic departments - 2h per 50 LOC
    Level 2: Department specialists - 2h per 30 LOC
    Level 3: Sub-specialists - 2h per 20 LOC
    """
    LEVEL_1 = 1  # Generic: 50 LOC per 2h
    LEVEL_2 = 2  # Specialist: 30 LOC per 2h
    LEVEL_3 = 3  # Sub-specialist: 20 LOC per 2h


class TaskComplexity(Enum):
    """Task complexity for meeting time calculation."""
    SIMPLE = "simple"      # < 50 LOC, 1 file
    MEDIUM = "medium"      # 50-200 LOC, 2-5 files
    COMPLEX = "complex"    # > 200 LOC, > 5 files


class DeliveryType(Enum):
    """Delivery type for review time calculation."""
    PARTIAL = "partial"    # Incomplete feature
    COMPLETE = "complete"  # Complete feature
    FINAL = "final"        # Complete module


# LOC thresholds per level (lines per 2 hours)
LOC_RATIOS: Dict[SpecializationLevel, int] = {
    SpecializationLevel.LEVEL_1: 50,  # 2h per 50 LOC
    SpecializationLevel.LEVEL_2: 30,  # 2h per 30 LOC
    SpecializationLevel.LEVEL_3: 20,  # 2h per 20 LOC
}

# Meeting hours by complexity
MEETING_HOURS: Dict[TaskComplexity, float] = {
    TaskComplexity.SIMPLE: 1.0,
    TaskComplexity.MEDIUM: 1.5,
    TaskComplexity.COMPLEX: 2.0,
}

# Review hours by delivery type
REVIEW_HOURS: Dict[DeliveryType, float] = {
    DeliveryType.PARTIAL: 0.5,
    DeliveryType.COMPLETE: 1.0,
    DeliveryType.FINAL: 1.5,
}


@dataclass
class ResourceDefinition:
    """Definition of a team resource (agent/specialist)."""
    id: str
    name: str
    alias: str
    level: SpecializationLevel
    parent_id: Optional[str] = None
    description: str = ""
    skills: List[str] = field(default_factory=list)


@dataclass
class TaskAssignment:
    """Assignment of a task to a resource."""
    task_id: str
    resource_id: str
    specialist_id: Optional[str] = None
    sub_specialist_id: Optional[str] = None

    @property
    def effective_level(self) -> SpecializationLevel:
        """Get the effective specialization level for this assignment."""
        if self.sub_specialist_id:
            return SpecializationLevel.LEVEL_3
        elif self.specialist_id:
            return SpecializationLevel.LEVEL_2
        return SpecializationLevel.LEVEL_1


@dataclass
class HoursEstimate:
    """Detailed hours estimate for a task."""
    task_id: str
    loc_estimated: int
    level: SpecializationLevel
    complexity: TaskComplexity
    delivery_type: DeliveryType

    # Calculated hours
    meeting_hours: float = 0.0
    development_hours: float = 0.0
    review_hours: float = 0.0

    # Metadata
    calculated_at: datetime = field(default_factory=datetime.utcnow)
    notes: str = ""

    @property
    def total_hours(self) -> float:
        """Total hours for this task."""
        return self.meeting_hours + self.development_hours + self.review_hours

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "task_id": self.task_id,
            "loc_estimated": self.loc_estimated,
            "level": self.level.value,
            "complexity": self.complexity.value,
            "delivery_type": self.delivery_type.value,
            "hours": {
                "meeting": self.meeting_hours,
                "development": self.development_hours,
                "review": self.review_hours,
                "total": self.total_hours,
            },
            "calculated_at": self.calculated_at.isoformat(),
            "notes": self.notes,
        }


@dataclass
class ProjectEstimate:
    """Complete hours estimate for a project."""
    project_id: str
    project_name: str
    tasks: List[HoursEstimate] = field(default_factory=list)

    # Aggregated data
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = "primo"

    @property
    def total_hours(self) -> float:
        """Total hours for entire project."""
        return sum(task.total_hours for task in self.tasks)

    @property
    def hours_by_category(self) -> Dict[str, float]:
        """Hours breakdown by category."""
        return {
            "meeting": sum(t.meeting_hours for t in self.tasks),
            "development": sum(t.development_hours for t in self.tasks),
            "review": sum(t.review_hours for t in self.tasks),
        }

    @property
    def hours_by_level(self) -> Dict[str, float]:
        """Hours breakdown by specialization level."""
        result = {f"level_{i}": 0.0 for i in range(1, 4)}
        for task in self.tasks:
            key = f"level_{task.level.value}"
            result[key] += task.development_hours
        return result

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "project_id": self.project_id,
            "project_name": self.project_name,
            "summary": {
                "total_hours": self.total_hours,
                "by_category": self.hours_by_category,
                "by_level": self.hours_by_level,
                "task_count": len(self.tasks),
            },
            "tasks": [t.to_dict() for t in self.tasks],
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
        }


class HoursCalculator:
    """
    Calculator for work hours based on LOC and specialization.

    Based on industry metrics:
    - ~10 LOC/day for experienced developers (Brooks, 1975)
    - 8-16 LOC/day for reliable embedded software (Jones, 2008)
    - 20-100 LOC/day useful code, avg ~40-60 (practical experience)
    - 4 hours of pure coding in an 8-hour workday

    GriPro ratios:
    - Level 1 (Generic): 2h per 50 LOC (25 LOC/h)
    - Level 2 (Specialist): 2h per 30 LOC (15 LOC/h)
    - Level 3 (Sub-specialist): 2h per 20 LOC (10 LOC/h)
    """

    def __init__(self):
        self._resource_library: Dict[str, ResourceDefinition] = {}
        self._load_default_resources()

    def _load_default_resources(self) -> None:
        """Load default resource definitions."""
        # Level 1 - Generic Departments
        level_1_resources = [
            ("fronti_frontend", "Frontend Development", "Fronti", "UI development, React/Vue/Angular"),
            ("baky_backend", "Backend Development", "Baky", "APIs, server logic, databases"),
            ("devi_devops", "DevOps & Infrastructure", "Devi", "CI/CD, deployment, infrastructure"),
            ("qai_testing", "Quality Assurance", "Qai", "Testing, QA processes"),
            ("secu_security", "Security & Compliance", "Secu", "Security audits, compliance"),
            ("mark_marketing", "Documentation", "Mark", "Technical docs, marketing"),
        ]

        for res_id, name, alias, desc in level_1_resources:
            self._resource_library[res_id] = ResourceDefinition(
                id=res_id,
                name=name,
                alias=alias,
                level=SpecializationLevel.LEVEL_1,
                description=desc,
            )

        # Level 2 - Specialists
        level_2_resources = [
            ("ux_designer", "UX Designer", "UX", "fronti_frontend", "User experience design"),
            ("ui_designer", "UI Designer", "UI", "fronti_frontend", "Visual interface design"),
            ("api_architect", "API Architect", "API", "baky_backend", "API design and architecture"),
            ("database_engineer", "Database Engineer", "DB", "baky_backend", "Database optimization"),
            ("security_auditor", "Security Auditor", "SecAudit", "secu_security", "Security audits"),
            ("performance_engineer", "Performance Engineer", "Perf", "devi_devops", "Performance optimization"),
            ("test_automation", "Test Automation", "AutoTest", "qai_testing", "Automated testing"),
        ]

        for res_id, name, alias, parent, desc in level_2_resources:
            self._resource_library[res_id] = ResourceDefinition(
                id=res_id,
                name=name,
                alias=alias,
                level=SpecializationLevel.LEVEL_2,
                parent_id=parent,
                description=desc,
            )

        # Level 3 - Sub-specialists
        level_3_resources = [
            ("seo_specialist", "SEO Specialist", "SEO", "ux_designer", "Search engine optimization"),
            ("accessibility_expert", "Accessibility Expert", "A11y", "ux_designer", "WCAG compliance"),
            ("animation_expert", "Animation Expert", "Anim", "ui_designer", "Complex animations"),
            ("graphql_specialist", "GraphQL Specialist", "GQL", "api_architect", "GraphQL APIs"),
            ("realtime_specialist", "Real-time Specialist", "RT", "baky_backend", "WebSockets, events"),
            ("pentest_expert", "Penetration Tester", "PenTest", "security_auditor", "Security testing"),
            ("mobile_performance", "Mobile Performance", "MobPerf", "performance_engineer", "Mobile optimization"),
        ]

        for res_id, name, alias, parent, desc in level_3_resources:
            self._resource_library[res_id] = ResourceDefinition(
                id=res_id,
                name=name,
                alias=alias,
                level=SpecializationLevel.LEVEL_3,
                parent_id=parent,
                description=desc,
            )

    def get_resource(self, resource_id: str) -> Optional[ResourceDefinition]:
        """Get a resource definition by ID."""
        return self._resource_library.get(resource_id)

    def get_resources_by_level(self, level: SpecializationLevel) -> List[ResourceDefinition]:
        """Get all resources at a specific level."""
        return [r for r in self._resource_library.values() if r.level == level]

    def get_specialists_for_department(self, department_id: str) -> List[ResourceDefinition]:
        """Get Level 2 specialists for a Level 1 department."""
        return [
            r for r in self._resource_library.values()
            if r.level == SpecializationLevel.LEVEL_2 and r.parent_id == department_id
        ]

    def get_sub_specialists_for_specialist(self, specialist_id: str) -> List[ResourceDefinition]:
        """Get Level 3 sub-specialists for a Level 2 specialist."""
        return [
            r for r in self._resource_library.values()
            if r.level == SpecializationLevel.LEVEL_3 and r.parent_id == specialist_id
        ]

    def calculate_development_hours(
        self,
        loc: int,
        level: SpecializationLevel,
    ) -> float:
        """
        Calculate development hours based on LOC and level.

        Formula: ceil(LOC / ratio) * 2 hours

        Args:
            loc: Lines of code estimated
            level: Specialization level

        Returns:
            Development hours
        """
        ratio = LOC_RATIOS[level]
        blocks = math.ceil(loc / ratio)
        return blocks * 2.0

    def determine_complexity(
        self,
        loc: int,
        file_count: int = 1,
    ) -> TaskComplexity:
        """
        Determine task complexity based on LOC and file count.

        Args:
            loc: Lines of code
            file_count: Number of files affected

        Returns:
            Task complexity level
        """
        if loc < 50 and file_count <= 1:
            return TaskComplexity.SIMPLE
        elif loc <= 200 and file_count <= 5:
            return TaskComplexity.MEDIUM
        else:
            return TaskComplexity.COMPLEX

    def calculate_task_hours(
        self,
        task_id: str,
        loc: int,
        level: SpecializationLevel,
        complexity: Optional[TaskComplexity] = None,
        delivery_type: DeliveryType = DeliveryType.COMPLETE,
        file_count: int = 1,
        notes: str = "",
    ) -> HoursEstimate:
        """
        Calculate complete hours estimate for a task.

        Args:
            task_id: Unique task identifier
            loc: Estimated lines of code
            level: Specialization level
            complexity: Task complexity (auto-determined if None)
            delivery_type: Type of delivery
            file_count: Number of files (for auto complexity)
            notes: Additional notes

        Returns:
            Complete hours estimate
        """
        if complexity is None:
            complexity = self.determine_complexity(loc, file_count)

        estimate = HoursEstimate(
            task_id=task_id,
            loc_estimated=loc,
            level=level,
            complexity=complexity,
            delivery_type=delivery_type,
            notes=notes,
        )

        # Calculate each component
        estimate.meeting_hours = MEETING_HOURS[complexity]
        estimate.development_hours = self.calculate_development_hours(loc, level)
        estimate.review_hours = REVIEW_HOURS[delivery_type]

        return estimate

    def estimate_project(
        self,
        project_id: str,
        project_name: str,
        tasks: List[dict],
    ) -> ProjectEstimate:
        """
        Generate complete project estimate.

        Args:
            project_id: Project identifier
            project_name: Project name
            tasks: List of task definitions with keys:
                   - task_id, loc, level (1-3), complexity?, delivery_type?

        Returns:
            Complete project estimate
        """
        project = ProjectEstimate(
            project_id=project_id,
            project_name=project_name,
        )

        for task_def in tasks:
            level = SpecializationLevel(task_def.get("level", 1))

            estimate = self.calculate_task_hours(
                task_id=task_def.get("task_id", str(uuid4())[:8]),
                loc=task_def.get("loc", 50),
                level=level,
                complexity=TaskComplexity(task_def["complexity"]) if "complexity" in task_def else None,
                delivery_type=DeliveryType(task_def.get("delivery_type", "complete")),
                file_count=task_def.get("file_count", 1),
                notes=task_def.get("notes", ""),
            )

            project.tasks.append(estimate)

        return project

    def format_estimate_summary(self, estimate: ProjectEstimate) -> str:
        """
        Format a project estimate as human-readable summary.

        Args:
            estimate: Project estimate

        Returns:
            Formatted string summary
        """
        by_cat = estimate.hours_by_category
        by_level = estimate.hours_by_level

        summary = f"""
Estimacion de Horas - {estimate.project_name}
{'=' * 50}

RESUMEN TOTAL: {estimate.total_hours:.1f} horas

Por Categoria:
  - Reuniones de traspaso: {by_cat['meeting']:.1f}h
  - Desarrollo: {by_cat['development']:.1f}h
  - Review de entregas: {by_cat['review']:.1f}h

Por Nivel de Especializacion:
  - Nivel 1 (Departamentos): {by_level['level_1']:.1f}h
  - Nivel 2 (Especialistas): {by_level['level_2']:.1f}h
  - Nivel 3 (Sub-especialistas): {by_level['level_3']:.1f}h

Tareas: {len(estimate.tasks)}
{'=' * 50}
"""
        return summary.strip()


# Singleton instance for easy access
_calculator: Optional[HoursCalculator] = None


def get_hours_calculator() -> HoursCalculator:
    """Get the singleton HoursCalculator instance."""
    global _calculator
    if _calculator is None:
        _calculator = HoursCalculator()
    return _calculator


# Convenience functions
def calculate_hours(
    loc: int,
    level: int = 1,
    complexity: str = "medium",
    delivery: str = "complete",
) -> dict:
    """
    Quick hours calculation.

    Args:
        loc: Lines of code
        level: 1, 2, or 3
        complexity: "simple", "medium", or "complex"
        delivery: "partial", "complete", or "final"

    Returns:
        Dictionary with hours breakdown
    """
    calc = get_hours_calculator()
    estimate = calc.calculate_task_hours(
        task_id="quick",
        loc=loc,
        level=SpecializationLevel(level),
        complexity=TaskComplexity(complexity),
        delivery_type=DeliveryType(delivery),
    )
    return estimate.to_dict()["hours"]


if __name__ == "__main__":
    # Example usage
    calc = get_hours_calculator()

    # Single task example
    task = calc.calculate_task_hours(
        task_id="TASK-001",
        loc=85,
        level=SpecializationLevel.LEVEL_3,
        complexity=TaskComplexity.MEDIUM,
        delivery_type=DeliveryType.COMPLETE,
        notes="Animation component for dashboard",
    )

    print(f"Task: {task.task_id}")
    print(f"LOC: {task.loc_estimated}")
    print(f"Level: {task.level.value}")
    print(f"Meeting: {task.meeting_hours}h")
    print(f"Development: {task.development_hours}h")
    print(f"Review: {task.review_hours}h")
    print(f"TOTAL: {task.total_hours}h")
    print()

    # Project example
    project = calc.estimate_project(
        project_id="PROJ-001",
        project_name="E-Commerce Dashboard",
        tasks=[
            {"task_id": "T1", "loc": 200, "level": 1, "notes": "Basic UI components"},
            {"task_id": "T2", "loc": 150, "level": 2, "notes": "UX improvements"},
            {"task_id": "T3", "loc": 80, "level": 3, "notes": "SEO optimization"},
            {"task_id": "T4", "loc": 300, "level": 1, "notes": "API endpoints"},
        ],
    )

    print(calc.format_estimate_summary(project))
