import time
from datetime import datetime


def make_task(text, task_id=None, created_at=None, done=False, completed_at=None):
    return {
        "id": task_id if task_id is not None else int(time.time() * 1000),
        "text": text.strip(),
        "done": done,
        "created_at": created_at or datetime.now().isoformat(),
        "completed_at": completed_at,
    }


def preserve_or_make_task(text, old_task=None, fallback_id=None, created_at=None):
    if old_task:
        return make_task(
            text,
            task_id=old_task.get("id", fallback_id),
            created_at=old_task.get("created_at", created_at),
            done=old_task.get("done", False),
            completed_at=old_task.get("completed_at"),
        )
    return make_task(text, task_id=fallback_id, created_at=created_at)
