from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        return f"{self.name} ({self.available_minutes} min available)"


@dataclass
class Pet:
    name: str
    species: str
    owner: Owner
    special_needs: str = ""

    def __str__(self) -> str:
        return f"{self.name} ({self.species})"


PRIORITY_MAP = {"high": 3, "medium": 2, "low": 1}


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str = "medium"
    category: str = ""

    def priority_value(self) -> int:
        """Return a numeric weight for sorting (higher = more important)."""
        return PRIORITY_MAP.get(self.priority, 0)

    def __str__(self) -> str:
        return f"{self.title} ({self.duration_minutes} min, {self.priority})"


@dataclass
class ScheduleEntry:
    task: Task
    start_minute: int
    reason: str = ""

    def end_minute(self) -> int:
        """Return the minute at which this entry finishes."""
        return self.start_minute + self.task.duration_minutes

    def __str__(self) -> str:
        return (
            f"{self.start_minute}–{self.end_minute()} min: "
            f"{self.task.title} — {self.reason}"
        )


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, owner: Owner, pet: Pet, tasks: list[Task] | None = None):
        self.owner = owner
        self.pet = pet
        self.tasks: list[Task] = tasks if tasks is not None else []

    def add_task(self, task: Task) -> None:
        """Append a task to the task list."""
        pass

    def remove_task(self, title: str) -> None:
        """Remove the first task matching *title*."""
        pass

    def generate_schedule(self) -> list[ScheduleEntry]:
        """Build a daily schedule that fits within the owner's available time."""
        pass

    def _fits_in_time(self, entries: list[ScheduleEntry], task: Task) -> bool:
        """Return True if *task* can still fit given already-scheduled entries."""
        pass

    def explain_schedule(self, entries: list[ScheduleEntry]) -> str:
        """Return a human-readable explanation of the generated schedule."""
        pass
