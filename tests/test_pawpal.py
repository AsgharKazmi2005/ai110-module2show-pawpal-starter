"""
Tests for PawPal+ core logic.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet


def test_mark_complete_changes_status():
    """Calling mark_complete() should set task.completed to True."""
    task = Task(description="Morning walk", time="7:00 AM")
    assert task.completed == False
    task.mark_complete()
    assert task.completed == True


def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet should increase its task count by 1."""
    pet = Pet(name="Mochi", species="dog")
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task(description="Feeding", time="8:00 AM"))
    assert len(pet.get_tasks()) == 1
