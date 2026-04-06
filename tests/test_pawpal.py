import pytest

from pawpal_system import Task, Pet, Owner, Scheduler


# ---------------------------------------------------------------------------
# Task Completion
# ---------------------------------------------------------------------------

class TestTaskCompletion:
    def test_new_task_is_not_completed(self):
        task = Task(title="Walk", description="Morning walk", duration_minutes=30)
        assert task.completed is False

    def test_mark_complete_changes_status(self):
        task = Task(title="Walk", description="Morning walk", duration_minutes=30)
        task.mark_complete()
        assert task.completed is True

    def test_reset_reverts_completed_status(self):
        task = Task(title="Walk", description="Morning walk", duration_minutes=30)
        task.mark_complete()
        task.reset()
        assert task.completed is False

    def test_mark_complete_is_idempotent(self):
        task = Task(title="Walk", description="Morning walk", duration_minutes=30)
        task.mark_complete()
        task.mark_complete()
        assert task.completed is True


# ---------------------------------------------------------------------------
# Task Addition to Pet
# ---------------------------------------------------------------------------

class TestPetTaskAddition:
    def test_adding_task_increases_count(self):
        pet = Pet(name="Mochi", species="dog")
        assert len(pet.tasks) == 0
        pet.add_task(Task(title="Walk", description="Morning walk", duration_minutes=30))
        assert len(pet.tasks) == 1

    def test_adding_multiple_tasks_increases_count(self):
        pet = Pet(name="Mochi", species="dog")
        pet.add_task(Task(title="Walk", description="Morning walk", duration_minutes=30))
        pet.add_task(Task(title="Feed", description="Breakfast", duration_minutes=10))
        pet.add_task(Task(title="Brush", description="Coat brushing", duration_minutes=15))
        assert len(pet.tasks) == 3

    def test_duplicate_task_title_raises_error(self):
        pet = Pet(name="Mochi", species="dog")
        pet.add_task(Task(title="Walk", description="Morning walk", duration_minutes=30))
        with pytest.raises(ValueError, match="already exists"):
            pet.add_task(Task(title="Walk", description="Evening walk", duration_minutes=20))

    def test_duplicate_rejection_does_not_change_count(self):
        pet = Pet(name="Mochi", species="dog")
        pet.add_task(Task(title="Walk", description="Morning walk", duration_minutes=30))
        with pytest.raises(ValueError):
            pet.add_task(Task(title="Walk", description="Evening walk", duration_minutes=20))
        assert len(pet.tasks) == 1


# ---------------------------------------------------------------------------
# Helper to build a quick scheduler
# ---------------------------------------------------------------------------

def _make_scheduler(minutes: int = 120) -> tuple[Owner, Pet, Pet, Scheduler]:
    """Return (owner, pet_a, pet_b, scheduler) wired together."""
    owner = Owner(name="Jordan", available_minutes=minutes)
    pet_a = Pet(name="Mochi", species="dog")
    pet_b = Pet(name="Whiskers", species="cat")
    owner.add_pet(pet_a)
    owner.add_pet(pet_b)
    return owner, pet_a, pet_b, Scheduler(owner)


# ---------------------------------------------------------------------------
# Sorting Correctness
# ---------------------------------------------------------------------------

class TestSortByTime:
    def test_tasks_returned_in_chronological_order(self):
        _, mochi, whiskers, scheduler = _make_scheduler()
        mochi.add_task(Task(
            title="Evening play", description="", duration_minutes=15,
            preferred_time="18:00",
        ))
        whiskers.add_task(Task(
            title="Morning feed", description="", duration_minutes=5,
            preferred_time="06:30",
        ))
        mochi.add_task(Task(
            title="Midday walk", description="", duration_minutes=20,
            preferred_time="12:00",
        ))

        sorted_tasks = scheduler.sort_by_time()
        times = [t.preferred_time for _, t in sorted_tasks]
        assert times == ["06:30", "12:00", "18:00"]

    def test_untimed_tasks_come_after_timed(self):
        _, mochi, _, scheduler = _make_scheduler()
        mochi.add_task(Task(
            title="No time task", description="", duration_minutes=10,
        ))
        mochi.add_task(Task(
            title="Timed task", description="", duration_minutes=10,
            preferred_time="09:00",
        ))

        sorted_tasks = scheduler.sort_by_time()
        titles = [t.title for _, t in sorted_tasks]
        assert titles == ["Timed task", "No time task"]

    def test_same_time_is_stable(self):
        _, mochi, whiskers, scheduler = _make_scheduler()
        mochi.add_task(Task(
            title="Task A", description="", duration_minutes=10,
            preferred_time="07:00",
        ))
        whiskers.add_task(Task(
            title="Task B", description="", duration_minutes=10,
            preferred_time="07:00",
        ))

        sorted_tasks = scheduler.sort_by_time()
        times = [t.preferred_time for _, t in sorted_tasks]
        assert times == ["07:00", "07:00"]

    def test_schedule_orders_by_time_then_priority(self):
        _, mochi, whiskers, scheduler = _make_scheduler()
        mochi.add_task(Task(
            title="Low @ 07:00", description="", duration_minutes=10,
            priority="low", preferred_time="07:00",
        ))
        whiskers.add_task(Task(
            title="High @ 08:00", description="", duration_minutes=10,
            priority="high", preferred_time="08:00",
        ))
        mochi.add_task(Task(
            title="High no time", description="", duration_minutes=10,
            priority="high",
        ))

        schedule = scheduler.generate_schedule()
        titles = [e.task.title for e in schedule]
        assert titles == ["Low @ 07:00", "High @ 08:00", "High no time"]


