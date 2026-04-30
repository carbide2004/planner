THEMES = {
    "dark": {
        "BG": "#0f0f0f", "SURFACE": "#1a1a1a", "SURFACE2": "#242424",
        "BORDER": "#2e2e2e", "ACCENT": "#c8f53a", "ACCENT_DIM": "#8fb028",
        "TEXT": "#e8e8e8", "TEXT_DIM": "#666666",
        "DONE_COLOR": "#3a3a3a", "DONE_TEXT": "#4a4a4a", "RED": "#ff4444"
    },
    "light": {
        "BG": "#ffffff", "SURFACE": "#f5f5f5", "SURFACE2": "#e8e8e8",
        "BORDER": "#d1d1d1", "ACCENT": "#22c55e", "ACCENT_DIM": "#16a34a",
        "TEXT": "#171717", "TEXT_DIM": "#737373",
        "DONE_COLOR": "#e5e5e5", "DONE_TEXT": "#a3a3a3", "RED": "#ef4444"
    }
}

BG = SURFACE = SURFACE2 = BORDER = ACCENT = ACCENT_DIM = TEXT = TEXT_DIM = DONE_COLOR = DONE_TEXT = RED = ""

def set_theme(theme_name):
    global BG, SURFACE, SURFACE2, BORDER, ACCENT, ACCENT_DIM, TEXT, TEXT_DIM, DONE_COLOR, DONE_TEXT, RED
    t = THEMES[theme_name]
    BG = t["BG"]
    SURFACE = t["SURFACE"]
    SURFACE2 = t["SURFACE2"]
    BORDER = t["BORDER"]
    ACCENT = t["ACCENT"]
    ACCENT_DIM = t["ACCENT_DIM"]
    TEXT = t["TEXT"]
    TEXT_DIM = t["TEXT_DIM"]
    DONE_COLOR = t["DONE_COLOR"]
    DONE_TEXT = t["DONE_TEXT"]
    RED = t["RED"]

set_theme("dark")

