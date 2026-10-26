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

Output from running `python main.py` (the schedule part):

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
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
.........                                                                [100%]
9 passed in 0.01s
```

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

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
