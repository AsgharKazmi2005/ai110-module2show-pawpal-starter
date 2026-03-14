import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# ── Step 1: Session State "vault" ────────────────────────────────────────────
# Streamlit reruns top-to-bottom on every interaction.
# We only create a fresh Owner once; after that we reuse what's in the vault.

if "owner" not in st.session_state:
    st.session_state.owner = None   # set properly when the owner form is submitted

# ── Step 2: Owner Setup ───────────────────────────────────────────────────────
st.subheader("Owner Info")

with st.form("owner_form"):
    owner_name = st.text_input("Your name", value="Jordan")
    submitted_owner = st.form_submit_button("Save owner")

if submitted_owner:
    st.session_state.owner = Owner(name=owner_name)
    st.success(f"Owner '{owner_name}' saved!")

if st.session_state.owner is None:
    st.info("Enter your name above to get started.")
    st.stop()   # don't render the rest until an owner exists

owner: Owner = st.session_state.owner

# ── Step 3a: Add a Pet ────────────────────────────────────────────────────────
st.divider()
st.subheader("Add a Pet")

with st.form("pet_form"):
    pet_name = st.text_input("Pet name", value="Mochi")
    species   = st.selectbox("Species", ["dog", "cat", "other"])
    submitted_pet = st.form_submit_button("Add pet")

if submitted_pet:
    new_pet = Pet(name=pet_name, species=species)
    owner.add_pet(new_pet)          # calls Owner.add_pet() from pawpal_system.py
    st.success(f"{pet_name} the {species} added!")

# Show pets currently registered
if owner.pets:
    st.markdown("**Registered pets:** " + ", ".join(p.name for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

# ── Step 3b: Add a Task to a Pet ─────────────────────────────────────────────
st.divider()
st.subheader("Add a Task")

if not owner.pets:
    st.warning("Add a pet first before adding tasks.")
else:
    with st.form("task_form"):
        pet_choice   = st.selectbox("Assign to pet", [p.name for p in owner.pets])
        task_desc    = st.text_input("Task description", value="Morning walk")
        task_time    = st.text_input("Time (e.g. 8:00 AM)", value="8:00 AM")
        task_freq    = st.selectbox("Frequency", ["daily", "weekly", "as needed"])
        submitted_task = st.form_submit_button("Add task")

    if submitted_task:
        target_pet = next(p for p in owner.pets if p.name == pet_choice)
        new_task = Task(description=task_desc, time=task_time, frequency=task_freq)
        target_pet.add_task(new_task)   # calls Pet.add_task() from pawpal_system.py
        st.success(f"Task '{task_desc}' added to {target_pet.name}!")

    # Show all current tasks across pets
    all_pairs = owner.get_all_tasks()
    if all_pairs:
        st.markdown("**Current tasks:**")
        rows = [
            {"Pet": pet.name, "Task": task.description,
             "Time": task.time, "Frequency": task.frequency,
             "Done": task.completed}
            for pet, task in all_pairs
        ]
        st.table(rows)
    else:
        st.info("No tasks yet.")

# ── Step 3c: Generate Schedule ────────────────────────────────────────────────
st.divider()
st.subheader("Generate Schedule")

if st.button("Build today's schedule"):
    if not owner.get_all_tasks():
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(owner=owner)
        sorted_tasks = scheduler.sort_by_time()

        st.markdown(f"### Today's Schedule for {owner.name}")
        for pet, task in sorted_tasks:
            status = "✅" if task.completed else "⬜"
            st.markdown(f"{status} **{task.time}** &nbsp;|&nbsp; [{pet.name}] {task.description} *({task.frequency})*")
