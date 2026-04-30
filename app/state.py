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
