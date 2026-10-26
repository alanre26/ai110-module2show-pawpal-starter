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

## ✨ Features

- **Sorting by time:** tasks show up in clock order, "Anytime" tasks go last, and if two tasks are at the same time the higher priority one goes first.
- **Priority-based planning:** the daily plan fits high priority tasks first into the minutes you have free, and tells you why each task was picked or skipped.
- **Filtering:** see tasks for one pet, or only what's done / still to do today.
- **Daily and weekly recurrence:** marking a daily task done makes a new copy for tomorrow, and a weekly task comes back in 7 days. One-time tasks don't repeat.
- **Conflict warnings:** if two tasks overlap, you get a warning saying whether one pet is double-booked or you (the owner) are.

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

## 🧪 Testing PawPal+

Run the full test suite from the project folder (with the virtual environment activated):

```bash
python -m pytest
```

The tests in `tests/test_pawpal.py` cover the scheduling logic in `pawpal_system.py`:

- **Sorting:** tasks come back in time order, "Anytime" tasks go last, and tasks at the same time are ordered high priority first.
- **Recurring tasks:** completing a daily task creates a copy due the next day, and a weekly task creates one due in 7 days. One-off tasks don't repeat, completing a task twice doesn't make duplicates, and a missed copy stays on the list until it's done.
- **Conflict detection:** same start times and overlapping time slots are flagged, for one pet or across two pets (owner double-booked). Back-to-back tasks and tasks with no set time are not flagged.
- **Filtering:** tasks can be narrowed by pet name and by done vs. still to do.
- **Planning:** when time runs out, high-priority tasks are kept and lower ones are skipped with a reason.
- **Edge cases:** a pet with no tasks gets an empty plan and a "No tasks are due today." message instead of an error, and a weekly task set to a weekday only shows up on that day.

Output of a successful test run:

```
============================= test session starts ==============================
platform darwin -- Python 3.14.7, pytest-9.1.1, pluggy-1.7.0
rootdir: /Users/alanreyes/ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 16 items

tests/test_pawpal.py ................                                    [100%]

============================== 16 passed in 0.01s ==============================
```

**Confidence Level: ⭐⭐⭐⭐ (4/5)**

All 16 tests pass, covering the main scheduling behaviors and the edge cases that are most likely to break them. I'm not giving it 5 stars because the Streamlit UI in `app.py` isn't tested automatically, and a few inputs aren't checked yet, such as tasks that run past midnight or a task with an unknown priority.

## 📐 Smarter Scheduling

All of this lives in the `Scheduler` and `Task` classes in `pawpal_system.py`.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_by_priority()` | By time of day, "Anytime" last, priority breaks ties |
| Filtering | `Scheduler.filter_tasks()`, `Scheduler.get_todays_tasks()` | By pet name and/or done vs. still to do |
| Conflict handling | `Scheduler.detect_conflicts()` | Overlapping time windows, same pet or different pets |
| Recurring tasks | `Scheduler.complete_task()`, `Task.next_due_date()`, `Task.is_due_today()` | Daily copy due +1 day, weekly copy due +7 days |

### Sorting by time
`Scheduler.sort_by_time(tasks)` uses `sorted()` with a lambda key that returns a tuple: `(has no time, preferred time, -priority)`. Python compares tuples left to right, so timed tasks come first in clock order, "Anytime" tasks go last, and two tasks at the same time are ordered high priority first. `Scheduler.sort_by_priority(tasks)` is used when building the plan (high first, shorter first on ties so more tasks fit).

### Filtering by pet or status
`Scheduler.filter_tasks(today, pet_name=None, completed=None)` narrows the task list one filter at a time. Leave an argument as `None` to skip that filter.
- `pet_name="Mochi"` gives only Mochi's tasks
- `completed=True` gives tasks checked off today
- `completed=False` gives tasks due today that are still to do

### Conflict detection
`Scheduler.detect_conflicts(tasks)` sorts the timed tasks, then compares each task with the ones that start before it ends (start + duration). Because the list is sorted it can stop early instead of checking every pair. It never raises an error. It returns warning strings that say whether one pet is double-booked or the owner is (two different pets at once). Back-to-back tasks (08:00–08:30, then 08:30) are not a conflict. Tasks with no preferred time are not checked.

### Recurring tasks
Each `Task` object is one occurrence. `Scheduler.complete_task(task_id, today)` marks the task done, and if it's `daily` or `weekly` it creates a new copy for the next occurrence:
- `Task.next_due_date()` uses `timedelta`: daily = `today + timedelta(days=1)`, weekly = `today + timedelta(days=7)`
- the copy gets a new task ID, a `due_date`, and is added to the same pet
- `once` tasks don't repeat, and completing a task twice doesn't create duplicates
- `Task.is_due_today()` hides tasks finished on earlier days and shows copies once their `due_date` arrives (overdue copies stay on the list until done)

## 📸 Demo Walkthrough

Run the app with `streamlit run app.py`.

**What you can do in the app**

1. **Owner:** enter your name and how many minutes you have free today.
2. **Pets:** add a pet with a name, species, and age. Adding two pets with the same name gives an error.
3. **Tasks:** add a task for a pet with a title, duration, priority, optional preferred time, and how often it repeats (daily, weekly on a certain day, or once).
4. **Task list:** tasks are sorted by time. You can filter by pet or by "To do today" / "Done today", and the Status column shows what's done and when repeat copies are due next.
5. **Mark done:** pick a task and click "Mark done". If it repeats, a message tells you when the next one is due.
6. **Today's Schedule:** click "Generate schedule" to see the plan in time order with a "Why" column. Conflicts show up as a yellow warning at the top, and tasks that didn't fit are listed at the bottom.

**Example workflow**

1. Set your free time to 90 minutes and add two pets, Mochi (dog) and Luna (cat).
2. Give Mochi a daily "Morning walk" at 07:30 and "Dinner" at 18:00, and give Luna "Litter box" at 18:00.
3. Click "Generate schedule". The walk shows up first, and you get a warning that you're double-booked at 18:00 (Mochi's dinner and Luna's litter box).
4. Mark "Morning walk" done. The app says the next one is due tomorrow, and the task list shows the new copy.

**Sample CLI output**

`python main.py` runs the same logic in the terminal with sample pets and tasks:

```
============================================================
  Today's Schedule - Sunday, October 25, 2026
  Owner: Alan  |  Time used: 85 of 90 min
============================================================
  Time    Task              Pet       Length   Priority
  --------------------------------------------------------
  07:30   Morning walk      Mochi      30 min   high
  12:00   Noon walk         Mochi      20 min   medium
  12:10   Medication        Mochi       5 min   high
  18:00   Dinner            Mochi      10 min   high
  18:00   Litter box        Luna        5 min   medium
  Anytime Brushing          Luna       15 min   low

  Not scheduled:
    - Grooming (Mochi): skipped: needs 45 min but only 5 min left

  Warnings:
    ! Mochi is double-booked: 'Noon walk' (Mochi) at 12:00 and 'Medication' (Mochi) at 12:10 - 'Noon walk' runs until 12:20
    ! Owner is double-booked: 'Dinner' (Mochi) at 18:00 and 'Litter box' (Luna) at 18:00 - both start at 18:00
============================================================

Recurring tasks: completing a task adds its next copy
  Done: Morning walk (daily) -> next copy #10 due Mon 10/26
  Done: Grooming (weekly) -> next copy #11 due Sun 11/01
  Due tomorrow (Mon 10/26): Morning walk, Breakfast, Noon walk, Medication, Dinner, Litter box, Brushing
```
