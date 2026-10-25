"""Tests for the PawPal+ logic layer."""

from datetime import date

from pawpal_system import Pet, Task


def test_mark_complete_changes_status():
    """Calling mark_complete() should mark the task as done for that day."""
    task = Task(1, "Morning walk", 30, "high")
    today = date(2026, 10, 25)

    assert not task.is_completed(today)

    task.mark_complete(today)

    assert task.is_completed(today)
    assert task.last_completed == today


def test_add_task_increases_pet_task_count():
    """Adding a task to a pet should increase its task count by one."""
    pet = Pet("Mochi", "dog")
    assert len(pet.get_tasks()) == 0

    pet.add_task(Task(1, "Feeding", 10, "high"))

    assert len(pet.get_tasks()) == 1
