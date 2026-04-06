import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ---------------------------------------------------------------------------
# Session state — the "vault" that survives reruns
# ---------------------------------------------------------------------------

if "owner" not in st.session_state:
    st.session_state.owner = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None
if "last_schedule" not in st.session_state:
    st.session_state.last_schedule = None

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.title("🐾 PawPal+")
st.caption("A pet care planning assistant that builds your daily schedule.")

# ---------------------------------------------------------------------------
# 1. Owner setup
# ---------------------------------------------------------------------------

st.subheader("1 · Owner Setup")

with st.form("owner_form"):
    owner_name = st.text_input("Owner name", value="Jordan")
    available_minutes = st.number_input(
        "Available minutes today", min_value=1, max_value=480, value=90
    )
    save_owner = st.form_submit_button("Save owner")

if save_owner:
    if st.session_state.owner is None:
        st.session_state.owner = Owner(
            name=owner_name, available_minutes=available_minutes
        )
    else:
        st.session_state.owner.name = owner_name
        st.session_state.owner.available_minutes = available_minutes
    st.session_state.scheduler = Scheduler(st.session_state.owner)

if st.session_state.owner:
    st.success(f"Owner: **{st.session_state.owner}**")

st.divider()

# ---------------------------------------------------------------------------
# 2. Add pets  →  Owner.add_pet(Pet(...))
# ---------------------------------------------------------------------------

st.subheader("2 · Pets")

if st.session_state.owner is None:
    st.info("Save an owner first.")
else:
    owner: Owner = st.session_state.owner

    with st.form("pet_form"):
        col_pname, col_species = st.columns(2)
        with col_pname:
            pet_name = st.text_input("Pet name", value="Mochi")
        with col_species:
            species = st.selectbox("Species", ["dog", "cat", "other"])
        special_needs = st.text_input("Special needs (optional)", value="")
        add_pet = st.form_submit_button("Add pet")

    if add_pet:
        try:
            owner.add_pet(
                Pet(name=pet_name, species=species, special_needs=special_needs)
            )
            st.session_state.scheduler = Scheduler(owner)
        except ValueError as e:
            st.error(str(e))

    if owner.pets:
        for pet in owner.pets:
            col_info, col_btn = st.columns([4, 1])
            with col_info:
                needs = f" — {pet.special_needs}" if pet.special_needs else ""
                st.write(f"**{pet.name}** ({pet.species}){needs}")
            with col_btn:
                if st.button("Remove", key=f"rm_pet_{pet.name}"):
                    owner.remove_pet(pet.name)
                    st.session_state.scheduler = Scheduler(owner)
                    st.rerun()
    else:
        st.info("No pets yet.")

st.divider()

# ---------------------------------------------------------------------------
# 3. Add tasks  →  Scheduler.add_task(pet_name, Task(...))
# ---------------------------------------------------------------------------

st.subheader("3 · Tasks")

if st.session_state.owner and st.session_state.owner.pets:
    pet_names = [p.name for p in st.session_state.owner.pets]

    with st.form("task_form"):
        selected_pet = st.selectbox("Add task to pet", pet_names)
        col1, col2, col3 = st.columns(3)
        with col1:
            task_title = st.text_input("Task title", value="Morning walk")
        with col2:
            duration = st.number_input(
                "Duration (min)", min_value=1, max_value=240, value=20
            )
        with col3:
            priority = st.selectbox("Priority", ["high", "medium", "low"])
        task_desc = st.text_input("Description (optional)", value="")
        col_cat, col_freq = st.columns(2)
        with col_cat:
            category = st.selectbox(
                "Category",
                ["exercise", "feeding", "medical", "grooming", "enrichment", "other"],
            )
        with col_freq:
            frequency = st.selectbox("Frequency", ["daily", "weekly", "as_needed"])
        add_task = st.form_submit_button("Add task")

    if add_task:
        try:
            st.session_state.scheduler.add_task(
                selected_pet,
                Task(
                    title=task_title,
                    description=task_desc,
                    duration_minutes=int(duration),
                    priority=priority,
                    category=category,
                    frequency=frequency,
                ),
            )
            st.success(f"Added **{task_title}** to {selected_pet}")
        except ValueError as e:
            st.error(str(e))

    for pet in st.session_state.owner.pets:
        if pet.tasks:
            st.markdown(f"**{pet.name}'s tasks** — {pet.completion_summary()}")
            for task in pet.tasks:
                col_task, col_done, col_rm = st.columns([5, 1, 1])
                with col_task:
                    status = "✅" if task.completed else "⬜"
                    st.write(
                        f"{status} {task.title} · {task.duration_minutes} min · "
                        f"{task.priority} · {task.category}"
                    )
                with col_done:
                    if not task.completed:
                        if st.button("Done", key=f"done_{pet.name}_{task.title}"):
                            task.mark_complete()
                            st.rerun()
                with col_rm:
                    if st.button("✗", key=f"rm_{pet.name}_{task.title}"):
                        pet.remove_task(task.title)
                        st.rerun()
else:
    st.info("Add an owner and pet above first.")

st.divider()

# ---------------------------------------------------------------------------
# 4. Generate schedule  →  Scheduler.generate_schedule()
# ---------------------------------------------------------------------------

st.subheader("4 · Build Schedule")

if st.button("Generate schedule"):
    scheduler: Scheduler | None = st.session_state.scheduler
    if scheduler is None:
        st.warning("Set up an owner and pets first.")
    elif not scheduler.get_all_pending():
        st.warning("Add at least one pending task before generating a schedule.")
    else:
        st.session_state.last_schedule = scheduler.generate_schedule()

if st.session_state.last_schedule:
    schedule = st.session_state.last_schedule
    st.markdown("### 📋 Today's Schedule")
    for entry in schedule:
        st.markdown(
            f"**{entry.start_minute}–{entry.end_minute()} min** · "
            f"[{entry.pet_name}] **{entry.task.title}** — _{entry.reason}_"
        )
    st.divider()
    st.markdown("### Explanation")
    st.text(st.session_state.scheduler.explain_schedule(schedule))

    if st.button("Mark all scheduled tasks complete"):
        st.session_state.scheduler.mark_scheduled_complete()
        st.session_state.last_schedule = None
        st.rerun()
