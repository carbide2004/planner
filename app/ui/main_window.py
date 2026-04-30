import threading
import time
import tkinter as tk
from datetime import datetime

from app import autostart, config, storage
from app.resources import get_resource_path
from app.state import save_and_refresh, state
from app.ui import theme
from app.ui.interval_window import CustomIntervalWindow
from app.ui.plan_window import PlanWindow
from app.ui.reminder_window import ReminderWindow
from app.ui.summary_window import SummaryWindow


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        state.main_win = self
        self.title(config.APP_DISPLAY_NAME)
        self.iconbitmap(get_resource_path(config.ICON_FILENAME))
        self.configure(bg=theme.BG)
        self.geometry(config.MAIN_WINDOW_GEOMETRY)
        self.minsize(*config.MAIN_WINDOW_MIN_SIZE)
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
        tk.Frame(self, bg=theme.ACCENT, height=3).pack(fill="x")

        # Header
        header = tk.Frame(self, bg=theme.BG, padx=24, pady=18)
        header.pack(fill="x")

        left = tk.Frame(header, bg=theme.BG)
        left.pack(side="left", fill="x", expand=True)

        self.date_label = tk.Label(left, text="", font=("Courier New", 10),
                                   bg=theme.BG, fg=theme.TEXT_DIM, anchor="w")
        self.date_label.pack(anchor="w")

        tk.Label(left, text="今日计划", font=("Microsoft YaHei", 18, "bold"),
                 bg=theme.BG, fg=theme.TEXT, anchor="w").pack(anchor="w")

        right = tk.Frame(header, bg=theme.BG)
        right.pack(side="right")

        self.summary_btn = tk.Button(right, text="📊 总结",
                                     font=("Microsoft YaHei", 9),
                                     bg=theme.SURFACE2, fg=theme.TEXT_DIM,
                                     activebackground=theme.BORDER, activeforeground=theme.TEXT,
                                     bd=0, padx=12, pady=6, cursor="hand2",
                                     command=self._open_summary)
        self.summary_btn.pack(side="left", padx=(0, 8))

        self.edit_btn = tk.Button(right, text="✎ 编辑",
                                  font=("Microsoft YaHei", 9),
                                  bg=theme.SURFACE2, fg=theme.TEXT_DIM,
                                  activebackground=theme.BORDER, activeforeground=theme.TEXT,
                                  bd=0, padx=12, pady=6, cursor="hand2",
                                  command=self._open_plan)
        self.edit_btn.pack(side="left", padx=(0, 8))

        theme_icon = "🌙" if state.theme == "dark" else "☀️"
        self.theme_btn = tk.Button(right, text=theme_icon,
                                   font=("Segoe UI Emoji", 10),
                                   bg=theme.SURFACE2, fg=theme.TEXT_DIM,
                                   activebackground=theme.BORDER, activeforeground=theme.TEXT,
                                   bd=0, padx=12, pady=6, cursor="hand2",
                                   command=self._toggle_theme)
        self.theme_btn.pack(side="left")

        # Progress bar area
        self.progress_frame = tk.Frame(self, bg=theme.BG, padx=24, pady=0)
        self.progress_frame.pack(fill="x")

        self.progress_bg = tk.Frame(self.progress_frame, bg=theme.SURFACE2, height=4)
        self.progress_bg.pack(fill="x")

        self.progress_bar = tk.Frame(self.progress_frame, bg=theme.ACCENT, height=4)
        # placed via place() in refresh()

        self.stats_label = tk.Label(self, text="",
                                    font=("Microsoft YaHei", 9),
                                    bg=theme.BG, fg=theme.TEXT_DIM, anchor="w")
        self.stats_label.pack(padx=24, anchor="w", pady=(6, 0))

        # Divider
        tk.Frame(self, bg=theme.BORDER, height=1).pack(fill="x", padx=24, pady=12)

        # Scrollable task list
        self.canvas = tk.Canvas(self, bg=theme.BG, bd=0, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=0, pady=0)

        self.task_frame = tk.Frame(self.canvas, bg=theme.BG)
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.task_frame, anchor="nw")

        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.task_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Bottom bar
        bottom = tk.Frame(self, bg=theme.SURFACE, padx=24, pady=14)
        bottom.pack(fill="x", side="bottom")

        self.next_label = tk.Label(bottom, text="",
                                   font=("Microsoft YaHei", 9),
                                   bg=theme.SURFACE, fg=theme.TEXT_DIM, anchor="w")
        self.next_label.pack(side="left")

        self.interval_menu_btn = tk.Menubutton(bottom, text="🕒",
                                               font=("Segoe UI Emoji", 10),
                                               bg=theme.SURFACE, fg=theme.TEXT_DIM,
                                               activebackground=theme.SURFACE2, activeforeground=theme.TEXT,
                                               bd=0, cursor="hand2", direction="above",
                                               relief="flat")
        self.interval_menu_btn.pack(side="left", padx=(8, 0))

        menu = tk.Menu(self.interval_menu_btn, tearoff=0, bg=theme.SURFACE, fg=theme.TEXT,
                       activebackground=theme.ACCENT, activeforeground=theme.BG,
                       font=("Microsoft YaHei", 10))
        self.interval_menu_btn["menu"] = menu

        menu.add_command(label="15 分钟", command=lambda: self._set_interval(15 * 60))
        menu.add_command(label="30 分钟", command=lambda: self._set_interval(30 * 60))
        menu.add_command(label="1 小时", command=lambda: self._set_interval(60 * 60))
        menu.add_separator(background=theme.BORDER)
        menu.add_command(label="自定义...", command=self._open_custom_interval_dialog)

        self.autostart_var = tk.BooleanVar(value=autostart.is_autostart_enabled())
        tk.Checkbutton(bottom, text="开机自启",
                       variable=self.autostart_var,
                       font=("Microsoft YaHei", 9),
                       bg=theme.SURFACE, fg=theme.TEXT_DIM,
                       activebackground=theme.SURFACE, activeforeground=theme.TEXT,
                       selectcolor=theme.SURFACE2,
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
                     font=("Microsoft YaHei", 11), bg=theme.BG, fg=theme.TEXT_DIM,
                     pady=40).pack()
        else:
            for task in tasks:
                self._make_task_row(task)

        # Next reminder countdown
        self._update_countdown()

    def _make_task_row(self, task):
        is_done = task["done"]
        row_bg = theme.DONE_COLOR if is_done else theme.SURFACE

        row = tk.Frame(self.task_frame, bg=row_bg, pady=0)
        row.pack(fill="x", padx=24, pady=(0, 2))

        # Checkbox area
        check_frame = tk.Frame(row, bg=row_bg, width=40, padx=12, pady=14)
        check_frame.pack(side="left")
        check_frame.pack_propagate(False)

        symbol = "✓" if is_done else "○"
        sym_color = theme.ACCENT if is_done else theme.TEXT_DIM
        sym_label = tk.Label(check_frame, text=symbol,
                             font=("Courier New", 13, "bold"),
                             bg=row_bg, fg=sym_color, cursor="hand2")
        sym_label.pack(expand=True)

        # Task text
        txt_color = theme.DONE_TEXT if is_done else theme.TEXT
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
                t["completed_at"] = datetime.now().isoformat() if t["done"] else None
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
        if hasattr(self, '_countdown_after_id'):
            self.after_cancel(self._countdown_after_id)

        if hasattr(self, '_next_reminder_time') and self._next_reminder_time:
            remaining = max(0, int(self._next_reminder_time - time.time()))
            m, s = divmod(remaining, 60)
            if hasattr(self, 'next_label') and self.next_label.winfo_exists():
                self.next_label.config(text=f"下次提醒 {m:02d}:{s:02d}")
                
        self._countdown_after_id = self.after(1000, self._update_countdown)

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

    def _open_summary(self):
        SummaryWindow(self)

    # ── Theme control ─────────────────────────────────────────────────────────
    def _toggle_theme(self):
        state.theme = "light" if state.theme == "dark" else "dark"
        theme.set_theme(state.theme)
        self.configure(bg=theme.BG)
        for w in self.winfo_children():
            w.destroy()
        self._build_ui()
        self.refresh()

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
            from PIL import Image

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
            icon_image = Image.open(get_resource_path(config.ICON_FILENAME))
            icon = pystray.Icon(config.APP_NAME, icon_image, config.APP_DISPLAY_NAME, menu)
            threading.Thread(target=icon.run, daemon=True).start()
        except ImportError:
            # pystray not installed: just minimize
            self.iconify()

# ── Entry point ───────────────────────────────────────────────────────────────
