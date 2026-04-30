import tkinter as tk

from app import config
from app import task_service
from app.resources import get_resource_path
from app.ui import theme


class SummaryWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("历史总结")
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

        tk.Label(body, text="最近一周完成情况", font=("Microsoft YaHei", 16, "bold"),
                 bg=theme.BG, fg=theme.TEXT).pack(anchor="w", pady=(0, 20))

        c_width = 440
        c_height = 220
        canvas = tk.Canvas(body, width=c_width, height=c_height, bg=theme.SURFACE, bd=0, highlightthickness=0)
        canvas.pack(pady=(0, 20))

        stats = task_service.get_recent_stats(7)
        
        max_val = max((s[1] for s in stats), default=0)
        max_val = max(max_val, 5)  # 保证坐标系最少有个基础高度
        
        pad_x = 40
        pad_y = 30
        eff_w = c_width - 2 * pad_x
        eff_h = c_height - 2 * pad_y
        
        # 绘制底部轴线
        canvas.create_line(pad_x, c_height - pad_y, c_width - pad_x, c_height - pad_y, fill=theme.BORDER, width=2)
        
        points = []
        n = len(stats)
        for i, (date_str, comp, total) in enumerate(stats):
            x = pad_x + i * (eff_w / (n - 1)) if n > 1 else pad_x + eff_w / 2
            y = c_height - pad_y - (comp / max_val) * eff_h
            points.append((x, y))
            
            # x轴日期系标签
            canvas.create_text(x, c_height - pad_y + 15, text=date_str, fill=theme.TEXT_DIM, font=("Courier New", 9))
            # 数值标签
            canvas.create_text(x, y - 15, text=str(comp), fill=theme.ACCENT, font=("Courier New", 10, "bold"))
            
        if len(points) > 1:
            coords = [c for p in points for c in p]
            canvas.create_line(*coords, fill=theme.ACCENT, width=2)
                
        for x, y in points:
            canvas.create_oval(x-4, y-4, x+4, y+4, fill=theme.BG, outline=theme.ACCENT, width=2)
            
        tk.Button(body, text="关闭", font=("Microsoft YaHei", 11), bg=theme.SURFACE2, fg=theme.TEXT,
                  activebackground=theme.BORDER, activeforeground=theme.TEXT, bd=0, padx=24, pady=8,
                  cursor="hand2", command=self._on_close).pack()

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
