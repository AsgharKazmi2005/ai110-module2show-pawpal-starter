"""
main.py — Demo script to test PawPal+ logic in the terminal.
"""

from pawpal_system import Task, Pet, Owner, Scheduler

# --- Setup Owner ---
owner = Owner(name="Jordan")

# --- Setup Pets ---
mochi = Pet(name="Mochi", species="dog")
luna = Pet(name="Luna", species="cat")

# --- Add Tasks to Mochi (dog) ---
mochi.add_task(Task(description="Morning walk",    time="7:00 AM", frequency="daily"))
mochi.add_task(Task(description="Breakfast feeding", time="8:00 AM", frequency="daily"))

# --- Add Tasks to Luna (cat) ---
luna.add_task(Task(description="Medication",       time="9:00 AM", frequency="daily"))
luna.add_task(Task(description="Playtime",         time="6:00 PM", frequency="daily"))

# --- Register Pets with Owner ---
owner.add_pet(mochi)
owner.add_pet(luna)

# --- Run Scheduler ---
scheduler = Scheduler(owner=owner)
scheduler.print_schedule()
