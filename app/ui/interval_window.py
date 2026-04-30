import tkinter as tk

from app import config
from app.resources import get_resource_path
from app.state import state
from app.ui import theme


class CustomIntervalWindow(tk.Toplevel):
    def __init__(self, master, on_save):
        super().__init__(master)
        self.on_save = on_save

        self.title("自定义提醒间隔")
        self.iconbitmap(get_resource_path(config.ICON_FILENAME))
        self.configure(bg=theme.BG)
        self.resizable(False, False)
        self.grab_set()
        self.focus_force()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build()
        self._center()

    def _build(self):
        body = tk.Frame(self, bg=theme.BG, padx=24, pady=20)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="设置提醒间隔（分钟）", font=("Microsoft YaHei", 11),
                    bg=theme.BG, fg=theme.TEXT).pack(anchor="w", pady=(0, 10))

        self.entry = tk.Entry(body, width=10, font=("Courier New", 12),
                                bg=theme.SURFACE, fg=theme.TEXT, insertbackground=theme.ACCENT,
                                relief="flat", bd=0, justify="center")
        self.entry.pack(pady=(0, 20))
        self.entry.insert(0, str(state.interval_sec // 60))
        self.entry.focus_set()
        self.entry.select_range(0, 'end')

        btn_row = tk.Frame(body, bg=theme.BG)
        btn_row.pack(fill="x")

        tk.Button(btn_row, text="取消", font=("Microsoft YaHei", 10), bg=theme.SURFACE2, fg=theme.TEXT_DIM,
                    activebackground=theme.BORDER, activeforeground=theme.TEXT, bd=0, padx=16, pady=8,
                    cursor="hand2", command=self._on_close).pack(side="left")

        tk.Button(btn_row, text="确定", font=("Microsoft YaHei", 10, "bold"), bg=theme.ACCENT, fg="#0f0f0f",
                    activebackground=theme.ACCENT_DIM, activeforeground="#0f0f0f", bd=0, padx=20, pady=8,
                    cursor="hand2", command=self._save).pack(side="right")

    def _save(self):
        try:
            minutes = int(self.entry.get())
            if minutes > 0 and minutes < 1440:
                self.on_save(minutes * 60)
                self._on_close()
            else:
                from tkinter import messagebox
                messagebox.showwarning("输入无效", "间隔必须大于0分钟并小于24小时。", parent=self)
        except ValueError:
            from tkinter import messagebox
            messagebox.showerror("输入无效", "请输入一个有效的数字（分钟）。", parent=self)

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

# ── Summary window ────────────────────────────────────────────────────────────
