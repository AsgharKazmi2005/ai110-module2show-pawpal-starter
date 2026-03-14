"""
Automated test suite for PawPal+ core scheduling logic.
Covers: sorting, recurrence, conflict detection, filtering, and edge cases.
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet, Owner, Scheduler


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_scheduler(*pets):
    """Create an Owner + Scheduler pre-loaded with the given Pet objects."""
    owner = Owner(name="Jordan")
    for pet in pets:
        owner.add_pet(pet)
    return Scheduler(owner=owner)


# ── Task: mark_complete ───────────────────────────────────────────────────────

def test_mark_complete_changes_status():
    """Happy path: completed starts False, becomes True after mark_complete."""
    task = Task(description="Morning walk", time="7:00 AM")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_mark_incomplete_resets_status():
    """mark_incomplete brings a completed task back to pending."""
    task = Task(description="Feeding", time="8:00 AM")
    task.mark_complete()
    task.mark_incomplete()
    assert task.completed is False


# ── Pet: task management ──────────────────────────────────────────────────────

def test_add_task_increases_count():
    """Adding a task to a Pet increases its task list by 1."""
    pet = Pet(name="Mochi", species="dog")
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task(description="Walk", time="7:00 AM"))
    assert len(pet.get_tasks()) == 1


def test_pet_with_no_tasks_returns_empty_list():
    """Edge case: a fresh Pet has an empty task list, not None."""
    pet = Pet(name="Luna", species="cat")
    result = pet.get_tasks()
    assert result == []


# ── Scheduler: sorting ────────────────────────────────────────────────────────

def test_sort_by_time_returns_chronological_order():
    """Tasks added out-of-order must come back sorted earliest → latest."""
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(description="Evening walk",    time="6:00 PM"))
    pet.add_task(Task(description="Lunch treat",     time="12:00 PM"))
    pet.add_task(Task(description="Morning walk",    time="7:00 AM"))
    pet.add_task(Task(description="Breakfast",       time="8:00 AM"))

    scheduler = make_scheduler(pet)
    sorted_tasks = scheduler.sort_by_time()
    times = [task.time for _, task in sorted_tasks]

    assert times == ["7:00 AM", "8:00 AM", "12:00 PM", "6:00 PM"]


def test_sort_across_multiple_pets():
    """Sorting works correctly when tasks come from different pets."""
    mochi = Pet(name="Mochi", species="dog")
    luna  = Pet(name="Luna",  species="cat")
    mochi.add_task(Task(description="Walk",       time="9:00 AM"))
    luna.add_task( Task(description="Medication", time="7:30 AM"))

    scheduler = make_scheduler(mochi, luna)
    sorted_tasks = scheduler.sort_by_time()

    assert sorted_tasks[0][1].description == "Medication"
    assert sorted_tasks[1][1].description == "Walk"


# ── Scheduler: filtering ──────────────────────────────────────────────────────

def test_get_pending_tasks_excludes_completed():
    """get_pending_tasks should not include tasks already marked complete."""
    pet = Pet(name="Mochi", species="dog")
    t1 = Task(description="Walk",    time="7:00 AM")
    t2 = Task(description="Feeding", time="8:00 AM")
    t1.mark_complete()
    pet.add_task(t1)
    pet.add_task(t2)

    scheduler = make_scheduler(pet)
    pending = [task.description for _, task in scheduler.get_pending_tasks()]

    assert "Walk" not in pending
    assert "Feeding" in pending


def test_filter_by_pet_is_case_insensitive():
    """filter_by_pet('mochi') should match a pet named 'Mochi'."""
    mochi = Pet(name="Mochi", species="dog")
    luna  = Pet(name="Luna",  species="cat")
    mochi.add_task(Task(description="Walk",       time="7:00 AM"))
    luna.add_task( Task(description="Medication", time="9:00 AM"))

    scheduler = make_scheduler(mochi, luna)
    results = scheduler.filter_by_pet("mochi")

    assert len(results) == 1
    assert results[0][1].description == "Walk"


def test_filter_by_unknown_pet_returns_empty():
    """Edge case: filtering by a pet name that doesn't exist returns []."""
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(description="Walk", time="7:00 AM"))

    scheduler = make_scheduler(pet)
    assert scheduler.filter_by_pet("Ghost") == []


