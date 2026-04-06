from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    # --- Owner ---
    owner = Owner(name="Jordan", available_minutes=90, preferences=["morning walks"])

    # --- Pets ---
    mochi = Pet(name="Mochi", species="dog", special_needs="needs daily joint supplement")
    whiskers = Pet(name="Whiskers", species="cat")

    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    # --- Tasks for Mochi (dog) ---
    mochi.add_task(Task(
        title="Morning walk",
        description="30-minute walk around the neighbourhood",
        duration_minutes=30,
        priority="high",
        category="exercise",
        frequency="daily",
    ))
    mochi.add_task(Task(
        title="Joint supplement",
        description="Give glucosamine chew with breakfast",
        duration_minutes=5,
        priority="high",
        category="medical",
        frequency="daily",
    ))
    mochi.add_task(Task(
        title="Fetch in the yard",
        description="Play fetch for enrichment and energy burn",
        duration_minutes=20,
        priority="medium",
        category="enrichment",
        frequency="daily",
    ))

    # --- Tasks for Whiskers (cat) ---
    whiskers.add_task(Task(
        title="Wet food breakfast",
        description="Serve half a can of wet food",
        duration_minutes=5,
        priority="high",
        category="feeding",
        frequency="daily",
    ))
    whiskers.add_task(Task(
        title="Litter box cleanup",
        description="Scoop and refresh litter",
        duration_minutes=10,
        priority="medium",
        category="grooming",
        frequency="daily",
    ))
    whiskers.add_task(Task(
        title="Laser pointer play",
        description="Interactive play session with laser toy",
        duration_minutes=15,
        priority="low",
        category="enrichment",
        frequency="as_needed",
    ))

    # --- Generate and print schedule ---
    scheduler = Scheduler(owner)
    schedule = scheduler.generate_schedule()

    print("=" * 50)
    print("  🐾  TODAY'S SCHEDULE")
    print("=" * 50)
    print()
    print(scheduler.explain_schedule(schedule))
    print()

    # --- Per-pet completion summary ---
    print("-" * 50)
    for pet in owner.pets:
        print(pet.completion_summary())


if __name__ == "__main__":
    main()
