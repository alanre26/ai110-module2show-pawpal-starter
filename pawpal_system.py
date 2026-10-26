"""PawPal+ logic layer: backend classes for owners, pets, tasks, and scheduling."""

from dataclasses import dataclass, field, fields, replace
from datetime import date, time, timedelta

# Higher number = more important. Sort with this instead of the raw strings,
# because alphabetically "high" < "low" < "medium".
PRIORITY_ORDER = {"high": 3, "medium": 2, "low": 1}

# How many days after completion the next copy of a repeating task is due.
REPEAT_DAYS = {"daily": 1, "weekly": 7}


def _minutes(t: time) -> int:
    """Convert a time of day to minutes after midnight."""
    return t.hour * 60 + t.minute


@dataclass
class Task:
    """A single pet care activity, such as a walk, feeding, or medication."""

    task_id: int
    title: str
    duration_minutes: int
    priority: str = "medium"              # "low", "medium", or "high"
    pet_name: str = ""                    # which pet this task belongs to
    preferred_time: time | None = None    # e.g. time(8, 0); None = any time
    frequency: str = "daily"              # "daily", "weekly", or "once"
    day_of_week: int | None = None        # for weekly tasks: 0 = Monday ... 6 = Sunday
    last_completed: date | None = None    # date it was last checked off
    due_date: date | None = None          # set on auto-created repeats; None = use frequency rules

    def mark_complete(self, today: date) -> None:
        """Record that this task was done on the given date."""
        self.last_completed = today

    def mark_incomplete(self) -> None:
        """Clear the completion record for this task."""
        self.last_completed = None

    def is_completed(self, today: date) -> bool:
        """Return True if this task was already done on the given date."""
        return self.last_completed == today

    def is_due_today(self, today: date) -> bool:
        """Return True if this task should happen on the given date."""
        # Each Task is one occurrence. Once it's done on an earlier day it's finished;
        # for daily/weekly tasks, Scheduler.complete_task() adds the next copy.
        if self.last_completed is not None and self.last_completed != today:
            return False
        if self.due_date is not None:
            return self.due_date <= today     # overdue copies stay on the list until done
        if self.frequency == "weekly" and self.day_of_week is not None:
            return today.weekday() == self.day_of_week
        return True

    def next_due_date(self, completed_on: date) -> date | None:
        """Return when the next copy is due after finishing on completed_on, or None if it doesn't repeat."""
        days = REPEAT_DAYS.get(self.frequency)
        return completed_on + timedelta(days=days) if days else None


@dataclass
class Pet:
    """An animal that has its own list of care tasks."""

    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet and set the task's pet_name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def edit_task(self, task_id: int, **changes) -> None:
        """Update fields on the task with the given id."""
        task = self._find_task(task_id)
        allowed = {f.name for f in fields(Task)} - {"task_id", "pet_name"}
        for key, value in changes.items():
            if key not in allowed:
                raise ValueError(f"Cannot edit field '{key}'")
            setattr(task, key, value)

    def remove_task(self, task_id: int) -> None:
        """Remove the task with the given id."""
        self.tasks.remove(self._find_task(task_id))

    def get_tasks(self) -> list[Task]:
        """Return all of this pet's tasks."""
        return list(self.tasks)

    def _find_task(self, task_id: int) -> Task:
        """Return the task with the given id, or raise ValueError."""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        raise ValueError(f"{self.name} has no task with id {task_id}")


