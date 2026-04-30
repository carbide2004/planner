import tkinter as tk

from app import config, task_service
from app.resources import get_resource_path
from app.state import state
from app.ui import theme


class PlanWindow(tk.Toplevel):
    def __init__(self, master, on_save=None):
        super().__init__(master)
        self.on_save = on_save
        self.title("今日计划")
        self.iconbitmap(get_resource_path(config.ICON_FILENAME))
        self.configure(bg=theme.BG)
        self.resizable(False, False)
        self.grab_set()
        self.focus_force()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._build()
        self._center()

    def _build(self):
        hdr = tk.Frame(self, bg=theme.ACCENT, height=4)
        hdr.pack(fill="x")

        body = tk.Frame(self, bg=theme.BG, padx=32, pady=28)
        body.pack(fill="both", expand=True)

        from datetime import date
        date_str = date.today().strftime("%Y年%m月%d日")
        tk.Label(body, text=date_str, font=("Courier New", 11),
                 bg=theme.BG, fg=theme.TEXT_DIM).pack(anchor="w")
        tk.Label(body, text="今天要做什么？", font=("Microsoft YaHei", 16, "bold"),
                 bg=theme.BG, fg=theme.TEXT).pack(anchor="w", pady=(4, 16))

        tk.Label(body, text="每行一个任务", font=("Microsoft YaHei", 10),
                 bg=theme.BG, fg=theme.TEXT_DIM).pack(anchor="w", pady=(0, 6))

        # Pre-fill existing tasks if editing
        existing = "\n".join(t["text"] for t in state.data["tasks"])

        self.text = tk.Text(body, width=42, height=12,
                            font=("Microsoft YaHei", 11),
                            bg=theme.SURFACE, fg=theme.TEXT, insertbackground=theme.ACCENT,
                            relief="flat", bd=0, padx=12, pady=10,
                            selectbackground=theme.ACCENT_DIM)
        self.text.pack(fill="x", pady=(0, 20))
        if existing:
            self.text.insert("1.0", existing)
        self.text.focus_set()

        btn_row = tk.Frame(body, bg=theme.BG)
        btn_row.pack(fill="x")

        tk.Button(btn_row, text="取消",
                  font=("Microsoft YaHei", 10),
                  bg=theme.SURFACE2, fg=theme.TEXT_DIM,
                  activebackground=theme.BORDER, activeforeground=theme.TEXT,
                  bd=0, padx=16, pady=8, cursor="hand2",
                  command=self._on_close).pack(side="left")

        tk.Button(btn_row, text="保存计划  ✓",
                  font=("Microsoft YaHei", 11, "bold"),
                  bg=theme.ACCENT, fg="#0f0f0f",
                  activebackground=theme.ACCENT_DIM, activeforeground="#0f0f0f",
                  bd=0, padx=20, pady=8, cursor="hand2",
                  command=self._save).pack(side="right")

    def _save(self):
        raw = self.text.get("1.0", "end").strip()
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        if not lines:
            return

        task_service.replace_tasks_from_lines(lines)
        if state.main_win and state.main_win.winfo_exists():
            state.main_win.refresh()
        self.grab_release()
        self.destroy()
        if self.on_save:
            self.on_save()

    def _on_close(self):
        self.grab_release()
        self.destroy()

    def _center(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"+{x}+{y}")


# ── Custom Interval window ────────────────────────────────────────────────────
