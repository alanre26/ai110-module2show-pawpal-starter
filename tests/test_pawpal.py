"""Tests for the PawPal+ logic layer."""

from datetime import date, time, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task

TODAY = date(2026, 10, 25)  # a Sunday


def make_scheduler(*tasks: Task) -> Scheduler:
    """Return a scheduler for an owner whose dog Mochi has the given tasks."""
    owner = Owner("Alan", available_minutes=120)
    mochi = Pet("Mochi", "dog")
    owner.add_pet(mochi)
    for task in tasks:
        task.task_id = owner.new_task_id()
        mochi.add_task(task)
    return Scheduler(owner)


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


def test_sort_by_time_orders_tasks_and_puts_anytime_last():
    """Tasks added out of order should come back earliest first, with no-time tasks at the end."""
    scheduler = make_scheduler(
        Task(0, "Dinner", 10, preferred_time=time(18, 0)),
        Task(0, "Brushing", 15),
        Task(0, "Walk", 30, preferred_time=time(7, 30)),
    )
    titles = [t.title for t in scheduler.sort_by_time(scheduler.owner.get_all_tasks())]
    assert titles == ["Walk", "Dinner", "Brushing"]


def test_filter_tasks_by_pet_and_status():
    """filter_tasks should narrow by pet name and by done / still-to-do."""
    scheduler = make_scheduler(Task(0, "Walk", 30), Task(0, "Feeding", 10))
    luna = Pet("Luna", "cat")
    scheduler.owner.add_pet(luna)
    luna.add_task(Task(scheduler.owner.new_task_id(), "Litter box", 5))
    scheduler.complete_task(1, TODAY)

    assert [t.title for t in scheduler.filter_tasks(TODAY, pet_name="Luna")] == ["Litter box"]
    assert [t.title for t in scheduler.filter_tasks(TODAY, completed=True)] == ["Walk"]
    assert [t.title for t in scheduler.filter_tasks(TODAY, pet_name="Mochi", completed=False)] == ["Feeding"]


def test_completing_daily_task_creates_copy_due_tomorrow():
    """A finished daily task should spawn a new task due the next day."""
    scheduler = make_scheduler(Task(0, "Walk", 30, frequency="daily"))
    next_task = scheduler.complete_task(1, TODAY)

    assert next_task.due_date == TODAY + timedelta(days=1)
    assert next_task.task_id != 1 and next_task.last_completed is None
    assert [t.task_id for t in scheduler.get_todays_tasks(TODAY)] == []
    assert [t.task_id for t in scheduler.get_todays_tasks(TODAY + timedelta(days=1))] == [next_task.task_id]


def test_completing_weekly_task_creates_copy_due_in_seven_days():
    """A finished weekly task should come back exactly one week later, not the next day."""
    scheduler = make_scheduler(Task(0, "Grooming", 45, frequency="weekly"))
    next_task = scheduler.complete_task(1, TODAY)

    assert next_task.due_date == TODAY + timedelta(days=7)
    assert scheduler.get_todays_tasks(TODAY + timedelta(days=1)) == []


def test_completing_once_task_or_completing_twice_adds_nothing():
    """One-off tasks don't repeat, and completing the same task twice shouldn't duplicate it."""
    scheduler = make_scheduler(Task(0, "Vet visit", 60, frequency="once"), Task(0, "Walk", 30))

    assert scheduler.complete_task(1, TODAY) is None
    scheduler.complete_task(2, TODAY)
    assert scheduler.complete_task(2, TODAY) is None
    assert len(scheduler.owner.get_all_tasks()) == 3   # 2 originals + 1 copy of Walk


def test_detect_conflicts_flags_same_time_and_overlaps():
    """Same start time and overlapping windows should each produce a warning."""
    scheduler = make_scheduler(
        Task(0, "Walk", 30, preferred_time=time(12, 0)),
        Task(0, "Medication", 5, preferred_time=time(12, 10)),   # inside the walk
        Task(0, "Dinner", 10, preferred_time=time(18, 0)),
        Task(0, "Brushing", 10, preferred_time=time(18, 0)),     # same start
    )
    warnings = scheduler.detect_conflicts(scheduler.owner.get_all_tasks())

    assert len(warnings) == 2
    assert "Mochi is double-booked" in warnings[0]
    assert "both start at 18:00" in warnings[1]


def test_back_to_back_tasks_are_not_a_conflict():
    """A task starting right when another ends should not be flagged."""
    scheduler = make_scheduler(
        Task(0, "Walk", 30, preferred_time=time(8, 0)),
        Task(0, "Feeding", 10, preferred_time=time(8, 30)),
    )
    assert scheduler.detect_conflicts(scheduler.owner.get_all_tasks()) == []
