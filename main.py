from pawpal_system import Owner, Pet, Task, Scheduler


def print_tasks(owner: Owner, label: str = "") -> None:
    """Helper to show every task's status for each pet."""
    for pet in owner.pets:
        print(f"  {pet.name}:")
        for t in pet.tasks:
            status = "done" if t.completed else "pending"
            freq = t.frequency
            time_str = f" @ {t.preferred_time}" if t.preferred_time else ""
            print(f"    [{status}] {t.title}{time_str}  ({t.priority}, {freq})")


def main() -> None:
    owner = Owner(name="Jordan", available_minutes=90, preferences=["morning walks"])

    mochi = Pet(name="Mochi", species="dog", special_needs="needs daily joint supplement")
    whiskers = Pet(name="Whiskers", species="cat")
    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    # --- Tasks added DELIBERATELY OUT OF ORDER ---
    whiskers.add_task(Task(
        title="Laser pointer play",
        description="Interactive play session with laser toy",
        duration_minutes=15, priority="low",
        category="enrichment", frequency="as_needed",
    ))
    mochi.add_task(Task(
        title="Fetch in the yard",
        description="Play fetch for enrichment and energy burn",
        duration_minutes=20, priority="medium",
        category="enrichment", frequency="daily",
        preferred_time="17:00",
    ))
    whiskers.add_task(Task(
        title="Litter box cleanup",
        description="Scoop and refresh litter",
        duration_minutes=10, priority="medium",
        category="grooming", frequency="daily",
        preferred_time="08:00",
    ))
    mochi.add_task(Task(
        title="Joint supplement",
        description="Give glucosamine chew with breakfast",
        duration_minutes=5, priority="high",
        category="medical", frequency="daily",
        preferred_time="07:30",
    ))
    whiskers.add_task(Task(
        title="Wet food breakfast",
        description="Serve half a can of wet food",
        duration_minutes=5, priority="high",
        category="feeding", frequency="daily",
        preferred_time="06:30",
    ))
    mochi.add_task(Task(
        title="Morning walk",
        description="30-minute walk around the neighbourhood",
        duration_minutes=30, priority="high",
        category="exercise", frequency="daily",
        preferred_time="07:00",
    ))

    scheduler = Scheduler(owner)

    # --- 1. Raw insertion order ---
    print("=" * 58)
    print("  📝  TASKS IN RAW INSERTION ORDER")
    print("=" * 58)
    print_tasks(owner)

    # --- 2. Sorted by preferred time ---
    print()
    print("=" * 58)
    print("  🕐  SORTED BY PREFERRED TIME")
    print("=" * 58)
    for pet, task in scheduler.sort_by_time():
        time_str = task.preferred_time or "no time set"
        print(f"  [{pet.name}] {task.title} @ {time_str}")

    # --- 3. Filter by category ---
    print()
    print("=" * 58)
    print("  🏷️   FILTER BY CATEGORY")
    print("=" * 58)
    for cat in ("enrichment", "medical", "feeding"):
        for pet in owner.pets:
            matches = pet.tasks_by_category(cat)
            if matches:
                print(f"  [{pet.name}] {cat}: {[t.title for t in matches]}")

    # --- 4. Generate DAY 1 schedule ---
    schedule = scheduler.generate_schedule()
    print()
    print("=" * 58)
    print("  🐾  DAY 1 — SCHEDULE")
    print("=" * 58)
    print()
    print(scheduler.explain_schedule(schedule))

    # --- 5. Complete all scheduled tasks ---
    print()
    print("=" * 58)
    print("  ✅  MARKING ALL SCHEDULED TASKS COMPLETE")
    print("=" * 58)
    scheduler.mark_scheduled_complete()
    print_tasks(owner)
    print()
    print("  Notice: daily/weekly tasks are PENDING again (auto-renewed).")
    print("  The as_needed task (Laser pointer play) stays DONE.")

    # --- 6. Generate DAY 2 schedule ---
    schedule2 = scheduler.generate_schedule()
    print()
    print("=" * 58)
    print("  🐾  DAY 2 — SCHEDULE (recurring tasks reappear)")
    print("=" * 58)
    print()
    print(scheduler.explain_schedule(schedule2))

    # --- 7. Complete a single recurring task manually ---
    print()
    print("=" * 58)
    print("  🔁  COMPLETE A SINGLE RECURRING TASK MANUALLY")
    print("=" * 58)
    print("  Completing 'Morning walk' for Mochi ...")
    mochi.complete_task("Morning walk")
    print_tasks(owner)
    print()
    print("  'Morning walk' was daily → auto-renewed as pending.")

    # --- 8. Conflict detection ---
    print()
    print("=" * 58)
    print("  🔥  CONFLICT DETECTION DEMO")
    print("=" * 58)
    print()
    print("  Adding two tasks that overlap at 07:00 ...")
    mochi.add_task(Task(
        title="Teeth brushing",
        description="Brush Mochi's teeth after breakfast",
        duration_minutes=10, priority="medium",
        category="grooming", frequency="daily",
        preferred_time="07:10",
    ))
    whiskers.add_task(Task(
        title="Morning cuddles",
        description="Bonding time with Whiskers",
        duration_minutes=20, priority="low",
        category="enrichment", frequency="daily",
        preferred_time="07:00",
    ))
    print()
    print("  Current preferred-time tasks:")
    for pet, task in scheduler.sort_by_time():
        if task.preferred_time:
            h, m = task.preferred_time.split(":")
            start = int(h) * 60 + int(m)
            end = start + task.duration_minutes
            print(
                f"    [{pet.name}] {task.title}  "
                f"{task.preferred_time}–{end // 60:02d}:{end % 60:02d}"
            )
    print()

    conflicts = scheduler.detect_conflicts()
    if conflicts:
        print("  Warnings returned by detect_conflicts():")
        for w in conflicts:
            print(f"    {w}")
    else:
        print("  No conflicts detected.")

    print()
    schedule3 = scheduler.generate_schedule()
    print(scheduler.explain_schedule(schedule3))


if __name__ == "__main__":
    main()
