import tkinter as tk
from tkinter import font as tkfont
import threading
import time
import sys
import os
from datetime import datetime

import storage
import autostart

# ── Palette ──────────────────────────────────────────────────────────────────
BG          = "#0f0f0f"
SURFACE     = "#1a1a1a"
SURFACE2    = "#242424"
BORDER      = "#2e2e2e"
ACCENT      = "#c8f53a"        # sharp lime-yellow
ACCENT_DIM  = "#8fb028"
TEXT        = "#e8e8e8"
TEXT_DIM    = "#666666"
DONE_COLOR  = "#3a3a3a"
DONE_TEXT   = "#4a4a4a"
RED         = "#ff4444"

INTERVAL_SEC = 30 * 60        # default interval: 30 minutes

def get_resource_path(relative_path):
    # PyInstaller 创建临时文件夹，将路径存储在 _MEIPASS 中
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# ── Shared state ──────────────────────────────────────────────────────────────
class AppState:
    def __init__(self):
        self.data = storage.load_today()
        self.timer = None
        self.main_win = None
        self.reminder_open = False
        self.interval_sec = INTERVAL_SEC

state = AppState()


# ── Utilities ─────────────────────────────────────────────────────────────────
def make_task(text):
    return {"id": int(time.time() * 1000), "text": text.strip(), "done": False}

def save_and_refresh():
    storage.save_today(state.data)
    if state.main_win and state.main_win.winfo_exists():
        state.main_win.refresh()


