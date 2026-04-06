# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Five classes in two layers — four dataclasses for data, one regular class for behaviour:

- **Owner** — name, available minutes, preferences. Defines the time budget.
- **Pet** — name, species, special needs. Owns a list of tasks.
- **Task** — title, duration, priority, category, frequency, preferred time, completion status.
- **ScheduleEntry** — wraps a Task with a start time and a reason string.
- **Scheduler** — takes an Owner, aggregates tasks across all pets, produces a list of ScheduleEntries.

Core user actions: register a pet profile, add/manage care tasks, generate a daily schedule.

**b. Design changes**

Two key changes during implementation:

1. Removed the `Pet → Owner` back-reference. The initial design had `Pet.__post_init__` auto-register into `owner.pets`, but this caused circular issues in Streamlit's session state. Final design uses explicit `Owner.add_pet()` for a clean one-directional flow: Owner → Pet → Task.
2. Evolved the Scheduler from single-pet to multi-pet by accepting just an Owner and aggregating tasks across all pets.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

Three constraints in order: preferred time (chronological `HH:MM`), then priority (high → low), then duration (shorter first). Preferred time outranks priority because a pet owner's day has a natural rhythm — feeding happens at feeding time regardless of priority level.

**b. Tradeoffs**

The scheduler uses a **greedy algorithm** instead of an optimal knapsack solver. It skips tasks that don't fit the remaining budget even if a different combination would use more time. This is reasonable because pet care schedules are small (5–15 tasks) — the greedy approach is instant, readable, and produces human-sensible plans.

---

## 3. AI Collaboration

**a. How you used AI**

- **Design** — brainstormed classes, attributes, and user actions.
- **Code generation** — built stubs from UML, then iteratively added sorting, conflict detection, and recurrence with specific prompts (e.g. "sort by HH:MM using a lambda key").
- **Code review** — asked Copilot to review its own output; it found seven issues like stubs returning `None`.
- **Testing** — described behaviours in plain English; Copilot produced 23 targeted pytest cases.

Most effective features: codebase-aware suggestions via `#file:` references, iterative self-review, and natural-language-to-test translation. Separate chat sessions per phase (design → code → tests → UI) kept context focused.

**b. Judgment and verification**

Rejected Copilot's `Pet.__post_init__` auto-registration pattern because it silently mutated the Owner on construction, causing duplicate pets on Streamlit page refresh. Replaced it with explicit `Owner.add_pet()` calls. Verified by tracing the object lifecycle in the running app.

---

## 4. Testing and Verification

**a. What you tested**

23 tests across five areas: task completion toggling, task addition with duplicate rejection, chronological sorting correctness, daily/weekly recurrence with attribute preservation, and conflict detection for overlapping/adjacent/multi-way time windows.

**b. Confidence**

**4 / 5** — Core logic is solid. Gaps: overnight time wrapping, large task-count stress tests, and Streamlit UI end-to-end testing.

---

## 5. Reflection

**a. What went well**

The layered architecture — data classes separate from the Scheduler algorithm — made each feature (conflict detection, recurrence) easy to add without ripple effects.

**b. What you would improve**

Add a time-picker widget instead of free-text `HH:MM`, a completion history log, and task dependencies (e.g. "medication after feeding").

**c. Key takeaway**

**AI works best when you stay in the architect role.** Clear, scoped instructions produce immediately usable output. Vague instructions lead to assumptions that don't fit your design. The developer's job is to decide, verify, and say "no" when needed.
