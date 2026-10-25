"""PawPal+ logic layer: backend classes for owners, pets, tasks, and scheduling."""

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Task:
    """A single pet care activity, such as a walk, feeding, or medication."""

    task_id: int
    title: str
    duration_minutes: int
    priority: str = "medium"          # "low", "medium", or "high"
    preferred_time: str = ""          # e.g. "08:00"
    frequency: str = "daily"          # "daily", "weekly", or "once"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        pass

    def mark_incomplete(self) -> None:
        """Mark this task as not done."""
        pass

    def is_due_today(self, today: date) -> bool:
        """Return True if this task should happen on the given date."""
        pass

    def next_occurrence(self) -> date:
        """Return the next date this task is due, based on its frequency."""
        pass


@dataclass
class Pet:
    """An animal that has its own list of care tasks."""

    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet."""
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
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass

    def remove_pet(self, pet_name: str) -> None:
        """Remove the pet with the given name."""
        pass

    def get_pet(self, pet_name: str) -> Pet:
        """Return the pet with the given name."""
        pass

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        pass


class Scheduler:
    """Builds and explains a daily care plan for an owner's pets."""

    def __init__(self, owner: Owner):
        self.owner = owner
        self.plan: list[Task] = []

    def get_todays_tasks(self) -> list[Task]:
        """Return tasks that are due today."""
        pass

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered from high to low priority."""
        pass

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered by preferred time."""
        pass

    def detect_conflicts(self) -> list[str]:
        """Return warnings for tasks whose times overlap."""
        pass

    def generate_plan(self) -> list[Task]:
        """Choose and order today's tasks to fit the owner's available time."""
        pass

    def explain_plan(self) -> str:
        """Return a readable explanation of why each task was chosen."""
        pass
