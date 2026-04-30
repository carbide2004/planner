from datetime import date, datetime
import time

from app import models, storage
from app.state import state


def load_today():
    state.data = storage.load_today()
    return state.data


def save_today():
    storage.save_today(state.data)


def replace_tasks_from_lines(lines):
    old_tasks = state.data.get("tasks", [])
    old_map = {task["text"]: task for task in old_tasks}
    now_iso = datetime.now().isoformat()

    state.data = {
        "date": str(date.today()),
        "tasks": [
            models.preserve_or_make_task(
                line,
                old_task=old_map.get(line),
                fallback_id=int(time.time() * 1000 + index),
                created_at=now_iso,
            )
            for index, line in enumerate(lines)
        ],
    }
    save_today()
    return state.data


def toggle_task(task_id):
    for task in state.data.get("tasks", []):
        if task.get("id") == task_id:
            task["done"] = not task.get("done", False)
            task["completed_at"] = datetime.now().isoformat() if task["done"] else None
            break
    save_today()
    return state.data


def get_pending_tasks(data=None):
    day_data = data if data is not None else state.data
    return [task for task in day_data.get("tasks", []) if not task.get("done", False)]


def is_new_day():
    data = storage.load_today()
    return data.get("date") != str(date.today()) or len(data.get("tasks", [])) == 0


def get_recent_stats(days=7):
    return storage.get_recent_stats(days)
