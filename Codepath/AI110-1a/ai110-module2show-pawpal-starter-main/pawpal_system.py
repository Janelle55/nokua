"""PawPal+ — pet care scheduling system (logic layer).

Class relationships:
    Owner --owns--> Pet --has--> Task   (Task keeps a back-reference to its Pet)
    Scheduler --references--> Owner     (reads tasks via Owner.get_all_tasks())

This module is UI-agnostic: it holds all the "brain" of the app so it can be
driven from a CLI (main.py), a test suite (tests/), or Streamlit (app.py).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import IntEnum


class Priority(IntEnum):
    """Task priority with a defined order (higher value = more urgent)."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


# How far ahead the next occurrence of a recurring task is scheduled.
_FREQUENCY_STEP = {
    "daily": timedelta(days=1),
    "weekly": timedelta(weeks=1),
}


def _to_minutes(time_str: str) -> int:
    """Convert an 'HH:MM' string into minutes since midnight for time math."""
    hours, minutes = time_str.split(":")
    return int(hours) * 60 + int(minutes)


@dataclass
class Task:
    """A single care activity for a pet (e.g. 'Walk', 'Feed', 'Medicate')."""

    description: str
    duration: int                     # minutes
    priority: Priority
    time: str                         # scheduled start, "HH:MM"
    frequency: str                    # "daily" | "weekly" | "once"
    completed: bool = False
    due_date: date = field(default_factory=date.today)
    # Back-reference set by Pet.add_task so a conflict can name the pet involved.
    pet: "Pet | None" = field(default=None, repr=False)

    @property
    def start_minutes(self) -> int:
        """Return the task's start time as minutes since midnight."""
        return _to_minutes(self.time)

    @property
    def end_minutes(self) -> int:
        """Return the task's end time (start + duration) in minutes."""
        return self.start_minutes + self.duration

    def overlaps(self, other: "Task") -> bool:
        """Return True if this task's time window overlaps another's."""
        return self.start_minutes < other.end_minutes and other.start_minutes < self.end_minutes

    def is_recurring(self) -> bool:
        """Return True if this task repeats on a known frequency."""
        return self.frequency in _FREQUENCY_STEP

    def create_next_occurrence(self) -> "Task":
        """Return a fresh, uncompleted copy of this task on its next date."""
        step = _FREQUENCY_STEP[self.frequency]
        return Task(
            description=self.description,
            duration=self.duration,
            priority=self.priority,
            time=self.time,
            frequency=self.frequency,
            completed=False,
            due_date=self.due_date + step,
            pet=None,  # re-linked when added to a pet
        )

    def mark_complete(self) -> "Task | None":
        """Mark this task done; if recurring, schedule and return its next occurrence."""
        self.completed = True
        if self.is_recurring() and self.pet is not None:
            return self.pet.add_task(self.create_next_occurrence())
        return None

    def __str__(self) -> str:
        """Return a human-readable one-line summary of the task."""
        owner_pet = self.pet.name if self.pet else "?"
        status = "done" if self.completed else "todo"
        return (
            f"{self.time}  {self.description:<16} "
            f"({self.duration:>3} min | {self.priority.name:<6} | {owner_pet} | {status})"
        )


@dataclass
class Pet:
    """A pet owned by an Owner. Holds its own list of care tasks."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> Task:
        """Attach a task to this pet, linking the task back to the pet."""
        task.pet = self
        self.tasks.append(task)
        return task

    def get_tasks(self) -> list[Task]:
        """Return all tasks belonging to this pet."""
        return self.tasks


@dataclass
class Owner:
    """A pet owner. Manages multiple pets and exposes all their tasks."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> Pet:
        """Add a pet to this owner."""
        self.pets.append(pet)
        return pet

    def get_all_tasks(self) -> list[Task]:
        """Flatten and return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.get_tasks()]


@dataclass
class Scheduler:
    """The 'brain': retrieves, sorts, filters, and checks an owner's tasks."""

    owner: Owner

    def sort_by_time(self) -> list[Task]:
        """Return the owner's tasks ordered by scheduled start time."""
        return sorted(self.owner.get_all_tasks(), key=lambda t: t.start_minutes)

    def sort_by_priority(self) -> list[Task]:
        """Return tasks by priority (most urgent first), then by time."""
        return sorted(
            self.owner.get_all_tasks(),
            key=lambda t: (-t.priority, t.start_minutes),
        )

    def filter_tasks(
        self,
        pet_name: str | None = None,
        completed: bool | None = None,
        priority: Priority | None = None,
        frequency: str | None = None,
    ) -> list[Task]:
        """Return tasks matching any of the given pet/status/priority filters."""
        tasks = self.owner.get_all_tasks()
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet and t.pet.name == pet_name]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        if priority is not None:
            tasks = [t for t in tasks if t.priority == priority]
        if frequency is not None:
            tasks = [t for t in tasks if t.frequency == frequency]
        return tasks

    def detect_conflicts(self) -> list[tuple[Task, Task]]:
        """Return pairs of pending tasks whose time windows overlap."""
        pending = sorted(
            (t for t in self.owner.get_all_tasks() if not t.completed),
            key=lambda t: t.start_minutes,
        )
        conflicts: list[tuple[Task, Task]] = []
        for i, current in enumerate(pending):
            for nxt in pending[i + 1:]:
                if nxt.start_minutes >= current.end_minutes:
                    break  # sorted, so nothing later can overlap current either
                conflicts.append((current, nxt))
        return conflicts

    def conflict_warnings(self) -> list[str]:
        """Return human-readable warning strings for each detected conflict."""
        warnings = []
        for a, b in self.detect_conflicts():
            warnings.append(
                f"[!] Conflict: '{a.description}' ({a.pet.name if a.pet else '?'}) at {a.time} "
                f"overlaps '{b.description}' ({b.pet.name if b.pet else '?'}) at {b.time}"
            )
        return warnings

    def generate_daily_plan(self, day: date | None = None) -> list[Task]:
        """Return the pending tasks due on `day` (default today), ordered by time."""
        target = day or date.today()
        due = [
            t
            for t in self.owner.get_all_tasks()
            if not t.completed and t.due_date == target
        ]
        return sorted(due, key=lambda t: t.start_minutes)


if __name__ == "__main__":
    # Minimal self-check; the full CLI demo lives in main.py.
    owner = Owner(name="Demo")
    pet = owner.add_pet(Pet(name="Rex", species="dog"))
    pet.add_task(Task("Walk", 30, Priority.HIGH, "08:00", "daily"))
    print(Scheduler(owner).generate_daily_plan()[0])