# ── Reminder popup ────────────────────────────────────────────────────────────
class ReminderWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        state.reminder_open = True

        self.title("时间到了")
        self.iconbitmap(get_resource_path('planner.ico'))
        self.configure(bg=BG)
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
        hdr = tk.Frame(self, bg=ACCENT, height=4)
        hdr.pack(fill="x")

        body = tk.Frame(self, bg=BG, padx=32, pady=28)
        body.pack(fill="both", expand=True)

        now_str = datetime.now().strftime("%H:%M")
        tk.Label(body, text=now_str, font=("Courier New", 42, "bold"),
                 bg=BG, fg=ACCENT).pack(anchor="w")

        tk.Label(body, text="三十分钟过去了。", font=("Microsoft YaHei", 13),
                 bg=BG, fg=TEXT_DIM).pack(anchor="w", pady=(0, 20))

        # Pending tasks
        pending = storage.get_pending_tasks(state.data)

        if not pending:
            tk.Label(body, text="✦ 今日任务已全部完成", font=("Microsoft YaHei", 12),
                     bg=BG, fg=ACCENT).pack(anchor="w", pady=8)
        else:
            tk.Label(body, text=f"剩余 {len(pending)} 项任务", font=("Microsoft YaHei", 10),
                     bg=BG, fg=TEXT_DIM).pack(anchor="w", pady=(0, 10))

            task_frame = tk.Frame(body, bg=SURFACE, bd=0, relief="flat")
            task_frame.pack(fill="x", pady=(0, 20))

            for i, task in enumerate(pending):
                row = tk.Frame(task_frame, bg=SURFACE, pady=0)
                row.pack(fill="x")

                # separator
                if i > 0:
                    sep = tk.Frame(task_frame, bg=BORDER, height=1)
                    sep.pack(fill="x")

                num = tk.Label(row, text=f"{i+1:02d}", font=("Courier New", 10),
                               bg=SURFACE, fg=ACCENT_DIM, width=3, anchor="e",
                               padx=12, pady=10)
                num.pack(side="left")

                tk.Label(row, text=task["text"], font=("Microsoft YaHei", 11),
                         bg=SURFACE, fg=TEXT, anchor="w", padx=12, pady=10,
                         wraplength=340, justify="left").pack(side="left", fill="x", expand=True)

        # Dismiss button
        btn = tk.Button(body, text="继续专注  →",
                        font=("Microsoft YaHei", 11, "bold"),
                        bg=ACCENT, fg="#0f0f0f",
                        activebackground=ACCENT_DIM, activeforeground="#0f0f0f",
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
class PlanWindow(tk.Toplevel):
    def __init__(self, master, on_save=None):
        super().__init__(master)
        self.on_save = on_save
        self.title("今日计划")
        self.iconbitmap(get_resource_path('planner.ico'))
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()
        self.focus_force()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._build()
        self._center()

    def _build(self):
        hdr = tk.Frame(self, bg=ACCENT, height=4)
        hdr.pack(fill="x")

        body = tk.Frame(self, bg=BG, padx=32, pady=28)
        body.pack(fill="both", expand=True)

        from datetime import date
        date_str = date.today().strftime("%Y年%m月%d日")
        tk.Label(body, text=date_str, font=("Courier New", 11),
                 bg=BG, fg=TEXT_DIM).pack(anchor="w")
        tk.Label(body, text="今天要做什么？", font=("Microsoft YaHei", 16, "bold"),
                 bg=BG, fg=TEXT).pack(anchor="w", pady=(4, 16))

        tk.Label(body, text="每行一个任务", font=("Microsoft YaHei", 10),
                 bg=BG, fg=TEXT_DIM).pack(anchor="w", pady=(0, 6))

        # Pre-fill existing tasks if editing
        existing = "\n".join(t["text"] for t in state.data["tasks"])

        self.text = tk.Text(body, width=42, height=12,
                            font=("Microsoft YaHei", 11),
                            bg=SURFACE, fg=TEXT, insertbackground=ACCENT,
                            relief="flat", bd=0, padx=12, pady=10,
                            selectbackground=ACCENT_DIM)
        self.text.pack(fill="x", pady=(0, 20))
        if existing:
            self.text.insert("1.0", existing)
        self.text.focus_set()

        btn_row = tk.Frame(body, bg=BG)
        btn_row.pack(fill="x")

        tk.Button(btn_row, text="取消",
                  font=("Microsoft YaHei", 10),
                  bg=SURFACE2, fg=TEXT_DIM,
                  activebackground=BORDER, activeforeground=TEXT,
                  bd=0, padx=16, pady=8, cursor="hand2",
                  command=self._on_close).pack(side="left")

        tk.Button(btn_row, text="保存计划  ✓",
                  font=("Microsoft YaHei", 11, "bold"),
                  bg=ACCENT, fg="#0f0f0f",
                  activebackground=ACCENT_DIM, activeforeground="#0f0f0f",
                  bd=0, padx=20, pady=8, cursor="hand2",
                  command=self._save).pack(side="right")

    def _save(self):
        raw = self.text.get("1.0", "end").strip()
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        if not lines:
            return

        from datetime import date
        # Preserve done status for tasks with same text
        old_map = {t["text"]: t["done"] for t in state.data["tasks"]}
        state.data = {
            "date": str(date.today()),
            "tasks": [{"id": int(time.time()*1000 + i),
                       "text": l,
                       "done": old_map.get(l, False)} for i, l in enumerate(lines)]
        }
        save_and_refresh()
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
class CustomIntervalWindow(tk.Toplevel):
    def __init__(self, master, on_save):
        super().__init__(master)
        self.on_save = on_save

        self.title("自定义提醒间隔")
        self.iconbitmap(get_resource_path('planner.ico'))
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()
        self.focus_force()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build()
        self._center()

    def _build(self):
        body = tk.Frame(self, bg=BG, padx=24, pady=20)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="设置提醒间隔（分钟）", font=("Microsoft YaHei", 11),
                    bg=BG, fg=TEXT).pack(anchor="w", pady=(0, 10))

        self.entry = tk.Entry(body, width=10, font=("Courier New", 12),
                                bg=SURFACE, fg=TEXT, insertbackground=ACCENT,
                                relief="flat", bd=0, justify="center")
        self.entry.pack(pady=(0, 20))
        self.entry.insert(0, str(state.interval_sec // 60))
        self.entry.focus_set()
        self.entry.select_range(0, 'end')

        btn_row = tk.Frame(body, bg=BG)
        btn_row.pack(fill="x")

        tk.Button(btn_row, text="取消", font=("Microsoft YaHei", 10), bg=SURFACE2, fg=TEXT_DIM,
                    activebackground=BORDER, activeforeground=TEXT, bd=0, padx=16, pady=8,
                    cursor="hand2", command=self._on_close).pack(side="left")

        tk.Button(btn_row, text="确定", font=("Microsoft YaHei", 10, "bold"), bg=ACCENT, fg="#0f0f0f",
                    activebackground=ACCENT_DIM, activeforeground="#0f0f0f", bd=0, padx=20, pady=8,
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


# ── Main window ───────────────────────────────────────────────────────────────
class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        state.main_win = self
        self.title("Daily Planner")
        self.iconbitmap(get_resource_path('planner.ico'))
        self.configure(bg=BG)
        self.geometry("460x580")
        self.minsize(400, 400)
        self.resizable(True, True)

        # System tray / hide to taskbar on close
        self.protocol("WM_DELETE_WINDOW", self._hide)

        self._build_ui()
        self.refresh()

        # Start reminder loop
        self._schedule_reminder()

        # If new day, prompt plan input
        if storage.is_new_day():
            self.after(400, self._open_plan)

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Top accent bar
        tk.Frame(self, bg=ACCENT, height=3).pack(fill="x")

        # Header
        header = tk.Frame(self, bg=BG, padx=24, pady=18)
        header.pack(fill="x")

        left = tk.Frame(header, bg=BG)
        left.pack(side="left", fill="x", expand=True)

        self.date_label = tk.Label(left, text="", font=("Courier New", 10),
                                   bg=BG, fg=TEXT_DIM, anchor="w")
        self.date_label.pack(anchor="w")

        tk.Label(left, text="今日计划", font=("Microsoft YaHei", 18, "bold"),
                 bg=BG, fg=TEXT, anchor="w").pack(anchor="w")

        right = tk.Frame(header, bg=BG)
        right.pack(side="right")

        self.edit_btn = tk.Button(right, text="✎ 编辑",
                                  font=("Microsoft YaHei", 9),
                                  bg=SURFACE2, fg=TEXT_DIM,
                                  activebackground=BORDER, activeforeground=TEXT,
                                  bd=0, padx=12, pady=6, cursor="hand2",
                                  command=self._open_plan)
        self.edit_btn.pack()

        # Progress bar area
        self.progress_frame = tk.Frame(self, bg=BG, padx=24, pady=0)
        self.progress_frame.pack(fill="x")

        self.progress_bg = tk.Frame(self.progress_frame, bg=SURFACE2, height=4)
        self.progress_bg.pack(fill="x")

        self.progress_bar = tk.Frame(self.progress_frame, bg=ACCENT, height=4)
        # placed via place() in refresh()

        self.stats_label = tk.Label(self, text="",
                                    font=("Microsoft YaHei", 9),
                                    bg=BG, fg=TEXT_DIM, anchor="w")
        self.stats_label.pack(padx=24, anchor="w", pady=(6, 0))

        # Divider
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=24, pady=12)

        # Scrollable task list
        self.canvas = tk.Canvas(self, bg=BG, bd=0, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=0, pady=0)

        self.task_frame = tk.Frame(self.canvas, bg=BG)
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.task_frame, anchor="nw")

        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.task_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Bottom bar
        bottom = tk.Frame(self, bg=SURFACE, padx=24, pady=14)
        bottom.pack(fill="x", side="bottom")

        self.next_label = tk.Label(bottom, text="",
                                   font=("Microsoft YaHei", 9),
                                   bg=SURFACE, fg=TEXT_DIM, anchor="w")
        self.next_label.pack(side="left")

        self.interval_menu_btn = tk.Menubutton(bottom, text="🕒",
                                               font=("Segoe UI Emoji", 10),
                                               bg=SURFACE, fg=TEXT_DIM,
                                               activebackground=SURFACE2, activeforeground=TEXT,
                                               bd=0, cursor="hand2", direction="above",
                                               relief="flat")
        self.interval_menu_btn.pack(side="left", padx=(8, 0))

        menu = tk.Menu(self.interval_menu_btn, tearoff=0, bg=SURFACE, fg=TEXT,
                       activebackground=ACCENT, activeforeground=BG,
                       font=("Microsoft YaHei", 10))
        self.interval_menu_btn["menu"] = menu

        menu.add_command(label="15 分钟", command=lambda: self._set_interval(15 * 60))
        menu.add_command(label="30 分钟", command=lambda: self._set_interval(30 * 60))
        menu.add_command(label="1 小时", command=lambda: self._set_interval(60 * 60))
        menu.add_separator(background=BORDER)
        menu.add_command(label="自定义...", command=self._open_custom_interval_dialog)

        self.autostart_var = tk.BooleanVar(value=autostart.is_autostart_enabled())
        tk.Checkbutton(bottom, text="开机自启",
                       variable=self.autostart_var,
                       font=("Microsoft YaHei", 9),
                       bg=SURFACE, fg=TEXT_DIM,
                       activebackground=SURFACE, activeforeground=TEXT,
                       selectcolor=SURFACE2,
                       bd=0, cursor="hand2",
                       command=self._toggle_autostart).pack(side="right")

    # ── Refresh ───────────────────────────────────────────────────────────────
    def refresh(self):
        state.data = storage.load_today()
        tasks = state.data["tasks"]
        done_count = sum(1 for t in tasks if t["done"])
        total = len(tasks)

        from datetime import date
        self.date_label.config(text=date.today().strftime("%Y年%m月%d日  %A"))

        # Progress bar
        if total > 0:
            ratio = done_count / total
            self.update_idletasks()
            bar_w = max(1, int(self.progress_bg.winfo_width() * ratio))
            self.progress_bar.place(in_=self.progress_bg, x=0, y=0,
                                    width=bar_w, height=4)
        else:
            self.progress_bar.place_forget()

        self.stats_label.config(
            text=f"已完成 {done_count} / {total}" if total else "还没有计划，点击编辑开始")

        # Task list
        for w in self.task_frame.winfo_children():
            w.destroy()

        if not tasks:
            tk.Label(self.task_frame, text="点击右上角「编辑」添加今日任务",
                     font=("Microsoft YaHei", 11), bg=BG, fg=TEXT_DIM,
                     pady=40).pack()
        else:
            for task in tasks:
                self._make_task_row(task)

        # Next reminder countdown
        self._update_countdown()

    def _make_task_row(self, task):
        is_done = task["done"]
        row_bg = DONE_COLOR if is_done else SURFACE

        row = tk.Frame(self.task_frame, bg=row_bg, pady=0)
        row.pack(fill="x", padx=24, pady=(0, 2))

        # Checkbox area
        check_frame = tk.Frame(row, bg=row_bg, width=40, padx=12, pady=14)
        check_frame.pack(side="left")
        check_frame.pack_propagate(False)

        symbol = "✓" if is_done else "○"
        sym_color = ACCENT if is_done else TEXT_DIM
        sym_label = tk.Label(check_frame, text=symbol,
                             font=("Courier New", 13, "bold"),
                             bg=row_bg, fg=sym_color, cursor="hand2")
        sym_label.pack(expand=True)

        # Task text
        txt_color = DONE_TEXT if is_done else TEXT
        txt_font_opts = ("Microsoft YaHei", 11)
        txt = tk.Label(row, text=task["text"],
                       font=txt_font_opts,
                       bg=row_bg, fg=txt_color, anchor="w",
                       wraplength=340, justify="left", pady=14, padx=4)
        txt.pack(side="left", fill="x", expand=True)

        # Toggle on click anywhere in row
        for widget in (row, check_frame, sym_label, txt):
            widget.bind("<Button-1>", lambda e, t=task: self._toggle_task(t))
            widget.configure(cursor="hand2")

    def _toggle_task(self, task):
        for t in state.data["tasks"]:
            if t["id"] == task["id"]:
                t["done"] = not t["done"]
                break
        save_and_refresh()

    # ── Interval control ──────────────────────────────────────────────────────
    def _set_interval(self, seconds):
        """设置提醒间隔并重新安排提醒。"""
        state.interval_sec = seconds
        # 注意：此实现不会将间隔时间保存到磁盘。
        # 应用重启后会重置为默认值。
        self._schedule_reminder()
        self._update_countdown() # 立即更新倒计时显示

    def _open_custom_interval_dialog(self):
        CustomIntervalWindow(self, on_save=self._set_interval)

    # ── Countdown ─────────────────────────────────────────────────────────────
    def _update_countdown(self):
        if hasattr(self, '_next_reminder_time') and self._next_reminder_time:
            remaining = max(0, int(self._next_reminder_time - time.time()))
            m, s = divmod(remaining, 60)
            self.next_label.config(text=f"下次提醒 {m:02d}:{s:02d}")
        self.after(1000, self._update_countdown)

    # ── Reminder scheduling ───────────────────────────────────────────────────
    def _schedule_reminder(self):
        self._next_reminder_time = time.time() + state.interval_sec
        if state.timer:
            state.timer.cancel()
        state.timer = threading.Timer(state.interval_sec, self._fire_reminder)
        state.timer.daemon = True
        state.timer.start()

    def _fire_reminder(self):
        if not state.reminder_open:
            self.after(0, self._show_reminder)
        # Reschedule regardless
        self._schedule_reminder()

    def _show_reminder(self):
        ReminderWindow(self)

    # ── Plan editing ──────────────────────────────────────────────────────────
    def _open_plan(self):
        PlanWindow(self)

    # ── Canvas helpers ────────────────────────────────────────────────────────
    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_resize(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ── Autostart ─────────────────────────────────────────────────────────────
    def _toggle_autostart(self):
        if self.autostart_var.get():
            autostart.enable_autostart()
        else:
            autostart.disable_autostart()

    # ── Hide to taskbar instead of closing ───────────────────────────────────
    def _hide(self):
        self.withdraw()

        # Tray icon via pystray if available, else just stay hidden
        try:
            import pystray
            from PIL import Image, ImageDraw

            def make_icon():
                img = Image.new("RGB", (64, 64), color="#0f0f0f")
                d = ImageDraw.Draw(img)
                d.rectangle([8, 8, 56, 56], fill="#c8f53a")
                return img

            def show_window(icon, item):
                icon.stop()
                self.after(0, self.deiconify)

            def quit_app(icon, item):
                icon.stop()
                if state.timer:
                    state.timer.cancel()
                self.after(0, self.destroy)

            menu = pystray.Menu(
                pystray.MenuItem("打开", show_window, default=True),
                pystray.MenuItem("退出", quit_app)
            )
            icon = pystray.Icon("DailyPlanner", make_icon(), "Daily Planner", menu)
            threading.Thread(target=icon.run, daemon=True).start()
        except ImportError:
            # pystray not installed: just minimize
            self.iconify()

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # On Windows, prevent console window when frozen
    if sys.platform == "win32" and getattr(sys, 'frozen', False):
        import ctypes
        ctypes.windll.kernel32.FreeConsole()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Carbide.Planner.0.1")

    app = MainWindow()
    app.mainloop()
