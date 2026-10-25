from datetime import date

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan your pets' care for the day based on your time and each task's priority.")

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Streamlit reruns this whole script on every click, so the Owner lives in
# session_state. It is only created the first time; after that we reuse it.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", available_minutes=60)

owner: Owner = st.session_state.owner

# --- Owner -----------------------------------------------------------------
st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner.name = st.text_input("Owner name", value=owner.name)
with col2:
    owner.available_minutes = st.number_input(
        "Time available today (minutes)", min_value=0, max_value=1440, value=owner.available_minutes
    )

st.divider()

# --- Pets ------------------------------------------------------------------
st.subheader("Pets")
with st.form("add_pet", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col3:
        age = st.number_input("Age", min_value=0, max_value=40, value=1)

    if st.form_submit_button("Add pet"):
        if not pet_name.strip():
            st.error("Please enter a pet name.")
        else:
            try:
                owner.add_pet(Pet(pet_name.strip(), species, int(age)))
                st.success(f"Added {pet_name.strip()}!")
            except ValueError as error:
                st.error(str(error))

if owner.pets:
    st.table([{"Name": p.name, "Species": p.species, "Age": p.age, "Tasks": len(p.tasks)} for p in owner.pets])
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Tasks -----------------------------------------------------------------
st.subheader("Tasks")
if not owner.pets:
    st.caption("Add a pet first, then you can give it tasks.")
else:
    with st.form("add_task", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            task_pet = st.selectbox("Pet", [p.name for p in owner.pets])
            task_title = st.text_input("Task title", placeholder="Morning walk")
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        with col2:
            preferred_time = st.time_input("Preferred time (optional)", value=None, step=900)
            frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])
            day_name = st.selectbox("Day (weekly tasks only)", DAYS)

        if st.form_submit_button("Add task"):
            if not task_title.strip():
                st.error("Please enter a task title.")
            else:
                owner.get_pet(task_pet).add_task(
                    Task(
                        owner.new_task_id(),
                        task_title.strip(),
                        int(duration),
                        priority,
                        preferred_time=preferred_time,
                        frequency=frequency,
                        day_of_week=DAYS.index(day_name) if frequency == "weekly" else None,
                    )
                )
                st.success(f"Added '{task_title.strip()}' for {task_pet}.")

    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.table([
            {
                "Pet": t.pet_name,
                "Task": t.title,
                "Time": f"{t.preferred_time:%H:%M}" if t.preferred_time else "Anytime",
                "Minutes": t.duration_minutes,
                "Priority": t.priority,
                "Repeats": t.frequency if t.frequency != "weekly" else f"weekly ({DAYS[t.day_of_week]})",
            }
            for t in all_tasks
        ])
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# --- Schedule --------------------------------------------------------------
st.subheader("Today's Schedule")

if st.button("Generate schedule"):
    today = date.today()
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan(today)

    if not plan and not scheduler.skipped:
        st.info("No tasks are due today.")
    else:
        used = sum(t.duration_minutes for t in plan)
        st.caption(f"{today:%A, %B %d} · {used} of {owner.available_minutes} minutes planned")

        if plan:
            st.table([
                {
                    "Time": f"{t.preferred_time:%H:%M}" if t.preferred_time else "Anytime",
                    "Task": t.title,
                    "Pet": t.pet_name,
                    "Minutes": t.duration_minutes,
                    "Priority": t.priority,
                    "Why": scheduler.reasons[t.task_id],
                }
                for t in plan
            ])

        for t in scheduler.skipped:
            st.warning(f"Not scheduled: {t.title} ({t.pet_name}): {scheduler.reasons[t.task_id]}")

        for conflict in scheduler.detect_conflicts(plan):
            st.error(f"Time conflict: {conflict}")
