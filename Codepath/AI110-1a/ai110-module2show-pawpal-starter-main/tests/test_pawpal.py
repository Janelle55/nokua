"""Automated tests for the PawPal+ logic layer.

Run from the project root with:  py -m pytest   (or: python -m pytest)

Covers the core behaviors and the edge cases that matter for a scheduler:
task completion, task addition, sorting, filtering, conflict detection,
recurring-task generation, and an empty-schedule edge case.
"""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Task, Priority, Scheduler


def make_task(description="Walk", duration=30, priority=Priority.MEDIUM,
              time="08:00", frequency="daily"):
    """Build a Task with sensible defaults so tests stay readable."""
    return Task(description, duration, priority, time, frequency)


# --- Core behaviors (Phase 2) ---------------------------------------------

def test_mark_complete_changes_status():
    """Calling mark_complete() flips a task's completed flag to True."""
    pet = Pet("Rex", "dog")
    task = pet.add_task(make_task(frequency="once"))
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    """Adding a task to a Pet increases that pet's task count by one."""
    pet = Pet("Rex", "dog")
    assert len(pet.get_tasks()) == 0
    pet.add_task(make_task())
    assert len(pet.get_tasks()) == 1


def test_add_task_sets_back_reference():
    """A task added to a pet points back to that pet."""
    pet = Pet("Bella", "cat")
    task = pet.add_task(make_task())
    assert task.pet is pet


# --- Sorting (Phase 4/5) --------------------------------------------------

def test_sort_by_time_is_chronological():
    """sort_by_time() returns tasks in ascending start-time order."""
    owner = Owner("Jan")
    pet = owner.add_pet(Pet("Rex", "dog"))
    pet.add_task(make_task(description="Late", time="18:00"))
    pet.add_task(make_task(description="Early", time="06:00"))
    pet.add_task(make_task(description="Mid", time="12:00"))
    ordered = [t.description for t in Scheduler(owner).sort_by_time()]
    assert ordered == ["Early", "Mid", "Late"]


def test_sort_by_priority_orders_high_first():
    """sort_by_priority() puts the most urgent task first."""
    owner = Owner("Jan")
    pet = owner.add_pet(Pet("Rex", "dog"))
    pet.add_task(make_task(description="Low", priority=Priority.LOW, time="07:00"))
    pet.add_task(make_task(description="High", priority=Priority.HIGH, time="09:00"))
    ordered = [t.description for t in Scheduler(owner).sort_by_priority()]
    assert ordered[0] == "High"


# --- Filtering (Phase 4) --------------------------------------------------

def test_filter_by_pet_name():
    """filter_tasks(pet_name=...) returns only that pet's tasks."""
    owner = Owner("Jan")
    rex = owner.add_pet(Pet("Rex", "dog"))
    bella = owner.add_pet(Pet("Bella", "cat"))
    rex.add_task(make_task(description="Walk"))
    bella.add_task(make_task(description="Feed"))
    result = Scheduler(owner).filter_tasks(pet_name="Bella")
    assert len(result) == 1 and result[0].description == "Feed"


def test_filter_by_completion_status():
    """filter_tasks(completed=False) excludes finished tasks."""
    owner = Owner("Jan")
    pet = owner.add_pet(Pet("Rex", "dog"))
    done = pet.add_task(make_task(description="Done", frequency="once"))
    pet.add_task(make_task(description="Pending", frequency="once"))
    done.mark_complete()
    pending = Scheduler(owner).filter_tasks(completed=False)
    assert [t.description for t in pending] == ["Pending"]


# --- Conflict detection (Phase 4/5) ---------------------------------------

def test_detect_conflicts_flags_overlap():
    """Two overlapping tasks are reported as a conflict."""
    owner = Owner("Jan")
    pet = owner.add_pet(Pet("Rex", "dog"))
    pet.add_task(make_task(description="Walk", time="08:00", duration=30))   # 08:00-08:30
    pet.add_task(make_task(description="Meds", time="08:15", duration=5))    # 08:15-08:20
    conflicts = Scheduler(owner).detect_conflicts()
    assert len(conflicts) == 1


def test_no_conflict_for_back_to_back_tasks():
    """Tasks that touch but do not overlap are not flagged."""
    owner = Owner("Jan")
    pet = owner.add_pet(Pet("Rex", "dog"))
    pet.add_task(make_task(description="Walk", time="08:00", duration=30))   # ends 08:30
    pet.add_task(make_task(description="Feed", time="08:30", duration=10))   # starts 08:30
    assert Scheduler(owner).detect_conflicts() == []


# --- Recurring tasks (Phase 4/5) ------------------------------------------

def test_completing_daily_task_creates_next_day_occurrence():
    """Marking a daily task complete creates a new task for the following day."""
    pet = Pet("Rex", "dog")
    task = pet.add_task(make_task(frequency="daily"))
    start_date = task.due_date
    next_task = task.mark_complete()
    assert len(pet.get_tasks()) == 2
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.due_date == start_date + timedelta(days=1)


def test_completing_weekly_task_creates_next_week_occurrence():
    """A weekly task's next occurrence is scheduled seven days later."""
    pet = Pet("Bella", "cat")
    task = pet.add_task(make_task(frequency="weekly"))
    next_task = task.mark_complete()
    assert next_task.due_date == task.due_date + timedelta(weeks=1)


def test_non_recurring_task_creates_no_new_occurrence():
    """A one-off task does not spawn a follow-up when completed."""
    pet = Pet("Rex", "dog")
    task = pet.add_task(make_task(frequency="once"))
    assert task.mark_complete() is None
    assert len(pet.get_tasks()) == 1


# --- Edge cases (Phase 5) -------------------------------------------------

def test_daily_plan_for_pet_with_no_tasks_is_empty():
    """An owner with a pet but no tasks produces an empty daily plan."""
    owner = Owner("Jan")
    owner.add_pet(Pet("Rex", "dog"))
    assert Scheduler(owner).generate_daily_plan() == []


def test_daily_plan_excludes_other_days():
    """Tasks due on another date do not appear in today's plan."""
    owner = Owner("Jan")
    pet = owner.add_pet(Pet("Rex", "dog"))
    today_task = make_task(description="Today")
    tomorrow_task = make_task(description="Tomorrow")
    tomorrow_task.due_date = date.today() + timedelta(days=1)
    pet.add_task(today_task)
    pet.add_task(tomorrow_task)
    plan = Scheduler(owner).generate_daily_plan()
    assert [t.description for t in plan] == ["Today"]
