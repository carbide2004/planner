import json
import sys, os
from datetime import date

def get_base_dir():
    if getattr(sys, 'frozen', False):
        # 打包后：exe 所在目录
        return os.path.dirname(sys.executable)
    else:
        # 开发时：脚本所在目录
        return os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(get_base_dir(), "data", f"{str(date.today())}.json")

def _empty_day():
    return {"date": str(date.today()), "tasks": []}

def load_today():
    """Load today's tasks. If file missing or date mismatch, return empty."""
    if not os.path.exists(DATA_FILE):
        return _empty_day()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("date") != str(date.today()):
            return _empty_day()
        return data
    except Exception:
        return _empty_day()

def save_today(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def is_new_day():
    data = load_today()
    return data["date"] != str(date.today()) or len(data["tasks"]) == 0

def get_pending_tasks(data):
    return [t for t in data["tasks"] if not t["done"]]