# ---------------------------------------------------------------------------
# Recurrence Logic
# ---------------------------------------------------------------------------

class TestRecurrence:
    def test_daily_task_renews_after_completion(self):
        pet = Pet(name="Mochi", species="dog")
        pet.add_task(Task(
            title="Walk", description="Morning walk", duration_minutes=30,
            frequency="daily",
        ))

        pet.complete_task("Walk")
        assert len(pet.tasks) == 1
        assert pet.tasks[0].completed is False

    def test_weekly_task_renews_after_completion(self):
        pet = Pet(name="Mochi", species="dog")
        pet.add_task(Task(
            title="Bath", description="Weekly bath", duration_minutes=45,
            frequency="weekly",
        ))

        pet.complete_task("Bath")
        assert len(pet.tasks) == 1
        assert pet.tasks[0].completed is False

    def test_as_needed_task_stays_done(self):
        pet = Pet(name="Mochi", species="dog")
        pet.add_task(Task(
            title="Nail trim", description="Trim nails", duration_minutes=15,
            frequency="as_needed",
        ))

        pet.complete_task("Nail trim")
        assert len(pet.tasks) == 1
        assert pet.tasks[0].completed is True

    def test_renewed_task_preserves_attributes(self):
        pet = Pet(name="Mochi", species="dog")
        pet.add_task(Task(
            title="Walk", description="Morning stroll", duration_minutes=30,
            priority="high", category="exercise", frequency="daily",
            preferred_time="07:00",
        ))

        pet.complete_task("Walk")
        renewed = pet.tasks[0]
        assert renewed.title == "Walk"
        assert renewed.description == "Morning stroll"
        assert renewed.duration_minutes == 30
        assert renewed.priority == "high"
        assert renewed.category == "exercise"
        assert renewed.frequency == "daily"
        assert renewed.preferred_time == "07:00"
        assert renewed.completed is False

    def test_double_complete_keeps_single_task(self):
        pet = Pet(name="Mochi", species="dog")
        pet.add_task(Task(
            title="Walk", description="", duration_minutes=30,
            frequency="daily",
        ))

        pet.complete_task("Walk")
        pet.complete_task("Walk")
        assert len(pet.tasks) == 1
        assert pet.tasks[0].completed is False

    def test_scheduler_mark_scheduled_complete_renews_recurring(self):
        _, mochi, _, scheduler = _make_scheduler(minutes=60)
        mochi.add_task(Task(
            title="Walk", description="", duration_minutes=30,
            frequency="daily",
        ))
        mochi.add_task(Task(
            title="Nail trim", description="", duration_minutes=15,
            frequency="as_needed",
        ))

        scheduler.generate_schedule()
        scheduler.mark_scheduled_complete()

        walk = next(t for t in mochi.tasks if t.title == "Walk")
        nail = next(t for t in mochi.tasks if t.title == "Nail trim")
        assert walk.completed is False
        assert nail.completed is True


# ---------------------------------------------------------------------------
# Conflict Detection
# ---------------------------------------------------------------------------

class TestConflictDetection:
    def test_overlapping_times_flagged(self):
        _, mochi, _, scheduler = _make_scheduler()
        mochi.add_task(Task(
            title="Walk", description="", duration_minutes=30,
            preferred_time="07:00",
        ))
        mochi.add_task(Task(
            title="Brush teeth", description="", duration_minutes=10,
            preferred_time="07:15",
        ))

        warnings = scheduler.detect_conflicts()
        assert len(warnings) == 1
        assert "Walk" in warnings[0]
        assert "Brush teeth" in warnings[0]

    def test_cross_pet_overlap_flagged(self):
        _, mochi, whiskers, scheduler = _make_scheduler()
        mochi.add_task(Task(
            title="Walk", description="", duration_minutes=30,
            preferred_time="07:00",
        ))
        whiskers.add_task(Task(
            title="Feed", description="", duration_minutes=10,
            preferred_time="07:20",
        ))

        warnings = scheduler.detect_conflicts()
        assert len(warnings) == 1
        assert "Mochi" in warnings[0]
        assert "Whiskers" in warnings[0]

    def test_adjacent_times_not_flagged(self):
        _, mochi, _, scheduler = _make_scheduler()
        mochi.add_task(Task(
            title="Walk", description="", duration_minutes=30,
            preferred_time="07:00",
        ))
        mochi.add_task(Task(
            title="Feed", description="", duration_minutes=10,
            preferred_time="07:30",
        ))

        warnings = scheduler.detect_conflicts()
        assert len(warnings) == 0

    def test_no_timed_tasks_returns_empty(self):
        _, mochi, _, scheduler = _make_scheduler()
        mochi.add_task(Task(title="Walk", description="", duration_minutes=30))
        mochi.add_task(Task(title="Feed", description="", duration_minutes=10))

        warnings = scheduler.detect_conflicts()
        assert warnings == []

    def test_three_way_overlap_produces_three_warnings(self):
        _, mochi, whiskers, scheduler = _make_scheduler()
        mochi.add_task(Task(
            title="Task A", description="", duration_minutes=30,
            preferred_time="07:00",
        ))
        mochi.add_task(Task(
            title="Task B", description="", duration_minutes=20,
            preferred_time="07:10",
        ))
        whiskers.add_task(Task(
            title="Task C", description="", duration_minutes=25,
            preferred_time="07:05",
        ))

        warnings = scheduler.detect_conflicts()
        assert len(warnings) == 3
