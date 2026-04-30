import sys
import os

from app import config

def get_exe_path():
    """Return the path to the running executable or script."""
    if getattr(sys, 'frozen', False):
        return sys.executable
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return f'"{sys.executable}" "{os.path.join(project_dir, "main.py")}"'

def enable_autostart():
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, config.APP_NAME, 0, winreg.REG_SZ, get_exe_path())
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Autostart enable failed: {e}")
        return False

def disable_autostart():
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.DeleteValue(key, config.APP_NAME)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Autostart disable failed: {e}")
        return False

def is_autostart_enabled():
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_READ
        )
        winreg.QueryValueEx(key, config.APP_NAME)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False
