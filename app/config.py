import os


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

APP_NAME = "DailyPlanner"
APP_DISPLAY_NAME = "Daily Planner"
APP_USER_MODEL_ID = "Carbide.Planner.0.1"

ICON_FILENAME = "planner.ico"

DEFAULT_INTERVAL_SEC = 30 * 60

MAIN_WINDOW_GEOMETRY = "560x580"
MAIN_WINDOW_MIN_SIZE = (400, 400)
