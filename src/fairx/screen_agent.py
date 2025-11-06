import threading, time, os
try:
    import win32gui, win32ui, win32con
except:
    win32gui = None

from .events import Event
from .suspicion import SCORE
from .config import CFG

# ⚠️ Blocked keywords
SUSPICIOUS_APPS = [
    "discord", "telegram", "whatsapp", "teams",
    "instagram", "facebook", "messenger",
    "chrome", "edge", "firefox", "opera"
]

# Allowed safe windows (google meet / exam platforms)
SAFE_WINDOWS = [
    "zoom", "meet", "proctor", "exam", "test", "assessment", "lockdown"
]

# prevent spam
last_event = {}
def throttle(key, cooldown=3):
    now = time.time()
    if key not in last_event or now - last_event[key] > cooldown:
        last_event[key] = now
        return True
    return False


def screenshot(tag="screen"):
    """Capture proof of screen context"""
    try:
        hwnd = win32gui.GetDesktopWindow()
        w = win32gui.GetWindowRect(hwnd)
        width = w[2] - w[0]
        height = w[3] - w[1]

        hdc = win32gui.GetWindowDC(hwnd)
        dc = win32ui.CreateDCFromHandle(hdc)
        cdc = win32ui.CreateCompatibleDC(dc)
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(dc, width, height)
        cdc.SelectObject(bmp)
        cdc.BitBlt((0,0), (width, height), dc, (0,0), win32con.SRCCOPY)

        ts = int(time.time())
        path = os.path.join(CFG.evidence_dir, f"screen_{tag}_{ts}.bmp")
        bmp.SaveBitmapFile(cdc, path)
        cdc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hdc)
        print(f"[SCREEN] 📸 Screenshot saved: {path}")

    except Exception as e:
        print(f"[SCREEN] ❌ Screenshot fail: {e}")


class ScreenAgent(threading.Thread):
    def run(self):
        if win32gui is None:
            print("[SCREEN] ❌ pywin32 missing — skipping screen monitor")
            return
        
        print("[SCREEN] 🖥️ Screen agent active")

        prev_title = ""
        while True:
            try:
                hwnd = win32gui.GetForegroundWindow()
                title = win32gui.GetWindowText(hwnd).lower()
                if not title: 
                    time.sleep(0.2); 
                    continue

                # Skip system windows
                if "program manager" in title or "task switching" in title:
                    continue

                # Ignore safe exam platforms
                if any(safe in title for safe in SAFE_WINDOWS):
                    prev_title = title
                    time.sleep(0.2)
                    continue

                # Detect tab / window switch
                if title != prev_title and throttle("switch", 2):
                    print(f"[SCREEN] 🔄 Window changed: {title}")
                    SCORE.add(Event.now("tab_switch", 0.4, window=title))

                # Detect banned apps
                if any(app in title for app in SUSPICIOUS_APPS):
                    if throttle("banned", 5):
                        print(f"[SCREEN] 🚨 Suspicious window: {title}")
                        SCORE.add(Event.now("tab_switch", 0.9, app=title))
                        screenshot("banned")

                prev_title = title

            except Exception as e:
                print("[SCREEN] ❌ Error:", e)

            time.sleep(0.3)
