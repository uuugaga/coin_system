"""
Recognizing what the game is currently showing.

Clicking blind is what makes the bot fragile: pressing 'i' toggles the bag, so
sending it when the bag is already open closes it, and clicking where the bag
icon should be while the bag is shut lands on the game world instead. So the
interface is matched against small reference images of static UI artwork, kept
in references/ and created with debug/capture_reference.py.
"""
import datetime
import os

import cv2
import numpy as np
from PIL import Image, ImageGrab

import window

REFERENCE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'references')
INCIDENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'debug', 'incidents')
# Match quality above which the artwork counts as present. UI art is drawn
# identically every time, so a real match scores far higher than this.
MATCH_THRESHOLD = 0.8


def capture():
    """Capture the game's client area."""
    left, top, width, height = window.get_client_rect(window.find_window())
    if width == 0 or height == 0:
        raise RuntimeError('The game window is minimized, so nothing can be read from it.')
    return ImageGrab.grab((left, top, left + width, top + height), all_screens=True)


def grab_client():
    """Capture the game's client area as a grayscale array."""
    return np.array(capture().convert('L'))


def save_incident(reason):
    """
    Save what the game is showing, so an unexpected screen can be looked at
    afterwards instead of being lost. Returns the path, or None if even the
    capture failed.
    """
    try:
        image = capture()
    except RuntimeError as error:
        print(f'could not capture the screen: {error}')
        return None

    now = datetime.datetime.now()
    folder = os.path.join(INCIDENT_DIR, f'{now:%Y-%m-%d}')
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f'{now:%H%M%S}_{reason}.png')
    image.save(path)
    print(f'saved {path}')
    return path


def reference_path(name):
    return os.path.join(REFERENCE_DIR, f'{name}.png')


def has_reference(name):
    return os.path.exists(reference_path(name))


def match(name, screen=None):
    """
    Return (score, (x, y)) for the best match of a reference image, where x, y
    is its top left corner in client coordinates. Score runs from 0 to 1.
    """
    # Loaded through Pillow rather than cv2.imread, which cannot open paths
    # containing non-ASCII characters on Windows.
    try:
        template = np.array(Image.open(reference_path(name)).convert('L'))
    except FileNotFoundError:
        raise FileNotFoundError(
            f'No reference image for {name!r}. Create it with '
            f'debug/capture_reference.py while the game shows that screen.'
        )

    if screen is None:
        screen = grab_client()
    if screen.shape[0] < template.shape[0] or screen.shape[1] < template.shape[1]:
        return 0.0, (0, 0)

    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _, score, _, location = cv2.minMaxLoc(result)
    return float(score), location


def is_showing(name, screen=None, threshold=MATCH_THRESHOLD):
    """
    Whether that part of the interface is on screen. Returns None when no
    reference image exists yet, so callers can fall back to their old behavior
    instead of guessing.
    """
    if not has_reference(name):
        return None
    score, _ = match(name, screen)
    return score >= threshold
