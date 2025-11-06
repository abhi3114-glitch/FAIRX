import threading, time
try:
    import win32gui
except:
    win32gui = None

from .events import Event
from .suspicion import SCORE

FORBIDDEN = {"discord", "whatsapp", "telegram", "teams", "chrome"}

class ScreenAgent(threading.Thread):
    def run(self):
        if win32gui is None:
            return
        
        last = ""
        while True:
            title = win32gui.GetWindowText(win32gui.GetForegroundWindow()).lower()
            if title != last:
                last = title
                SCORE.add(Event.now("tab_switch", 0.5, window=title))
                if any(app in title for app in FORBIDDEN):
                    SCORE.add(Event.now("tab_switch", 0.9, banned=title))
            time.sleep(0.2)
