import pytest

from pawpal_system import Task, Pet


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