@dataclass
class Owner:
    """The person using the app, who owns one or more pets."""

    name: str
    available_minutes: int = 60
    pets: list[Pet] = field(default_factory=list)
    _next_task_id: int = field(default=1, repr=False)

    def new_task_id(self) -> int:
        """Return a task id that is unique across all of this owner's pets."""
        task_id = self._next_task_id
        self._next_task_id += 1
        return task_id

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        if self.get_pet(pet.name) is not None:
            raise ValueError(f"{self.name} already has a pet named {pet.name}")
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove the pet with the given name."""
        pet = self.get_pet(pet_name)
        if pet is None:
            raise ValueError(f"{self.name} has no pet named {pet_name}")
        self.pets.remove(pet)

    def get_pet(self, pet_name: str) -> Pet | None:
        """Return the pet with the given name, or None if not found."""
        for pet in self.pets:
            if pet.name == pet_name:
                return pet
        return None

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Builds and explains a daily care plan for an owner's pets."""

    def __init__(self, owner: Owner):
        """Create a scheduler for the given owner with an empty plan."""
        self.owner = owner
        self.plan: list[Task] = []            # tasks chosen for today, in order
        self.skipped: list[Task] = []         # due today but didn't fit in the time
        self.reasons: dict[int, str] = {}     # task_id -> why it was chosen or skipped

    def get_todays_tasks(self, today: date) -> list[Task]:
        """Return tasks that are due today and not yet completed."""
        return [
            task for task in self.owner.get_all_tasks()
            if task.is_due_today(today) and not task.is_completed(today)
        ]

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered from high to low priority, using PRIORITY_ORDER."""
        # Ties go to the shorter task, so more tasks fit in the day.
        return sorted(tasks, key=lambda t: (-PRIORITY_ORDER.get(t.priority, 0), t.duration_minutes))

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered by preferred time; tasks with no time go last."""
        # Key tuple: timed tasks first, then earliest time, then higher priority on ties.
        return sorted(
            tasks,
            key=lambda t: (
                t.preferred_time is None,
                t.preferred_time or time.min,
                -PRIORITY_ORDER.get(t.priority, 0),
            ),
        )

    def filter_tasks(
        self, today: date, pet_name: str | None = None, completed: bool | None = None
    ) -> list[Task]:
        """Return tasks matching the given pet and/or completion status; None means any."""
        # Narrow the list one filter at a time; skipping a filter keeps everything.
        tasks = self.owner.get_all_tasks()
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet_name == pet_name]
        if completed is True:      # checked off today
            tasks = [t for t in tasks if t.is_completed(today)]
        elif completed is False:   # due today and still to do
            tasks = [t for t in tasks if t.is_due_today(today) and not t.is_completed(today)]
        return tasks

    def complete_task(self, task_id: int, today: date) -> Task | None:
        """Mark a task done; for daily/weekly tasks, add and return a new copy for the next due date."""
        task = next((t for t in self.owner.get_all_tasks() if t.task_id == task_id), None)
        if task is None:
            raise ValueError(f"No task with id {task_id}")
        if task.last_completed is not None:
            return None                       # already done, so don't create a duplicate copy

        task.mark_complete(today)
        next_date = task.next_due_date(today)
        if next_date is None:
            return None
        next_task = replace(task, task_id=self.owner.new_task_id(), last_completed=None, due_date=next_date)
        self.owner.get_pet(task.pet_name).add_task(next_task)
        return next_task

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Return warnings for tasks whose time windows (start + duration) overlap."""
        # Lightweight on purpose: never raises, just returns messages for the caller to show.
        # Sorting first means we can stop scanning as soon as a later task starts after this one ends.
        timed = self.sort_by_time([t for t in tasks if t.preferred_time is not None])
        warnings = []
        for i, first in enumerate(timed):
            first_end = _minutes(first.preferred_time) + first.duration_minutes
            for second in timed[i + 1:]:
                if _minutes(second.preferred_time) >= first_end:
                    break
                who = f"{first.pet_name} is double-booked" if first.pet_name == second.pet_name else "Owner is double-booked"
                if first.preferred_time == second.preferred_time:
                    detail = f"both start at {first.preferred_time:%H:%M}"
                else:
                    detail = f"'{first.title}' runs until {first_end // 60:02d}:{first_end % 60:02d}"
                warnings.append(
                    f"{who}: '{first.title}' ({first.pet_name}) at {first.preferred_time:%H:%M} and "
                    f"'{second.title}' ({second.pet_name}) at {second.preferred_time:%H:%M} - {detail}"
                )
        return warnings

    def generate_plan(self, today: date) -> list[Task]:
        """Rebuild plan, skipped, and reasons for the given date, and return the plan."""
        self.plan, self.skipped, self.reasons = [], [], {}
        remaining = self.owner.available_minutes

        for task in self.sort_by_priority(self.get_todays_tasks(today)):
            if task.duration_minutes <= remaining:
                self.plan.append(task)
                remaining -= task.duration_minutes
                self.reasons[task.task_id] = (
                    f"{task.priority} priority, fits in the time left ({remaining} min remaining after)"
                )
            else:
                self.skipped.append(task)
                self.reasons[task.task_id] = (
                    f"skipped: needs {task.duration_minutes} min but only {remaining} min left"
                )

        self.plan = self.sort_by_time(self.plan)
        return self.plan

    def explain_plan(self) -> str:
        """Return a readable explanation built from plan, skipped, and reasons."""
        if not self.plan and not self.skipped:
            return "No tasks are due today."

        lines = [f"Plan for {self.owner.name} ({self.owner.available_minutes} min available):"]
        for task in self.plan:
            when = f"{task.preferred_time:%H:%M}" if task.preferred_time else "Anytime"
            lines.append(
                f"  {when} - {task.title} for {task.pet_name} ({task.duration_minutes} min) "
                f"- {self.reasons[task.task_id]}"
            )
        for task in self.skipped:
            lines.append(f"  Not scheduled - {task.title} for {task.pet_name} - {self.reasons[task.task_id]}")
        for warning in self.detect_conflicts(self.plan):
            lines.append(f"  Warning: {warning}")
        return "\n".join(lines)
