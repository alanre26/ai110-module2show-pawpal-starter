"""Temporary testing ground: build a sample owner and print today's schedule."""

from datetime import date, time

from pawpal_system import Owner, Pet, Scheduler, Task


def print_schedule(scheduler: Scheduler, today: date) -> None:
    """Print the generated plan as a readable table."""
    owner = scheduler.owner
    used = sum(task.duration_minutes for task in scheduler.plan)

    print("=" * 60)
    print(f"  Today's Schedule - {today:%A, %B %d, %Y}")
    print(f"  Owner: {owner.name}  |  Time used: {used} of {owner.available_minutes} min")
    print("=" * 60)
    print(f"  {'Time':<8}{'Task':<18}{'Pet':<10}{'Length':<9}Priority")
    print("  " + "-" * 56)
    for task in scheduler.plan:
        when = f"{task.preferred_time:%H:%M}" if task.preferred_time else "Anytime"
        print(f"  {when:<8}{task.title:<18}{task.pet_name:<10}{task.duration_minutes:>3} min   {task.priority}")

    if scheduler.skipped:
        print("\n  Not scheduled:")
        for task in scheduler.skipped:
            print(f"    - {task.title} ({task.pet_name}): {scheduler.reasons[task.task_id]}")

    conflicts = scheduler.detect_conflicts(scheduler.plan)
    if conflicts:
        print("\n  Warnings:")
        for warning in conflicts:
            print(f"    ! {warning}")
    print("=" * 60)


def main() -> None:
    """Build a sample owner with two pets and print today's schedule."""
    owner = Owner("Alan", available_minutes=90)

    mochi = Pet("Mochi", "dog", age=3)
    luna = Pet("Luna", "cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task(owner.new_task_id(), "Morning walk", 30, "high", preferred_time=time(7, 30)))
    mochi.add_task(Task(owner.new_task_id(), "Noon walk", 20, "medium", preferred_time=time(12, 0)))
    luna.add_task(Task(owner.new_task_id(), "Breakfast", 10, "high", preferred_time=time(7, 45)))
    luna.add_task(Task(owner.new_task_id(), "Litter box", 5, "medium", preferred_time=time(18, 0)))
    luna.add_task(Task(owner.new_task_id(), "Brushing", 15, "low"))
    mochi.add_task(Task(owner.new_task_id(), "Grooming", 45, "low", frequency="weekly",
                        day_of_week=date.today().weekday()))

    today = date.today()
    scheduler = Scheduler(owner)
    scheduler.generate_plan(today)
    print_schedule(scheduler, today)


if __name__ == "__main__":
    main()
