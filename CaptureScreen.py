import cv2
import numpy as np
from ctypes import windll
import win32gui
import win32ui

'''
import mss
import numpy as np
import cv2
import pywinctl
'''

'''
def capture_screen(window_title, **kwargs):
    # Find the window by title
    windows = pywinctl.getWindowsWithTitle(window_title)
    if not windows:
        raise ValueError(f"Window with title '{window_title}' not found!")
    window = windows[0]

    # Get the window's bounding box
    bbox = {
        'top': window.top,
        'left': window.left,
        'width': window.width,
        'height': window.height
    }

    with mss.mss() as sct:
        # Capture the window
        screenshot = sct.grab(bbox)
        
        # Convert to a format suitable for OpenCV
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        return img
'''

from contextlib import contextmanager

@contextmanager
def gdi_resource_management(hwnd):
    # Acquire resources
    hwnd_dc = win32gui.GetWindowDC(hwnd)
    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()
    bitmap = win32ui.CreateBitmap()
    
    try:
        yield hwnd_dc, mfc_dc, save_dc, bitmap
    finally:
        # Ensure resources are released
        win32gui.DeleteObject(bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwnd_dc)

def capture_screen(window_name: str):
    windll.user32.SetProcessDPIAware()
    hwnd = win32gui.FindWindow(None, window_name)

    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    w = right - left
    h = bottom - top

    with gdi_resource_management(hwnd) as (hwnd_dc, mfc_dc, save_dc, bitmap):
        bitmap.CreateCompatibleBitmap(mfc_dc, w, h)
        save_dc.SelectObject(bitmap)

        result = windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 3)

        if not result:
            raise RuntimeError(f"Unable to acquire screenshot! Result: {result}")
        
        bmpinfo = bitmap.GetInfo()
        bmpstr = bitmap.GetBitmapBits(True)

    img = np.frombuffer(bmpstr, dtype=np.uint8).reshape((bmpinfo["bmHeight"], bmpinfo["bmWidth"], 4))
    img = np.ascontiguousarray(img)[..., :-1]  # make image C_CONTIGUOUS and drop alpha channel

    return img
