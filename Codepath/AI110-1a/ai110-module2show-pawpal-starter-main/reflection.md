# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
 The initial UML design has four classes, one for the owner information, pet information, tasks, and then one to generate a final schedule.
 
- What classes did you include, and what responsibilities did you assign to each?
For the owner class, there should be basic information such as name, age, and preferences. Likewise, the pet class functions in a similar manner. The task class should describe and manage tasks, and the scheduler class should create a personalized schedule.

**b. Design changes**

- Did your design change during implementation?
Yes. After building the skeleton I reviewed the relationships between the classes and found a few gaps in the original UML that I adjusted.

- If yes, describe at least one change and why you made it.

1. **Added a back-reference from Task to its Pet.** My original design only pointed one way (Owner → Pet → Task), but the Scheduler's `detect_conflicts()` returns pairs of overlapping tasks, and I realized I couldn't tell *which pet* each conflicting task belonged to. Without knowing the pet, a conflict message like "two tasks overlap" isn't useful — I need "Rex's walk overlaps with Bella's vet visit." So I gave the scheduler a way to keep the pet context when it flattens the task list.

2. **Changed `time` and `priority` from plain strings to typed values.** Originally `time` was a string like `"08:00"` and `priority` was a string like `"high"`. This broke two of my scheduler methods: string sorting puts priorities in the wrong order (alphabetically "high" comes before "low" and "medium"), and I can't do `time + duration` math on a string to detect overlaps. I switched priority to a ranked value so it sorts correctly, and treated time as a real time value so the conflict/overlap math works across hour boundaries.

3. **Made the Scheduler read tasks through `Owner.get_all_tasks()` instead of duplicating the traversal.** Several scheduler methods needed the full task list, and re-walking the Owner → Pet → Task tree in each one duplicated logic and re-computed the same list repeatedly. Centralizing the traversal in the Owner keeps the logic in one place and avoids redundant work when `generate_daily_plan()` calls the other methods.

Two smaller decisions that came out of the review: the scheduler should skip tasks marked `completed` so finished tasks don't create phantom conflicts, and `generate_daily_plan()` should consult `frequency` so weekly tasks don't show up on every daily plan.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
My scheduler considers three constraints: the **time** a task starts (and its duration, which together form a time window), the **priority** level (High/Medium/Low), and the task **frequency** (daily, weekly, or once) so recurring tasks regenerate and only tasks actually due show up in a day's plan. It also tracks **completion status** so finished tasks are excluded from the plan and from conflict checks.

- How did you decide which constraints mattered most?
Time mattered most because the whole point of a daily plan is *when* things happen, and time is what makes two tasks conflict. Priority came second: when a pet owner is busy, they need to know which task to protect if something has to give. I treated preferences as out of scope for this version to keep the core logic solid first (CLI-first workflow).

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
The biggest tradeoff is in **conflict detection**. I chose to detect *overlapping time windows* (`[start, start + duration)`) rather than only exact time matches — but I compare every pair of pending tasks after sorting, which is a simple O(n²)-style sweep rather than a fully optimized interval algorithm. I also model `time` as an `"HH:MM"` string converted to minutes, which means it does not handle tasks that cross midnight or account for time zones.

- Why is that tradeoff reasonable for this scenario?
A single pet owner realistically has a handful of tasks per day, not thousands, so the simple pairwise sweep is instant and far easier to read and trust than a clever algorithm. Detecting overlaps (not just identical start times) is the more *correct* choice for real scheduling — a 30-minute walk at 08:00 really does conflict with meds at 08:15 — so I spent my complexity budget there rather than on micro-optimizing the loop. Cross-midnight tasks are rare enough for daily pet care that deferring them is an acceptable simplification for this iteration.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used my AI coding assistant in agent mode across the whole build: generating the Mermaid UML from my class notes, scaffolding the class skeletons, then fleshing out the full implementation, tests, and Streamlit wiring. I also used it as a reviewer — I asked it to look at my skeleton and point out missing relationships and logic bottlenecks before I wrote any real logic. The most effective feature was letting the agent edit multiple files at once (logic, demo, tests) and then run `main.py` and `pytest` in the terminal so I could see real output instead of guessing.