def test_owner_with_no_pets_returns_empty_schedule():
    """Edge case: an Owner with no pets produces an empty task list."""
    owner = Owner(name="Jordan")
    scheduler = Scheduler(owner=owner)
    assert scheduler.get_all_tasks() == []
    assert scheduler.sort_by_time() == []
    assert scheduler.detect_conflicts() == []


# ── Recurrence ────────────────────────────────────────────────────────────────

def test_daily_task_next_occurrence_is_tomorrow():
    """A daily task's next_occurrence should have due_date = today + 1 day."""
    today = datetime.today().strftime("%Y-%m-%d")
    tomorrow = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")

    task = Task(description="Walk", time="7:00 AM", frequency="daily", due_date=today)
    next_task = task.next_occurrence()

    assert next_task is not None
    assert next_task.due_date == tomorrow
    assert next_task.completed is False


def test_weekly_task_next_occurrence_is_7_days_later():
    """A weekly task's next_occurrence should have due_date = today + 7 days."""
    today = datetime.today().strftime("%Y-%m-%d")
    next_week = (datetime.today() + timedelta(weeks=1)).strftime("%Y-%m-%d")

    task = Task(description="Bath", time="10:00 AM", frequency="weekly", due_date=today)
    next_task = task.next_occurrence()

    assert next_task.due_date == next_week


def test_as_needed_task_has_no_next_occurrence():
    """Edge case: an 'as needed' task returns None from next_occurrence."""
    task = Task(description="Grooming", time="3:00 PM", frequency="as needed")
    assert task.next_occurrence() is None


def test_mark_task_complete_adds_recurrence_to_pet():
    """mark_task_complete on a daily task should add a new task to the pet."""
    pet = Pet(name="Mochi", species="dog")
    task = Task(description="Walk", time="7:00 AM", frequency="daily")
    pet.add_task(task)

    scheduler = make_scheduler(pet)
    scheduler.mark_task_complete(pet, task)

    tasks = pet.get_tasks()
    assert len(tasks) == 2                          # original + next occurrence
    assert tasks[0].completed is True
    assert tasks[1].completed is False


def test_mark_task_complete_no_recurrence_for_as_needed():
    """mark_task_complete on 'as needed' should NOT add a new task."""
    pet = Pet(name="Luna", species="cat")
    task = Task(description="Grooming", time="3:00 PM", frequency="as needed")
    pet.add_task(task)

    scheduler = make_scheduler(pet)
    scheduler.mark_task_complete(pet, task)

    assert len(pet.get_tasks()) == 1               # no new task added
    assert pet.get_tasks()[0].completed is True


# ── Conflict Detection ────────────────────────────────────────────────────────

def test_conflict_detected_for_same_time():
    """Two tasks at the same time should trigger a conflict warning."""
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(description="Walk",    time="6:00 PM"))
    pet.add_task(Task(description="Feeding", time="6:00 PM"))

    scheduler = make_scheduler(pet)
    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
    assert "6:00 PM" in conflicts[0]


def test_conflict_detected_across_different_pets():
    """Tasks at the same time for different pets should still conflict."""
    mochi = Pet(name="Mochi", species="dog")
    luna  = Pet(name="Luna",  species="cat")
    mochi.add_task(Task(description="Walk",      time="6:00 PM"))
    luna.add_task( Task(description="Playtime",  time="6:00 PM"))

    scheduler = make_scheduler(mochi, luna)
    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
    assert "Mochi" in conflicts[0]
    assert "Luna" in conflicts[0]


def test_no_conflict_when_times_differ():
    """Happy path: tasks at different times produce no conflicts."""
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(description="Walk",    time="7:00 AM"))
    pet.add_task(Task(description="Feeding", time="8:00 AM"))

    scheduler = make_scheduler(pet)
    assert scheduler.detect_conflicts() == []
