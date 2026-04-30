# Daily Planner

Daily Planner is a small Windows desktop planner that prompts you at a fixed interval to review today's tasks.

It is built with Python's standard `tkinter` GUI toolkit. Optional tray support is provided by `pystray` and `Pillow`.

## Features

- Daily task planning with one task per line.
- Automatic carry-over of unfinished tasks from yesterday.
- Click a task row to toggle completed / pending.
- Periodic reminder popup with configurable interval.
- Recent completion summary chart.
- Light / dark theme switch.
- Optional Windows autostart.
- Single-instance guard to avoid launching duplicate app instances.

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Data

Task data is stored as JSON files in the project-level `data/` directory:

```text
data/
  YYYY-MM-DD.json
```

Each file contains the plan for one day:

```json
{
  "date": "2026-04-30",
  "tasks": [
    {
      "id": 1777534881306,
      "text": "Example task",
      "done": false,
      "created_at": "2026-04-30T15:41:21.306586",
      "completed_at": null
    }
  ]
}
```

## Project Structure

```text
planner/
  main.py                 # Application entry point
  planner.ico             # App icon
  requirements.txt
  app/
    config.py             # App constants and paths
    resources.py          # Resource path helper for dev / PyInstaller
    storage.py            # JSON file persistence
    models.py             # Task dict construction helpers
    task_service.py       # Task business operations
    state.py              # Runtime app state
    autostart.py          # Windows registry autostart
    single_instance.py    # Single-instance lock
    ui/
      main_window.py
      plan_window.py
      reminder_window.py
      summary_window.py
      interval_window.py
      theme.py
  data/                   # Runtime task data, ignored by git
```

## Architecture Notes

- `main.py` only starts the application.
- UI modules under `app/ui/` handle presentation and user interaction.
- `app/task_service.py` owns task operations such as replacing the daily plan and toggling completion.
- `app/storage.py` only reads and writes JSON files.
- `app/state.py` keeps runtime-only state such as the active timer, selected theme, and main window reference.

## Build EXE

Install PyInstaller if needed:

```bash
pip install pyinstaller
```

Build:

```bash
pyinstaller --noconsole --onefile -i planner.ico --add-data "planner.ico;." main.py
```

The generated executable will be written to `dist/`.