- What kinds of prompts or questions were most helpful?
Specific, design-level questions worked best: "How should the Scheduler retrieve all tasks from the Owner's pets?" and "Suggest a lightweight conflict-detection strategy that returns a warning instead of crashing." Open-ended "write my app" prompts were less useful than pointed questions about *one* relationship or *one* method.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
The assistant first used a ⚠️ emoji inside the conflict warning strings. When we ran `main.py`, the Windows terminal (cp1252 encoding) crashed with a `UnicodeEncodeError`. I rejected the emoji in the CLI layer and switched to a plain `[!]` marker for terminal output, keeping the nicer emoji only in the Streamlit UI where encoding isn't an issue. I also pushed back on leaving `priority` and `time` as plain strings, because that would have quietly broken sorting and overlap math.

- How did you evaluate or verify what the AI suggested?
I verified everything by running it, not by trusting it. Every logic change was checked against `py main.py` output and the `pytest` suite (14 tests covering completion, sorting, filtering, conflicts, recurrence, and empty-schedule edge cases). When the emoji crash happened, the traceback told me exactly where the bug was, and I confirmed the fix by re-running the demo to a clean finish.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
14 automated tests in `tests/test_pawpal.py`: task completion flips the status flag; adding a task increases the pet's count and sets the back-reference; `sort_by_time` returns chronological order and `sort_by_priority` puts High first; filtering by pet name and by completion status; conflict detection flags real overlaps but *not* back-to-back tasks; recurrence creates a next-day (daily) or next-week (weekly) copy and creates nothing for one-off tasks; and edge cases like a pet with no tasks and tasks due on other days.

- Why were these tests important?
These are the behaviors the whole app depends on. If sorting or conflict detection is wrong, the daily plan is actively misleading, which is worse than useless for someone managing a pet's meds. The "no conflict for back-to-back tasks" test was especially important because it's the boundary case that separates a correct overlap check from a naive one.

**b. Confidence**

- How confident are you that your scheduler works correctly?
Fairly confident — 4 out of 5. All 14 tests pass and they cover both happy paths and the tricky boundaries (overlap vs. adjacency, recurrence steps, empty schedules). I'm not at 5/5 because the tests that rely on `date.today()` aren't frozen to a fixed clock, and I haven't tested cross-midnight tasks or malformed time strings.

- What edge cases would you test next if you had more time?
Tasks that span midnight (e.g. 23:30 + 60 min), invalid time input like `"25:00"` or `"8am"`, three or more tasks overlapping at once, and freezing the date so the recurrence tests are fully deterministic regardless of when they run.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I'm most satisfied with the conflict detection and recurring-task logic working together cleanly, and with the CLI-first workflow. Building and verifying the "brain" in `main.py` and `pytest` *before* touching the Streamlit UI meant that by the time I wired up `app.py`, the hard logic was already trustworthy and the UI was mostly plumbing.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I'd replace the `"HH:MM"` string with a real `datetime`/`time` type so cross-midnight tasks and input validation come for free, add owner **preferences** as a real constraint (e.g. "no tasks before 07:00"), and give recurring tasks an end date so they don't regenerate forever. I'd also freeze the clock in tests for full determinism.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
The most important thing I learned is that I'm the **lead architect** and the AI is a fast implementer — it's excellent at generating code and catching things I'd miss, but it will happily produce something subtly wrong (like string-sorted priorities or an emoji that crashes the Windows terminal). Using separate chat sessions per phase kept my design thinking, implementation, and testing from bleeding into each other, and running the code myself after every change is what actually caught the bugs. AI accelerated the work, but the judgment about *what's correct* had to stay with me.
