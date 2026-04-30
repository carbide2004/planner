import json
import os
import sys
from datetime import date, timedelta

from app import config


def get_data_dir():
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "data")
    return config.DATA_DIR


def get_day_file(day):
    return os.path.join(get_data_dir(), f"{day}.json")


def _empty_day():
    return {"date": str(date.today()), "tasks": []}


def _load_yesterday():
    yesterday = date.today() - timedelta(days=1)
    try:
        with open(get_day_file(yesterday), "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("date") != str(yesterday):
            return _empty_day()
        data["tasks"] = [task for task in data.get("tasks", []) if not task.get("done", False)]
        return data
    except Exception:
        return _empty_day()


def load_today():
    today = date.today()
    today_file = get_day_file(today)
    if not os.path.exists(today_file):
        if os.path.exists(get_day_file(today - timedelta(days=1))):
            return _load_yesterday()
        return _empty_day()
    try:
        with open(today_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("date") != str(today):
            return _empty_day()
        return data
    except Exception:
        return _empty_day()


def save_today(data):
    today_file = get_day_file(date.today())
    os.makedirs(os.path.dirname(today_file), exist_ok=True)
    with open(today_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_recent_stats(days=7):
    stats = []
    for i in range(days - 1, -1, -1):
        day = date.today() - timedelta(days=i)
        completed = 0
        total = 0
        if os.path.exists(get_day_file(day)):
            try:
                with open(get_day_file(day), "r", encoding="utf-8") as f:
                    data = json.load(f)
                tasks = data.get("tasks", [])
                total = len(tasks)
                completed = sum(1 for task in tasks if task.get("done", False))
            except Exception:
                pass
        stats.append((day.strftime("%m-%d"), completed, total))
    return stats
