"""
PawPal+ Logic Layer
Backend classes for the pet care planning system.
"""

from datetime import datetime, timedelta


class Task:
    """Represents a single pet care activity."""

    def __init__(self, description: str, time: str, frequency: str = "daily",
                 due_date: str = None):
        self.description = description   # e.g. "Morning walk"
        self.time = time                 # e.g. "8:00 AM"
        self.frequency = frequency       # "daily", "weekly", "as needed"
        self.completed = False
        # due_date stored as "YYYY-MM-DD"; defaults to today
        self.due_date = due_date or datetime.today().strftime("%Y-%m-%d")

    def mark_complete(self) -> None:
        self.completed = True

    def mark_incomplete(self) -> None:
        self.completed = False

    def next_occurrence(self) -> "Task":
        """
        Returns a new Task for the next occurrence based on frequency.
        daily  → due_date + 1 day
        weekly → due_date + 7 days
        as needed → no recurrence, returns None
        """
        current = datetime.strptime(self.due_date, "%Y-%m-%d")
        if self.frequency == "daily":
            next_date = current + timedelta(days=1)
        elif self.frequency == "weekly":
            next_date = current + timedelta(weeks=1)
        else:
            return None
        return Task(
            description=self.description,
            time=self.time,
            frequency=self.frequency,
            due_date=next_date.strftime("%Y-%m-%d"),
        )

    def __repr__(self) -> str:
        status = "done" if self.completed else "pending"
        return f"Task('{self.description}' @ {self.time}, {self.frequency}, {status})"


class Pet:
    """Stores pet details and owns a list of tasks."""

    def __init__(self, name: str, species: str):
        self.name = name
        self.species = species
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        self.tasks.remove(task)

    def get_tasks(self) -> list[Task]:
        return self.tasks


class Owner:
    """Manages multiple pets and provides access to all their tasks."""

    def __init__(self, name: str):
        self.name = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Returns a flat list of (pet, task) pairs across all pets."""
        result = []
        for pet in self.pets:
            for task in pet.get_tasks():
                result.append((pet, task))
        return result


class Scheduler:
    """Retrieves, organizes, and manages tasks across all of an owner's pets."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Asks the Owner for every (pet, task) pair."""
        return self.owner.get_all_tasks()

    # ── Sorting ───────────────────────────────────────────────────────────────

    def sort_by_time(self) -> list[tuple[Pet, Task]]:
        """Returns all tasks sorted chronologically using time string as key."""
        return sorted(
            self.get_all_tasks(),
            key=lambda pair: datetime.strptime(pair[1].time, "%I:%M %p")
            if self._valid_time(pair[1].time) else datetime.min
        )

    def _valid_time(self, time_str: str) -> bool:
        try:
            datetime.strptime(time_str, "%I:%M %p")
            return True
        except ValueError:
            return False

    # ── Filtering ─────────────────────────────────────────────────────────────

    def get_pending_tasks(self) -> list[tuple[Pet, Task]]:
        """Returns only tasks that are not yet completed."""
        return [(pet, task) for pet, task in self.get_all_tasks()
                if not task.completed]

    def get_completed_tasks(self) -> list[tuple[Pet, Task]]:
        """Returns only tasks that are completed."""
        return [(pet, task) for pet, task in self.get_all_tasks()
                if task.completed]

    def filter_by_pet(self, pet_name: str) -> list[tuple[Pet, Task]]:
        """Returns tasks belonging to a specific pet (case-insensitive)."""
        return [(pet, task) for pet, task in self.get_all_tasks()
                if pet.name.lower() == pet_name.lower()]

    # ── Recurring Tasks ───────────────────────────────────────────────────────

    def mark_task_complete(self, pet: Pet, task: Task) -> Task | None:
        """
        Marks a task complete. If it recurs (daily/weekly), adds the next
        occurrence back to the pet and returns it. Returns None otherwise.
        """
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task:
            pet.add_task(next_task)
        return next_task

    # ── Conflict Detection ────────────────────────────────────────────────────

    def detect_conflicts(self) -> list[str]:
        """
        Checks for tasks scheduled at the same time across all pets.
        Returns a list of warning strings (empty list = no conflicts).
        """
        warnings = []
        seen: dict[str, list[tuple[Pet, Task]]] = {}

        for pet, task in self.get_all_tasks():
            key = task.time  # group by raw time string
            seen.setdefault(key, []).append((pet, task))

        for time_slot, pairs in seen.items():
            if len(pairs) > 1:
                names = ", ".join(
                    f"[{pet.name}] {task.description}" for pet, task in pairs
                )
                warnings.append(f"CONFLICT at {time_slot}: {names}")

        return warnings

    # ── Display ───────────────────────────────────────────────────────────────

    def print_schedule(self) -> None:
        """Prints Today's Schedule to the terminal."""
        tasks = self.sort_by_time()
        print(f"\n{'='*40}")
        print(f"  Today's Schedule for {self.owner.name}")
        print(f"{'='*40}")
        for pet, task in tasks:
            status = "[x]" if task.completed else "[ ]"
            print(f"  {status} {task.time:<12} [{pet.name}] {task.description}"
                  f"  ({task.frequency})")
        print(f"{'='*40}\n")
