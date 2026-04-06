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

## Smarter Scheduling

Beyond basic priority sorting, the scheduler includes several features that make daily plans more realistic:

- **Preferred times** — Each task can specify a preferred time in `HH:MM` format. The scheduler orders tasks chronologically by their preferred time first, then falls back to priority and duration for tasks with no time set.
- **Conflict detection** — Before finalising a schedule the scheduler scans all preferred-time windows for overlaps and returns warning messages (e.g. "Morning walk 07:00–07:30 overlaps with Teeth brushing 07:10–07:20") instead of crashing.
- **Recurring tasks** — Daily and weekly tasks automatically regenerate a fresh pending copy the moment they are marked complete, so the owner never has to re-enter them for the next day.
- **Time-budget packing** — A greedy algorithm fills the owner's available minutes by fitting as many tasks as possible, highest priority first, and reports which tasks were skipped due to lack of time.
- **Multi-pet support** — The scheduler aggregates tasks across all of an owner's pets into a single unified plan, labelling each entry with the pet it belongs to.

## Testing PawPal+

### Running the tests

```bash
source .venv/bin/activate
python -m pytest tests/test_pawpal.py -v
```

### What the tests cover

The test suite contains **23 tests** across five areas:

| Test class | Tests | What it verifies |
|---|---|---|
| `TestTaskCompletion` | 4 | `mark_complete()` and `reset()` toggle status correctly; idempotent calls are safe |
| `TestPetTaskAddition` | 4 | Adding tasks increases the count; duplicate titles are rejected without side effects |
| `TestSortByTime` | 4 | Tasks sort in chronological `HH:MM` order; untimed tasks come last; `generate_schedule()` respects time-then-priority ordering |
| `TestRecurrence` | 6 | Daily/weekly tasks auto-renew on completion; `as_needed` tasks stay done; renewed tasks preserve all attributes; double-complete doesn't duplicate |
| `TestConflictDetection` | 5 | Overlapping times flagged (same pet and cross-pet); adjacent non-overlapping times pass cleanly; three-way overlap produces exactly 3 warnings |

### Confidence level

**Rating: 4 / 5**

The core scheduling logic, sorting algorithm, recurrence lifecycle, and conflict detection are all well-covered. The main gaps that would push this to 5 stars are: testing the Streamlit UI integration end-to-end, testing the overnight time boundary (`23:50` wrapping past midnight), and stress-testing with a large number of tasks to verify performance.

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
