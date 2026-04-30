import time
from datetime import datetime

from app import storage
from app.config import DEFAULT_INTERVAL_SEC


class AppState:
    def __init__(self):
        self.data = storage.load_today()
        self.timer = None
        self.main_win = None
        self.reminder_open = False
        self.interval_sec = DEFAULT_INTERVAL_SEC
        self.theme = "dark"

state = AppState()


# ── Utilities ─────────────────────────────────────────────────────────────────
def make_task(text):
    return {
        "id": int(time.time() * 1000), 
        "text": text.strip(), 
        "done": False,
        "created_at": datetime.now().isoformat(),
        "completed_at": None
    }

def save_and_refresh():
    storage.save_today(state.data)
    if state.main_win and state.main_win.winfo_exists():
        state.main_win.refresh()
