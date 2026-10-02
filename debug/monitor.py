"""
Passive watcher that records what the game looked like when something went wrong.

Run it in a second terminal next to main.py:

    python debug/monitor.py

It never clicks, types or changes window focus. It only captures the screen and
writes the captures to debug/incidents/<date>/ together with monitor.log, so the
disconnect, maintenance and login screens can be studied afterwards and the
bot taught to handle them. Stop it with Ctrl+C.
"""
import datetime
import os
import sys
import time

from PIL import ImageChops, ImageGrab, ImageStat

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import position
import window

INCIDENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'incidents')
LOG_PATH = os.path.join(INCIDENT_DIR, 'monitor.log')

CHECK_SECONDS = 20
# The bot switches market tabs every few seconds, so a client area that has not
# changed for this long means it is stuck or the game is showing some dialog.
FROZEN_MINUTES = 10
ROUTINE_MINUTES = 30
# Maintenance and the re-login happen in this window, so capture it densely.
BUSY_HOURS = (datetime.time(6, 30), datetime.time(10, 0))
BUSY_MINUTES = 2
# Mean per-pixel difference (0-255) below which two frames count as the same.
SAME_FRAME_THRESHOLD = 1.5


def log(message):
    line = f'{datetime.datetime.now():%Y-%m-%d %H:%M:%S}  {message}'
    print(line)
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def save(image, reason):
    now = datetime.datetime.now()
    folder = os.path.join(INCIDENT_DIR, f'{now:%Y-%m-%d}')
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f'{now:%H%M%S}_{reason}.png')
    image.save(path)
    log(f'saved {reason}: {path}')


def thumbnail(image):
    """Small grayscale copy, cheap to compare and insensitive to noise."""
    return image.convert('L').resize((160, 90))


def same_frame(a, b):
    if a is None or b is None:
        return False
    return sum(ImageStat.Stat(ImageChops.difference(a, b)).mean) <= SAME_FRAME_THRESHOLD


def in_busy_hours(now):
    start, end = BUSY_HOURS
    return start <= now.time() <= end


def capture_game():
    """
    Return (state, image). The image is the client area when the game is
    visible, otherwise the whole desktop so the capture still shows why.
    """
    try:
        handle = window.find_window()
    except RuntimeError:
        return 'missing', ImageGrab.grab(all_screens=True)

    left, top, width, height = window.get_client_rect(handle)
    if width == 0 or height == 0:
        return 'minimized', ImageGrab.grab(all_screens=True)
    if (width, height) != (position.REFERENCE_WIDTH, position.REFERENCE_HEIGHT):
        state = f'size_{width}x{height}'
    else:
        state = 'ok'
    return state, ImageGrab.grab((left, top, left + width, top + height), all_screens=True)


def main():
    os.makedirs(INCIDENT_DIR, exist_ok=True)
    log('monitor started')

    last_state = None
    last_saved = None          # thumbnail of the last capture written to disk
    last_saved_time = 0.0
    unchanged_since = time.time()
    previous = None            # thumbnail of the previous check
    frozen_reported = False

    while True:
        now = datetime.datetime.now()
        state, image = capture_game()
        thumb = thumbnail(image)

        if state != last_state:
            log(f'state {last_state} -> {state}')
            if last_state is not None:
                save(image, f'state_{state}')
                last_saved, last_saved_time = thumb, time.time()
            last_state = state

        if same_frame(thumb, previous):
            if not frozen_reported and time.time() - unchanged_since >= FROZEN_MINUTES * 60:
                save(image, 'frozen')
                last_saved, last_saved_time = thumb, time.time()
                frozen_reported = True
        else:
            unchanged_since = time.time()
            frozen_reported = False
        previous = thumb

        interval = BUSY_MINUTES if in_busy_hours(now) else ROUTINE_MINUTES
        if time.time() - last_saved_time >= interval * 60 and not same_frame(thumb, last_saved):
            save(image, 'busy' if in_busy_hours(now) else 'routine')
            last_saved, last_saved_time = thumb, time.time()

        time.sleep(CHECK_SECONDS)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        log('monitor stopped')
