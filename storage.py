import json
import sys, os
from datetime import date, timedelta


def get_base_dir():
    if getattr(sys, 'frozen', False):
        # 打包后：exe 所在目录
        return os.path.dirname(sys.executable)
    else:
        # 开发时：脚本所在目录
        return os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(get_base_dir(), "data", f"{str(date.today())}.json")
YESTERDAY_DATA_FILE = os.path.join(get_base_dir(), "data", f"{str(date.today() - timedelta(days=1))}.json")

def _empty_day():
    return {"date": str(date.today()), "tasks": []}

def _load_yesterday():
    try:
        with open(YESTERDAY_DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("date") != str(date.today() - timedelta(days=1)):
            return _empty_day()
        data['tasks'] = [t for t in data['tasks'] if not t['done']]
        return data
    except Exception:
        return _empty_day()

def load_today():
    """Load today's tasks. If file missing or date mismatch, return empty."""
    if not os.path.exists(DATA_FILE):
        if os.path.exists(YESTERDAY_DATA_FILE):
            return _load_yesterday()
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

def get_recent_stats(days=7):
    stats = []
    base_dir = os.path.join(get_base_dir(), "data")
    for i in range(days - 1, -1, -1):
        d = date.today() - timedelta(days=i)
        file_path = os.path.join(base_dir, f"{str(d)}.json")
        completed = 0
        total = 0
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                tasks = data.get("tasks", [])
                total = len(tasks)
                completed = sum(1 for t in tasks if t.get("done", False))
            except Exception:
                pass
        stats.append((d.strftime("%m-%d"), completed, total))
    return stats
