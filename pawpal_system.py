"""PawPal+ logic layer: backend classes for owners, pets, tasks, and scheduling."""

from dataclasses import dataclass, field
from datetime import date, time

# Higher number = more important. Sort with this instead of the raw strings,
# because alphabetically "high" < "low" < "medium".
PRIORITY_ORDER = {"high": 3, "medium": 2, "low": 1}


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

    def mark_complete(self, today: date) -> None:
        """Record that this task was done on the given date."""
        pass

    def mark_incomplete(self) -> None:
        """Clear the completion record for this task."""
        pass

    def is_completed(self, today: date) -> bool:
        """Return True if this task was already done on the given date."""
        pass

    def is_due_today(self, today: date) -> bool:
        """Return True if this task should happen on the given date."""
        pass

    def next_occurrence(self, today: date) -> date | None:
        """Return the next date this task is due, or None if it won't repeat."""
        pass


@dataclass
class Pet:
    """An animal that has its own list of care tasks."""

    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet and set the task's pet_name."""
        pass

    def edit_task(self, task_id: int, **changes) -> None:
        """Update fields on the task with the given id."""
        pass

    def remove_task(self, task_id: int) -> None:
        """Remove the task with the given id."""
        pass

    def get_tasks(self) -> list[Task]:
        """Return all of this pet's tasks."""
        pass


@dataclass
class Owner:
    """The person using the app, who owns one or more pets."""

    name: str
    available_minutes: int = 60
    pets: list[Pet] = field(default_factory=list)
    _next_task_id: int = field(default=1, repr=False)

    def new_task_id(self) -> int:
        """Return a task id that is unique across all of this owner's pets."""
        pass

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass

    def remove_pet(self, pet_name: str) -> None:
        """Remove the pet with the given name."""
        pass

    def get_pet(self, pet_name: str) -> Pet | None:
        """Return the pet with the given name, or None if not found."""
        pass

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        pass


class Scheduler:
    """Builds and explains a daily care plan for an owner's pets."""

    def __init__(self, owner: Owner):
        self.owner = owner
        self.plan: list[Task] = []            # tasks chosen for today, in order
        self.skipped: list[Task] = []         # due today but didn't fit in the time
        self.reasons: dict[int, str] = {}     # task_id -> why it was chosen or skipped

    def get_todays_tasks(self, today: date) -> list[Task]:
        """Return tasks that are due today and not yet completed."""
        pass

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered from high to low priority, using PRIORITY_ORDER."""
        pass

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered by preferred time; tasks with no time go last."""
        pass

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Return warnings for tasks whose time windows (start + duration) overlap."""
        pass

    def generate_plan(self, today: date) -> list[Task]:
        """Rebuild plan, skipped, and reasons for the given date, and return the plan."""
        pass

    def explain_plan(self) -> str:
        """Return a readable explanation built from plan, skipped, and reasons."""
        pass
