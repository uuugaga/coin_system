"""Save a plain capture of the game's client area, for measuring new ratios."""
import os
import sys

from PIL import ImageGrab

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import window

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client.png')


def screenshot():
    """
    Capture the client area, so that a pixel read off the saved image divides
    straight into a ratio for position.py.
    """
    left, top, width, height = window.get_client_rect(window.find_window())
    image = ImageGrab.grab((left, top, left + width, top + height), all_screens=True)
    image.save(OUTPUT_PATH)
    print(f'wrote {OUTPUT_PATH} ({width}x{height})')
    return image


if __name__ == '__main__':
    screenshot()
