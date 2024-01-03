import win32gui, win32con, win32api
import time
import pyautogui
import random
import math
import numpy as np
from scipy import interpolate

def point_dist(x1, y1, x2, y2):
    """Calculate the distance between two points."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def smooth_mouse_move(x2, y2):
    """Move the mouse to (x2, y2) in a smooth, human-like curve."""
    cp = random.randint(4, 8)  # Number of control points. Must be at least 2.
    x1, y1 = pyautogui.position()  # Starting position

    # Distribute control points between start and destination evenly.
    x = np.linspace(x1, x2, num=cp, dtype='int')
    y = np.linspace(y1, y2, num=cp, dtype='int')

    # Randomize inner points a bit (+-RND at most).
    RND = 10
    xr = [random.randint(-RND, RND) for k in range(cp)]
    yr = [random.randint(-RND, RND) for k in range(cp)]
    xr[0] = yr[0] = xr[-1] = yr[-1] = 0
    x += xr
    y += yr

    # Approximate using Bezier spline.
    degree = 3 if cp > 3 else cp - 1  # Degree of b-spline. 3 is recommended.
                                      # Must be less than number of control points.
    tck, u = interpolate.splprep([x, y], k=degree)
    # Move up to a certain number of points
    u = np.linspace(0, 1, num=2+int(point_dist(x1, y1, x2, y2)/50.0))
    points = interpolate.splev(u, tck)

    # Move mouse.
    duration = 0.1
    timeout = duration / len(points[0])
    point_list = zip(*(i.astype(int) for i in points))
    for point in point_list:
        pyautogui.moveTo(*point, duration=timeout, tween=pyautogui.easeInOutQuad)

def click(coordinates):
    smooth_mouse_move(coordinates[0], coordinates[1])
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
    time.sleep(random.uniform(0.1, 0.2))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
    time.sleep(random.uniform(0.3, 1))