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
    preferred_time: str = ""
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
        if self.preferred_time and not self._valid_time(self.preferred_time):
            raise ValueError(
                f"preferred_time must be in HH:MM format, got '{self.preferred_time}'"
            )

    @staticmethod
    def _valid_time(t: str) -> bool:
        """Return True if *t* is a valid ``"HH:MM"`` string (00:00–23:59)."""
        parts = t.split(":")
        return (
            len(parts) == 2
            and parts[0].isdigit()
            and parts[1].isdigit()
            and 0 <= int(parts[0]) <= 23
            and 0 <= int(parts[1]) <= 59
        )

    def priority_value(self) -> int:
        """Return a numeric weight for sorting (higher = more important)."""
        return PRIORITY_MAP[self.priority]

    @property
    def is_recurring(self) -> bool:
        """True when the task repeats on a regular cadence (daily or weekly)."""
        return self.frequency in ("daily", "weekly")

    def next_occurrence(self) -> Task:
        """Return a fresh pending copy of this task for the next day/week."""
        return Task(
            title=self.title,
            description=self.description,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            category=self.category,
            frequency=self.frequency,
            preferred_time=self.preferred_time,
            completed=False,
        )

    def mark_complete(self) -> None:
        """Set this task's status to done."""
        self.completed = True

    def reset(self) -> None:
        """Set this task's status back to pending."""
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
        """Append *task* to this pet's task list.

        Raises ``ValueError`` if a task with the same title already exists.
        """
        if any(t.title == task.title for t in self.tasks):
            raise ValueError(f"Task '{task.title}' already exists for {self.name}")
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove the first task whose title matches *title*.

        Raises ``ValueError`` if no matching task is found.
        """
        for i, t in enumerate(self.tasks):
            if t.title == title:
                self.tasks.pop(i)
                return
        raise ValueError(f"No task titled '{title}' found for {self.name}")

    def complete_task(self, title: str) -> Task:
        """Mark a task complete. If it is recurring, replace it with a fresh
        pending copy so the next occurrence is automatically queued."""
        for i, t in enumerate(self.tasks):
            if t.title == title:
                t.mark_complete()
                if t.is_recurring:
                    self.tasks[i] = t.next_occurrence()
                return t
        raise ValueError(f"No task titled '{title}' found for {self.name}")

    def pending_tasks(self) -> list[Task]:
        """Return only incomplete tasks."""
        return [t for t in self.tasks if not t.completed]

    def tasks_by_category(self, category: str) -> list[Task]:
        """Return all tasks (pending or done) that belong to *category*."""
        return [t for t in self.tasks if t.category == category]

    def completion_summary(self) -> str:
        """Return a one-line string like ``"Mochi: 2/5 tasks complete"``."""
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
        """Register a new pet under this owner.

        Raises ``ValueError`` if a pet with the same name already exists.
        """
        if any(p.name == pet.name for p in self.pets):
            raise ValueError(f"A pet named '{pet.name}' already exists")
        self.pets.append(pet)

    def remove_pet(self, name: str) -> None:
        """Remove the pet whose name matches *name*.

        Raises ``ValueError`` if no matching pet is found.
        """
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
        """Calculate the minute this entry finishes (start + duration)."""
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
        self._last_warnings: list[str] = []

    # ----- task management helpers (delegates to pets) ---------------------

    def add_task(self, pet_name: str, task: Task) -> None:
        """Delegate task creation to the pet identified by *pet_name*."""
        pet = self._find_pet(pet_name)
        pet.add_task(task)

    def remove_task(self, pet_name: str, title: str) -> None:
        """Delegate task removal to the pet identified by *pet_name*."""
        pet = self._find_pet(pet_name)
        pet.remove_task(title)

    def get_all_pending(self) -> list[tuple[Pet, Task]]:
        """Return (pet, task) pairs for every incomplete task across all pets."""
        return [
            (pet, task)
            for pet in self.owner.pets
            for task in pet.pending_tasks()
        ]

    # ----- sorting helpers -------------------------------------------------

    def sort_by_time(self) -> list[tuple[Pet, Task]]:
        """Return all pending (pet, task) pairs sorted by preferred_time.

        Uses a lambda that splits the ``"HH:MM"`` string into an
        ``(int, int)`` tuple so that ``"08:30"`` sorts before ``"14:00"``.
        Tasks with no preferred_time are placed at the end.
        """
        pending = self.get_all_pending()
        pending.sort(
            key=lambda pair: (
                pair[1].preferred_time == "",
                tuple(int(p) for p in pair[1].preferred_time.split(":"))
                if pair[1].preferred_time
                else (24, 0),
            )
        )
        return pending

    # ----- conflict detection ---------------------------------------------

    @staticmethod
    def _time_to_minutes(t: str) -> int:
        """Convert ``"HH:MM"`` to minutes since midnight."""
        h, m = t.split(":")
        return int(h) * 60 + int(m)

    def detect_conflicts(self) -> list[str]:
        """Return human-readable warnings for any overlapping preferred times.

        Two tasks conflict when their preferred-time windows overlap:
        task A runs [startA, startA + durationA) and task B runs
        [startB, startB + durationB).  Only tasks that have a
        ``preferred_time`` set are checked.
        """
        timed: list[tuple[Pet, Task]] = [
            (pet, task)
            for pet, task in self.get_all_pending()
            if task.preferred_time
        ]

        warnings: list[str] = []
        for i in range(len(timed)):
            pet_a, task_a = timed[i]
            start_a = self._time_to_minutes(task_a.preferred_time)
            end_a = start_a + task_a.duration_minutes

            for j in range(i + 1, len(timed)):
                pet_b, task_b = timed[j]
                start_b = self._time_to_minutes(task_b.preferred_time)
                end_b = start_b + task_b.duration_minutes

                if start_a < end_b and start_b < end_a:
                    warnings.append(
                        f"⚠  Conflict: [{pet_a.name}] {task_a.title} "
                        f"({task_a.preferred_time}–{end_a // 60:02d}:{end_a % 60:02d}) "
                        f"overlaps with [{pet_b.name}] {task_b.title} "
                        f"({task_b.preferred_time}–{end_b // 60:02d}:{end_b % 60:02d})"
                    )

        return warnings

    # ----- scheduling algorithm -------------------------------------------

    def generate_schedule(self) -> list[ScheduleEntry]:
        """Build a daily schedule that fits within the owner's available time.

        Strategy:
        1. Collect all pending tasks across every pet.
        2. Sort by preferred_time first (tasks with a time come before
           those without), then by priority (high first), then by
           duration (shorter first) to fill gaps.
        3. Greedily pack tasks into the available time budget.
        """
        pending = self.get_all_pending()

        pending.sort(
            key=lambda pair: (
                pair[1].preferred_time == "",
                tuple(int(p) for p in pair[1].preferred_time.split(":"))
                if pair[1].preferred_time
                else (24, 0),
                -pair[1].priority_value(),
                pair[1].duration_minutes,
            )
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
        self._last_warnings = self.detect_conflicts()
        return entries

    def mark_scheduled_complete(self) -> None:
        """Mark every task in the last generated schedule as complete.

        For recurring tasks (daily/weekly) the pet automatically replaces
        the completed task with a fresh pending copy for the next occurrence.
        """
        for entry in self._last_schedule:
            pet = self._find_pet(entry.pet_name)
            pet.complete_task(entry.task.title)

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

        if self._last_warnings:
            lines.append("")
            lines.append("Preferred-time conflicts detected:")
            for w in self._last_warnings:
                lines.append(f"  {w}")

        skipped = self._skipped_tasks(target)
        if skipped:
            lines.append("")
            lines.append("Skipped (not enough time):")
            for pet, task in skipped:
                lines.append(f"  ✗ [{pet.name}] {task}")

        return "\n".join(lines)

    # ----- private helpers ------------------------------------------------

    def _find_pet(self, pet_name: str) -> Pet:
        """Look up a pet by name within the owner's pet list.

        Raises ``ValueError`` if no pet with that name exists.
        """
        for p in self.owner.pets:
            if p.name == pet_name:
                return p
        raise ValueError(f"No pet named '{pet_name}' found")

    def _build_reason(self, task: Task, scheduled: list[ScheduleEntry]) -> str:
        """Construct a short human-readable string explaining why *task* was
        placed at its position in the schedule.

        High-priority tasks are labelled as such; the very first entry is
        noted as "scheduled first"; everything else gets a generic message.
        """
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
        """Return ``(pet, task)`` pairs for pending tasks that did not make
        it into *entries*, typically because the owner's time budget ran out.
        """
        scheduled_titles = {e.task.title for e in entries}
        return [
            (pet, task)
            for pet in self.owner.pets
            for task in pet.pending_tasks()
            if task.title not in scheduled_titles
        ]
