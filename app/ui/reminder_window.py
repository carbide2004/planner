import tkinter as tk
from datetime import datetime

from app import config
from app import task_service
from app.resources import get_resource_path
from app.state import state
from app.ui import theme


class ReminderWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        state.reminder_open = True

        self.title("时间到了")
        self.iconbitmap(get_resource_path(config.ICON_FILENAME))
        self.configure(bg=theme.BG)
        self.resizable(False, False)

        # Force topmost + grab (blocks other windows)
        self.attributes("-topmost", True)
        self.grab_set()
        self.focus_force()
        self.protocol("WM_DELETE_WINDOW", self._dismiss)

        self._build()
        self._center()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=theme.ACCENT, height=4)
        hdr.pack(fill="x")

        body = tk.Frame(self, bg=theme.BG, padx=32, pady=28)
        body.pack(fill="both", expand=True)

        now_str = datetime.now().strftime("%H:%M")
        tk.Label(body, text=now_str, font=("Courier New", 42, "bold"),
                 bg=theme.BG, fg=theme.ACCENT).pack(anchor="w")

        tk.Label(body, text=f"{state.interval_sec // 60}分钟过去了。", font=("Microsoft YaHei", 13),
                 bg=theme.BG, fg=theme.TEXT_DIM).pack(anchor="w", pady=(0, 20))

        # Pending tasks
        pending = task_service.get_pending_tasks(state.data)

        if not pending:
            tk.Label(body, text="✦ 今日任务已全部完成", font=("Microsoft YaHei", 12),
                     bg=theme.BG, fg=theme.ACCENT).pack(anchor="w", pady=8)
        else:
            tk.Label(body, text=f"剩余 {len(pending)} 项任务", font=("Microsoft YaHei", 10),
                     bg=theme.BG, fg=theme.TEXT_DIM).pack(anchor="w", pady=(0, 10))

            task_frame = tk.Frame(body, bg=theme.SURFACE, bd=0, relief="flat")
            task_frame.pack(fill="x", pady=(0, 20))

            for i, task in enumerate(pending):
                row = tk.Frame(task_frame, bg=theme.SURFACE, pady=0)
                row.pack(fill="x")

                # separator
                if i > 0:
                    sep = tk.Frame(task_frame, bg=theme.BORDER, height=1)
                    sep.pack(fill="x")

                num = tk.Label(row, text=f"{i+1:02d}", font=("Courier New", 10),
                               bg=theme.SURFACE, fg=theme.ACCENT_DIM, width=3, anchor="e",
                               padx=12, pady=10)
                num.pack(side="left")

                tk.Label(row, text=task["text"], font=("Microsoft YaHei", 11),
                         bg=theme.SURFACE, fg=theme.TEXT, anchor="w", padx=12, pady=10,
                         wraplength=340, justify="left").pack(side="left", fill="x", expand=True)

        # Dismiss button
        btn = tk.Button(body, text="继续专注  →",
                        font=("Microsoft YaHei", 11, "bold"),
                        bg=theme.ACCENT, fg="#0f0f0f",
                        activebackground=theme.ACCENT_DIM, activeforeground="#0f0f0f",
                        bd=0, padx=24, pady=10, cursor="hand2",
                        command=self._dismiss)
        btn.pack(anchor="e")

    def _center(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"+{x}+{y}")

    def _dismiss(self):
        state.reminder_open = False
        self.grab_release()
        self.destroy()


# ── Plan input window ─────────────────────────────────────────────────────────
