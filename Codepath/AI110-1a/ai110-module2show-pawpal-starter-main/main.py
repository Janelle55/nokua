"""CLI demo / testing ground for the PawPal+ logic layer.

Run with:  py main.py   (or: python main.py)

Builds an owner with two pets and several tasks, then exercises the Scheduler:
sorting, filtering, conflict detection, and recurring-task handling.
"""

from pawpal_system import Owner, Pet, Task, Priority, Scheduler


def print_header(title: str) -> None:
    """Print a titled section divider for readable terminal output."""
    print(f"\n{title}")
    print("-" * len(title))


def main() -> None:
    """Build sample data and demonstrate every Scheduler capability."""
    # 1. Create an owner and two pets.
    owner = Owner(name="Janelle")
    rex = owner.add_pet(Pet(name="Rex", species="dog"))
    bella = owner.add_pet(Pet(name="Bella", species="cat"))

    # 2. Add tasks *out of order* so sorting has something to do.
    #    Rex's walk (08:00-08:30) and Bella's meds (08:15) overlap on purpose.
    bella.add_task(Task("Evening play", 20, Priority.LOW, "18:00", "daily"))
    rex.add_task(Task("Morning walk", 30, Priority.HIGH, "08:00", "daily"))
    bella.add_task(Task("Give meds", 5, Priority.HIGH, "08:15", "daily"))
    rex.add_task(Task("Feeding", 10, Priority.MEDIUM, "12:00", "daily"))
    bella.add_task(Task("Weekly grooming", 45, Priority.MEDIUM, "10:00", "weekly"))

    scheduler = Scheduler(owner)

    # 3. Today's schedule, sorted by time.
    print_header("Today's Schedule (sorted by time)")
    for task in scheduler.sort_by_time():
        print(" ", task)

    # 4. Sorted by priority (most urgent first).
    print_header("By Priority (most urgent first)")
    for task in scheduler.sort_by_priority():
        print(" ", task)

    # 5. Filter: only Bella's tasks.
    print_header("Filter: Bella's tasks")
    for task in scheduler.filter_tasks(pet_name="Bella"):
        print(" ", task)

    # 6. Conflict detection (returns warnings, never crashes).
    print_header("Conflict Check")
    warnings = scheduler.conflict_warnings()
    if warnings:
        for warning in warnings:
            print(" ", warning)
    else:
        print("  No conflicts found.")

    # 7. Recurring task: completing a daily task spawns tomorrow's copy.
    print_header("Recurring Tasks")
    walk = rex.get_tasks()[0]
    print(f"  Before: Rex has {len(rex.get_tasks())} tasks.")
    next_walk = walk.mark_complete()
    print(f"  Completed '{walk.description}'.")
    if next_walk:
        print(f"  Auto-created next occurrence for {next_walk.due_date}.")
    print(f"  After:  Rex has {len(rex.get_tasks())} tasks.")


if __name__ == "__main__":
    main()
