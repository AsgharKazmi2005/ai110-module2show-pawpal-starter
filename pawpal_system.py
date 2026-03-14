"""
PawPal+ Logic Layer
Backend classes for the pet care planning system.
"""


class Pet:
    def __init__(self, name: str, species: str, age: int, medical_notes: list[str] = None):
        self.name = name
        self.species = species
        self.age = age
        self.medical_notes = medical_notes or []

    def get_required_tasks(self) -> list:
        pass


class Owner:
    def __init__(self, name: str, available_minutes_per_day: int, preferences: list[str] = None):
        self.name = name
        self.available_minutes_per_day = available_minutes_per_day
        self.preferences = preferences or []
        self.pet = None

    def add_pet(self, pet: Pet) -> None:
        pass

    def set_availability(self, minutes: int) -> None:
        pass


class Task:
    def __init__(self, title: str, duration_minutes: int, priority: str,
                 category: str = "", is_recurring: bool = False, preferred_time_of_day: str = ""):
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.category = category
        self.is_recurring = is_recurring
        self.preferred_time_of_day = preferred_time_of_day

    def is_high_priority(self) -> bool:
        pass

    def edit(self, title: str, duration_minutes: int, priority: str) -> None:
        pass


class ScheduledTask:
    def __init__(self, task: Task, start_time: str, end_time: str, reason: str = ""):
        self.task = task
        self.start_time = start_time
        self.end_time = end_time
        self.reason = reason

    def get_summary(self) -> str:
        pass


class Schedule:
    def __init__(self, date: str):
        self.date = date
        self.items: list[ScheduledTask] = []
        self.total_duration_minutes = 0
        self.skipped_tasks: list[str] = []

    def display(self) -> str:
        pass

    def explain(self) -> str:
        pass

    def is_feasible(self) -> bool:
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet):
        self.owner = owner
        self.pet = pet
        self.total_minutes_available = owner.available_minutes_per_day
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def filter_by_priority(self, level: str) -> list[Task]:
        pass

    def sort_tasks(self) -> list[Task]:
        pass

    def generate_schedule(self) -> Schedule:
        pass
