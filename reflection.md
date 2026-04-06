# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The initial UML design uses five classes split into two layers: four data classes that represent the domain objects and one behavior class that contains the scheduling logic.

- **Owner** — Stores the pet owner's name, how many minutes they have available for pet care each day, and an optional list of preferences (e.g. "morning walks"). This class defines the time budget that constrains the schedule.
- **Pet** — Stores the pet's name, species, and any special needs. It holds a reference to its Owner, linking the two together so the scheduler knows whose constraints to apply.
- **Task** — Represents a single care activity (e.g. "morning walk"). Each task has a title, a duration in minutes, a priority level (high / medium / low), and an optional category (exercise, feeding, medical, etc.). It also provides a `priority_value()` helper that converts the priority string to a number for sorting.
- **ScheduleEntry** — Represents one slot in the generated daily plan. It wraps a Task with a start time (in minutes from the beginning of the day) and a reason string that explains why the task was placed at that time. It computes its own end time from the task's duration.
- **Scheduler** — The central algorithm class. It takes an Owner, a Pet, and a list of Tasks, then produces a list of ScheduleEntry objects via `generate_schedule()`. It also exposes helpers to add/remove tasks and to produce a human-readable explanation of the plan.

Owner, Pet, Task, and ScheduleEntry are implemented as Python dataclasses to keep the code concise and free of boilerplate. Scheduler is a regular class because its primary role is behavior (the scheduling algorithm), not data storage.

**Core user actions:**

1. **Register a pet profile** — The owner provides basic information about themselves and their pet (name, species, and any special needs). This gives the system the context it needs to tailor care recommendations and build a meaningful schedule.

2. **Add and manage care tasks** — The owner creates pet care tasks such as "morning walk," "feed dinner," or "give medication." Each task includes at least a duration and a priority level. The owner can also edit or remove tasks as their pet's routine changes.

3. **Generate a daily care schedule** — The owner requests a daily plan. The system selects and orders tasks based on constraints like available time, task priority, and owner preferences, then presents the schedule along with a brief explanation of why each task was placed at its assigned time.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
