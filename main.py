"""
main.py — Demo script testing sorting, filtering, recurring tasks, and conflicts.
"""

from pawpal_system import Task, Pet, Owner, Scheduler

# ── Setup ─────────────────────────────────────────────────────────────────────
owner = Owner(name="Jordan")

mochi = Pet(name="Mochi", species="dog")
luna  = Pet(name="Luna",  species="cat")

# Tasks added OUT OF ORDER to prove sorting works
mochi.add_task(Task(description="Evening walk",      time="6:00 PM", frequency="daily"))
mochi.add_task(Task(description="Breakfast feeding", time="8:00 AM", frequency="daily"))
mochi.add_task(Task(description="Morning walk",      time="7:00 AM", frequency="daily"))

luna.add_task(Task(description="Medication",         time="9:00 AM", frequency="daily"))
luna.add_task(Task(description="Playtime",           time="6:00 PM", frequency="weekly"))
# Conflict: Luna has a task at the same time as Mochi's Evening walk
luna.add_task(Task(description="Grooming",           time="6:00 PM", frequency="as needed"))

owner.add_pet(mochi)
owner.add_pet(luna)

scheduler = Scheduler(owner=owner)

# ── 1. Sorted Schedule ────────────────────────────────────────────────────────
scheduler.print_schedule()

# ── 2. Filtering ──────────────────────────────────────────────────────────────
print("--- Mochi's tasks only ---")
for pet, task in scheduler.filter_by_pet("Mochi"):
    print(f"  {task.time:<12} {task.description}")

print("\n--- Pending tasks (all pets) ---")
for pet, task in scheduler.get_pending_tasks():
    print(f"  [{pet.name}] {task.description}")

# Mark one task complete, then show completed filter
mochi_tasks = mochi.get_tasks()
scheduler.mark_task_complete(mochi, mochi_tasks[0])   # completes Evening walk

print("\n--- Completed tasks ---")
for pet, task in scheduler.get_completed_tasks():
    print(f"  [{pet.name}] {task.description}  (due: {task.due_date})")

# ── 3. Recurring Task ─────────────────────────────────────────────────────────
print("\n--- Recurring: Mochi's tasks after completing Evening walk ---")
for task in mochi.get_tasks():
    print(f"  {task.description:<22} due: {task.due_date}  completed: {task.completed}")

# ── 4. Conflict Detection ─────────────────────────────────────────────────────
print("\n--- Conflict Detection ---")
conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        print(f"  WARNING: {warning}")
else:
    print("  No conflicts found.")
