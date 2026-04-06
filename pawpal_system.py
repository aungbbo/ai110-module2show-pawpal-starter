from __future__ import annotations

from dataclasses import dataclass, field

VALID_PRIORITIES = {"high", "medium", "low"}
PRIORITY_MAP = {"high": 3, "medium": 2, "low": 1}
VALID_FREQUENCIES = {"daily", "weekly", "as_needed"}


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """A single pet-care activity."""

    title: str
    description: str
    duration_minutes: int
    priority: str = "medium"
    category: str = ""
    frequency: str = "daily"
    completed: bool = False

    def __post_init__(self) -> None:
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(
                f"priority must be one of {VALID_PRIORITIES}, got '{self.priority}'"
            )
        if self.frequency not in VALID_FREQUENCIES:
            raise ValueError(
                f"frequency must be one of {VALID_FREQUENCIES}, got '{self.frequency}'"
            )

    def priority_value(self) -> int:
        """Return a numeric weight for sorting (higher = more important)."""
        return PRIORITY_MAP[self.priority]

    def mark_complete(self) -> None:
        self.completed = True

    def reset(self) -> None:
        self.completed = False

    def __str__(self) -> str:
        status = "done" if self.completed else "pending"
        return f"{self.title} ({self.duration_minutes} min, {self.priority}, {status})"


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    """A pet with its own roster of care tasks."""

    name: str
    species: str
    special_needs: str = ""
    tasks: list[Task] = field(default_factory=list, repr=False)

    def add_task(self, task: Task) -> None:
        if any(t.title == task.title for t in self.tasks):
            raise ValueError(f"Task '{task.title}' already exists for {self.name}")
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        for i, t in enumerate(self.tasks):
            if t.title == title:
                self.tasks.pop(i)
                return
        raise ValueError(f"No task titled '{title}' found for {self.name}")

    def pending_tasks(self) -> list[Task]:
        """Return only incomplete tasks."""
        return [t for t in self.tasks if not t.completed]

    def tasks_by_category(self, category: str) -> list[Task]:
        return [t for t in self.tasks if t.category == category]

    def completion_summary(self) -> str:
        total = len(self.tasks)
        done = sum(1 for t in self.tasks if t.completed)
        return f"{self.name}: {done}/{total} tasks complete"

    def reset_all_tasks(self) -> None:
        """Mark every task as incomplete (useful at the start of a new day)."""
        for t in self.tasks:
            t.reset()

    def __str__(self) -> str:
        return f"{self.name} ({self.species})"


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    """A pet owner who may have multiple pets."""

    name: str
    available_minutes: int
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        if self.available_minutes < 0:
            raise ValueError("available_minutes cannot be negative")

    def add_pet(self, pet: Pet) -> None:
        if any(p.name == pet.name for p in self.pets):
            raise ValueError(f"A pet named '{pet.name}' already exists")
        self.pets.append(pet)

    def remove_pet(self, name: str) -> None:
        for i, p in enumerate(self.pets):
            if p.name == name:
                self.pets.pop(i)
                return
        raise ValueError(f"No pet named '{name}' found")

    def all_tasks(self) -> list[Task]:
        """Aggregate every task across all pets."""
        return [task for pet in self.pets for task in pet.tasks]

    def all_pending_tasks(self) -> list[Task]:
        """Aggregate only incomplete tasks across all pets."""
        return [task for pet in self.pets for task in pet.pending_tasks()]

    def __str__(self) -> str:
        return f"{self.name} ({self.available_minutes} min available)"


# ---------------------------------------------------------------------------
# ScheduleEntry
# ---------------------------------------------------------------------------

@dataclass
class ScheduleEntry:
    """One slot in a generated daily plan."""

    task: Task
    pet_name: str
    start_minute: int
    reason: str = ""

    def end_minute(self) -> int:
        return self.start_minute + self.task.duration_minutes

    def __str__(self) -> str:
        return (
            f"{self.start_minute}–{self.end_minute()} min: "
            f"[{self.pet_name}] {self.task.title} — {self.reason}"
        )


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """The brain: retrieves, organises, and schedules tasks across all pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner
        self._last_schedule: list[ScheduleEntry] = []

    # ----- task management helpers (delegates to pets) ---------------------

    def add_task(self, pet_name: str, task: Task) -> None:
        pet = self._find_pet(pet_name)
        pet.add_task(task)

    def remove_task(self, pet_name: str, title: str) -> None:
        pet = self._find_pet(pet_name)
        pet.remove_task(title)

    def get_all_pending(self) -> list[tuple[Pet, Task]]:
        """Return (pet, task) pairs for every incomplete task across all pets."""
        return [
            (pet, task)
            for pet in self.owner.pets
            for task in pet.pending_tasks()
        ]

    # ----- scheduling algorithm -------------------------------------------

    def generate_schedule(self) -> list[ScheduleEntry]:
        """Build a daily schedule that fits within the owner's available time.

        Strategy:
        1. Collect all pending tasks across every pet.
        2. Sort by priority (high first), then by duration (shorter first)
           so high-priority items run first and shorter tasks fill gaps.
        3. Greedily pack tasks into the available time budget.
        """
        pending = self.get_all_pending()

        pending.sort(
            key=lambda pair: (-pair[1].priority_value(), pair[1].duration_minutes)
        )

        entries: list[ScheduleEntry] = []
        current_minute = 0
        budget = self.owner.available_minutes

        for pet, task in pending:
            if current_minute + task.duration_minutes > budget:
                continue
            reason = self._build_reason(task, entries)
            entry = ScheduleEntry(
                task=task,
                pet_name=pet.name,
                start_minute=current_minute,
                reason=reason,
            )
            entries.append(entry)
            current_minute += task.duration_minutes

        self._last_schedule = entries
        return entries

    def mark_scheduled_complete(self) -> None:
        """Mark every task in the last generated schedule as complete."""
        for entry in self._last_schedule:
            entry.task.mark_complete()

    # ----- explanation ----------------------------------------------------

    def explain_schedule(self, entries: list[ScheduleEntry] | None = None) -> str:
        target = entries if entries is not None else self._last_schedule
        if not target:
            return "No tasks were scheduled."

        total_min = sum(e.task.duration_minutes for e in target)
        lines = [
            f"Daily plan for {self.owner.name}'s pets "
            f"({len(target)} tasks, {total_min}/{self.owner.available_minutes} min used):",
        ]
        for entry in target:
            lines.append(f"  • {entry}")

        skipped = self._skipped_tasks(target)
        if skipped:
            lines.append("")
            lines.append("Skipped (not enough time):")
            for pet, task in skipped:
                lines.append(f"  ✗ [{pet.name}] {task}")

        return "\n".join(lines)

    # ----- private helpers ------------------------------------------------

    def _find_pet(self, pet_name: str) -> Pet:
        for p in self.owner.pets:
            if p.name == pet_name:
                return p
        raise ValueError(f"No pet named '{pet_name}' found")

    def _build_reason(self, task: Task, scheduled: list[ScheduleEntry]) -> str:
        parts: list[str] = []
        if task.priority == "high":
            parts.append("high priority")
        elif task.priority == "low":
            parts.append("low priority — fits remaining time")
        if not scheduled:
            parts.append("scheduled first")
        return "; ".join(parts) if parts else "fits in remaining time"

    def _skipped_tasks(
        self, entries: list[ScheduleEntry]
    ) -> list[tuple[Pet, Task]]:
        scheduled_titles = {e.task.title for e in entries}
        return [
            (pet, task)
            for pet in self.owner.pets
            for task in pet.pending_tasks()
            if task.title not in scheduled_titles
        ]
