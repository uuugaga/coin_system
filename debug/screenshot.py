import win32gui
from PIL import ImageGrab 

window_handle = win32gui.FindWindow(None, "Albion Online Client")

def screenshot():
    x1, y1, x2, y2 = win32gui.GetWindowRect(window_handle)
    ImageGrab.grab((x1, y1, x2, y2)).convert('L').save('total_coin.png')
    exit(0)
