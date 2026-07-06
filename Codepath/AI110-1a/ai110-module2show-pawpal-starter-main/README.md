# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Terminal output from running `py main.py` (or `python main.py`):

```
Today's Schedule (sorted by time)
---------------------------------
  08:00  Morning walk     ( 30 min | HIGH   | Rex | todo)
  08:15  Give meds        (  5 min | HIGH   | Bella | todo)
  10:00  Weekly grooming  ( 45 min | MEDIUM | Bella | todo)
  12:00  Feeding          ( 10 min | MEDIUM | Rex | todo)
  18:00  Evening play     ( 20 min | LOW    | Bella | todo)

By Priority (most urgent first)
-------------------------------
  08:00  Morning walk     ( 30 min | HIGH   | Rex | todo)
  08:15  Give meds        (  5 min | HIGH   | Bella | todo)
  10:00  Weekly grooming  ( 45 min | MEDIUM | Bella | todo)
  12:00  Feeding          ( 10 min | MEDIUM | Rex | todo)
  18:00  Evening play     ( 20 min | LOW    | Bella | todo)

Filter: Bella's tasks
---------------------
  18:00  Evening play     ( 20 min | LOW    | Bella | todo)
  08:15  Give meds        (  5 min | HIGH   | Bella | todo)
  10:00  Weekly grooming  ( 45 min | MEDIUM | Bella | todo)

Conflict Check
--------------
  [!] Conflict: 'Morning walk' (Rex) at 08:00 overlaps 'Give meds' (Bella) at 08:15

Recurring Tasks
---------------
  Before: Rex has 2 tasks.
  Completed 'Morning walk'.
  Auto-created next occurrence for 2026-07-07.
  After:  Rex has 3 tasks.
```

## 🧪 Testing PawPal+

Run the full suite from the project root:

```bash
python -m pytest      # Windows: py -m pytest
```

The suite (`tests/test_pawpal.py`) covers:

- **Task completion** — `mark_complete()` flips the `completed` flag.
- **Task addition** — adding a task increases the pet's task count and sets the back-reference.
- **Sorting correctness** — tasks return in chronological order, and by priority (urgent first).
- **Filtering** — by pet name and by completion status.
- **Conflict detection** — overlapping tasks are flagged; back-to-back tasks are not.
- **Recurrence logic** — completing a daily task creates a next-day copy; weekly → +7 days; one-off → none.
- **Edge cases** — a pet with no tasks yields an empty plan; tasks due on other days are excluded.

Sample test output:

```
============================= test session starts =============================
platform win32 -- Python 3.13.7, pytest-9.1.1, pluggy-1.6.0
collected 14 items

tests\test_pawpal.py ..............                                      [100%]

============================= 14 passed in 0.03s ==============================
```

**Confidence Level:** ⭐⭐⭐⭐☆ (4/5) — All 14 tests pass and cover the core logic and key
edge cases. Held back one star because time is modeled as an `"HH:MM"` string (no timezone
or cross-midnight handling) and recurrence advances by a fixed step without a calendar/end-date.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_by_priority()` | Time uses an `HH:MM → minutes` key; priority sorts by `Priority` enum (HIGH→LOW), then time as a tiebreaker. |
| Filtering | `Scheduler.filter_tasks(pet_name, completed, priority, frequency)` | Any combination of filters; e.g. only Bella's pending tasks. |
| Conflict handling | `Scheduler.detect_conflicts()`, `Scheduler.conflict_warnings()` | Compares `[start, start+duration)` windows so real *overlaps* are caught (not just identical times); returns warning strings instead of crashing. |
| Recurring tasks | `Task.mark_complete()`, `Task.create_next_occurrence()` | Completing a `daily`/`weekly` task auto-creates the next occurrence via `timedelta`; `once` tasks do not recur. |
| Daily plan | `Scheduler.generate_daily_plan(day)` | Returns pending tasks due on a given date, ordered by time. |

## ✨ Features

- **Owner → Pet → Task model** with a Task back-reference to its Pet, so conflicts can name the pet involved.
- **Sorting by time** and **by priority** (`Scheduler.sort_by_time` / `sort_by_priority`).
- **Filtering** by pet, completion status, priority, or frequency (`Scheduler.filter_tasks`).
- **Conflict warnings** for overlapping time windows (`Scheduler.conflict_warnings`).
- **Recurring tasks** — daily/weekly tasks regenerate on completion (`Task.mark_complete`).
- **Daily plan** generation for a chosen date (`Scheduler.generate_daily_plan`).
- **Streamlit UI** that persists state across reruns via `st.session_state`.

## 📸 Demo Walkthrough

### Running it

```bash
pip install -r requirements.txt
python main.py            # CLI demo (see Sample Output above)
streamlit run app.py      # interactive UI
```

### Streamlit UI features & example workflow

1. **Set the owner name** and **add a pet** (name + species) — the pet persists in `st.session_state`.
2. **Add a task** for that pet: title, time (`HH:MM`), duration, priority, and frequency.
3. Repeat to **add several tasks** across pets, including two that overlap in time.
4. **Today's Schedule** shows every task in a table, ordered by time via `Scheduler.sort_by_time()`.
5. Any overlap surfaces as a yellow **conflict warning** at the top (`st.warning`); a clean
   schedule shows a green success message.

Key `Scheduler` behaviors shown in the UI: **time sorting** and **conflict warnings** — the same
logic verified by the CLI output and test suite above (which also cover priority sorting,
filtering, and recurring tasks).

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
