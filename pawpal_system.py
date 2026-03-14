"""
PawPal+ Logic Layer
Backend classes for the pet care planning system.
"""


class Task:
    """Represents a single pet care activity."""

    def __init__(self, description: str, time: str, frequency: str = "daily"):
        self.description = description   # e.g. "Morning walk"
        self.time = time                 # e.g. "8:00 AM"
        self.frequency = frequency       # e.g. "daily", "weekly"
        self.completed = False

    def mark_complete(self) -> None:
        self.completed = True

    def mark_incomplete(self) -> None:
        pass

    def __repr__(self) -> str:
        pass


class Pet:
    """Stores pet details and owns a list of tasks."""

    def __init__(self, name: str, species: str):
        self.name = name
        self.species = species
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        pass

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

    def sort_by_time(self) -> list[tuple[Pet, Task]]:
        """Returns tasks sorted by scheduled time."""
        from datetime import datetime
        def parse_time(pair):
            try:
                return datetime.strptime(pair[1].time, "%I:%M %p")
            except ValueError:
                return datetime.min
        return sorted(self.get_all_tasks(), key=parse_time)

    def get_pending_tasks(self) -> list[tuple[Pet, Task]]:
        """Returns only tasks that are not yet completed."""
        pass

    def print_schedule(self) -> None:
        """Prints Today's Schedule to the terminal."""
        tasks = self.sort_by_time()
        print(f"\n{'='*35}")
        print(f"  Today's Schedule for {self.owner.name}")
        print(f"{'='*35}")
        for pet, task in tasks:
            status = "[x]" if task.completed else "[ ]"
            print(f"  {status} {task.time:<12} [{pet.name}] {task.description}")
        print(f"{'='*35}\n")
