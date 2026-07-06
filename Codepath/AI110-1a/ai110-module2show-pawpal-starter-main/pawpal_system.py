"""PawPal — pet care scheduling system.

Skeleton generated from the UML class diagram:
    Owner --owns--> Pet --has--> Task
    Scheduler --references--> Owner
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    """A single care task for a pet (e.g. 'Walk', 'Feed', 'Medicate')."""

    description: str
    duration: int          # minutes
    priority: str          # e.g. "high" | "medium" | "low"
    time: str              # scheduled time, e.g. "08:00"
    frequency: str         # e.g. "daily" | "weekly"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        # TODO: set completed to True
        ...


@dataclass
class Pet:
    """A pet owned by an Owner. Holds its own list of care tasks."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a new task to this pet."""
        # TODO: append task to self.tasks
        ...

    def get_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        # TODO: return self.tasks
        ...


@dataclass
class Owner:
    """A pet owner. Owns one or more pets."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        # TODO: append pet to self.pets
        ...

    def get_all_tasks(self) -> list[Task]:
        """Collect and return tasks across all of this owner's pets."""
        # TODO: flatten tasks from every pet in self.pets
        ...


@dataclass
class Scheduler:
    """Organizes an owner's tasks into a usable plan.

    Reads tasks through the owner reference (Owner -> Pet -> Task).
    """

    owner: Owner

    def sort_by_time(self) -> list[Task]:
        """Return the owner's tasks ordered by scheduled time."""
        # TODO: sort self.owner.get_all_tasks() by Task.time
        ...

    def sort_by_priority(self) -> list[Task]:
        """Return the owner's tasks ordered by priority."""
        # TODO: sort self.owner.get_all_tasks() by Task.priority
        ...

    def filter_tasks(self, **criteria) -> list[Task]:
        """Return tasks matching the given criteria (e.g. priority, completed)."""
        # TODO: filter self.owner.get_all_tasks() by the given criteria
        ...

    def detect_conflicts(self) -> list[tuple[Task, Task]]:
        """Find pairs of tasks whose time + duration windows overlap."""
        # TODO: compare task time/duration windows and collect overlaps
        ...

    def generate_daily_plan(self) -> list[Task]:
        """Produce an ordered daily plan of tasks."""
        # TODO: build a time-ordered plan, factoring in priority/conflicts
        ...


if __name__ == "__main__":
    # Quick smoke test scaffold — fill in once methods are implemented.
    pass
