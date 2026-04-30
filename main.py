import sys

from app import config
from app.single_instance import SingleInstance, SingleInstanceException
from app.ui.main_window import MainWindow


def main():
    try:
        instance_lock = SingleInstance()
    except SingleInstanceException:
        from tkinter import messagebox

        messagebox.showerror(
            title=config.APP_DISPLAY_NAME,
            message=f"{config.APP_DISPLAY_NAME} is already running.",
        )
        return 0

    # Keep the single-instance socket alive for the lifetime of the app.
    _ = instance_lock

    if sys.platform == "win32" and getattr(sys, 'frozen', False):
        import ctypes

        ctypes.windll.kernel32.FreeConsole()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(config.APP_USER_MODEL_ID)

    app = MainWindow()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
