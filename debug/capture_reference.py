"""
Create the reference images screen.py matches against.

Set the game to the screen you want to teach it, then run:

    python debug/capture_reference.py bag

The named region is cut out of the game's client area and saved to
references/<name>.png. Pass --check instead to score the existing references
against whatever the game is showing right now:

    python debug/capture_reference.py --check

Only captures the screen; it never clicks or types.
"""
import os
import sys
import time

import win32gui
from PIL import ImageGrab

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import screen
import window

# Regions to cut, as (left, top, right, bottom) fractions of the client area.
# Each must cover artwork that never changes: an earlier 'bag' region included
# the coin amounts, so it stopped matching once the amounts did.
REGIONS = {
    # Loadout and wardrobe buttons, only on screen while the bag is open.
    'bag': (1150 / 1280, 280 / 720, 1240 / 1280, 332 / 720),
    # Title emblem of the events panel, not its close button, which is the
    # same artwork the market uses.
    'activity': (385 / 1280, 80 / 720, 500 / 1280, 135 / 720),
    # Close button shared by the advertising pop-ups, whose artwork changes with
    # every campaign. It is searched for anywhere on screen rather than at a
    # fixed spot, so this only has to be recaptured if the button itself changes.
    'popup_close': (958 / 1280, 103 / 720, 986 / 1280, 131 / 720),
    # OK button of the "order submitted" modal. Its wording shifts with the
    # order amount, so the button is the stable part to match.
    'order_confirm': (597 / 1280, 334 / 720, 684 / 1280, 367 / 720),
    # 'remember me' rows of the login screen, avoiding the email text.
    'login': (495 / 1280, 385 / 720, 620 / 1280, 445 / 720),
    'character_select': (745 / 1280, 573 / 720, 875 / 1280, 612 / 720),
}


def raise_game(handle):
    """Bring the game forward, so the capture is not of a window covering it."""
    try:
        win32gui.SetForegroundWindow(handle)
        time.sleep(1)
    except win32gui.error as error:
        print(f'could not raise the game window ({error}); click on it and retry')


def capture(name):
    if name not in REGIONS:
        print(f'unknown region {name!r}; known: {", ".join(sorted(REGIONS))}')
        return 1

    handle = window.find_window()
    raise_game(handle)
    left, top, width, height = window.get_client_rect(handle)
    r_left, r_top, r_right, r_bottom = REGIONS[name]
    box = (
        int(left + width * r_left),
        int(top + height * r_top),
        int(left + width * r_right),
        int(top + height * r_bottom),
    )

    os.makedirs(screen.REFERENCE_DIR, exist_ok=True)
    image = ImageGrab.grab(box, all_screens=True).convert('L')
    image.save(screen.reference_path(name))
    print(f'saved {screen.reference_path(name)} ({image.width}x{image.height})')
    print('Check it shows only the artwork you meant, then run with --check.')
    return 0


def check():
    handle = window.find_window()
    raise_game(handle)
    current = screen.grab_client()

    for name in sorted(REGIONS):
        if not screen.has_reference(name):
            print(f'  {name:<10} no reference image yet')
            continue
        score, location = screen.match(name, current)
        verdict = 'SHOWING' if score >= screen.MATCH_THRESHOLD else 'not showing'
        print(f'  {name:<10} score {score:.3f} at {location}  {verdict}')
    return 0


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    sys.exit(check() if args[0] == '--check' else capture(args[0]))
