"""PawPal+ Streamlit UI.

This is the "bridge" between the user and the logic layer in pawpal_system.py.
The Owner object is kept in st.session_state so pets and tasks persist across
Streamlit's top-to-bottom reruns.
"""

import streamlit as st

from pawpal_system import Owner, Pet, Task, Priority, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# --- Application "memory" -------------------------------------------------
# Streamlit reruns this whole script on every interaction, so we only build a
# fresh Owner the first time and then reuse the one stored in session_state.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)

st.title("🐾 PawPal+")
st.caption("Plan your pets' care tasks — sorted, filtered, and conflict-checked.")

# --- Owner + pets ---------------------------------------------------------
st.subheader("👤 Owner & Pets")
owner.name = st.text_input("Owner name", value=owner.name)

with st.form("add_pet_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        new_pet_name = st.text_input("Pet name", value="")
    with col2:
        new_pet_species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet") and new_pet_name.strip():
        owner.add_pet(Pet(name=new_pet_name.strip(), species=new_pet_species))
        st.success(f"Added {new_pet_name.strip()} ({new_pet_species}).")

if owner.pets:
    st.write("**Your pets:** " + ", ".join(f"{p.name} ({p.species})" for p in owner.pets))
else:
    st.info("Add a pet to get started.")

st.divider()

# --- Add a task -----------------------------------------------------------
st.subheader("📝 Add a Task")
if owner.pets:
    with st.form("add_task_form", clear_on_submit=True):
        pet_names = [p.name for p in owner.pets]
        c1, c2 = st.columns(2)
        with c1:
            task_pet = st.selectbox("For which pet?", pet_names)
            task_title = st.text_input("Task", value="Morning walk")
            task_time = st.text_input("Time (HH:MM)", value="08:00")
        with c2:
            task_duration = st.number_input("Duration (min)", 1, 240, 20)
            task_priority = st.selectbox("Priority", ["high", "medium", "low"])
            task_freq = st.selectbox("Frequency", ["daily", "weekly", "once"])
        if st.form_submit_button("Add task"):
            pet = next(p for p in owner.pets if p.name == task_pet)
            pet.add_task(
                Task(
                    description=task_title,
                    duration=int(task_duration),
                    priority=Priority[task_priority.upper()],
                    time=task_time,
                    frequency=task_freq,
                )
            )
            st.success(f"Added '{task_title}' for {task_pet}.")
else:
    st.caption("Add a pet first, then you can add tasks.")

st.divider()

# --- Today's schedule -----------------------------------------------------
st.subheader("📅 Today's Schedule")

all_tasks = owner.get_all_tasks()
if not all_tasks:
    st.info("No tasks yet. Add one above to see your plan.")
else:
    # Show the plan ordered by time, using the Scheduler's sorting method.
    tasks = scheduler.sort_by_time()

    # Conflict warnings — surfaced prominently so the owner notices overlaps.
    warnings = scheduler.conflict_warnings()
    if warnings:
        for warning in warnings:
            st.warning(warning.replace("[!] ", ""))
    else:
        st.success("No scheduling conflicts. 🎉")

    st.table(
        [
            {
                "Time": t.time,
                "Task": t.description,
                "Pet": t.pet.name if t.pet else "?",
                "Duration": f"{t.duration} min",
                "Priority": t.priority.name.title(),
                "Frequency": t.frequency,
            }
            for t in tasks
        ]
    )
