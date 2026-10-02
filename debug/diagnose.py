"""
Calibration helper.

Run this with the game open and the coin market on screen:

    python debug/diagnose.py

It reports the geometry the bot is working from and writes
debug/overlay.png, which is a capture of the game's client area with every
click target and OCR region drawn on top. Anything that does not sit on the
control it is named after needs its ratio corrected in position.py.
"""
import ctypes
import os
import sys
import time

import win32gui
from PIL import ImageDraw, ImageGrab

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import position
import window

OVERLAY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'overlay.png')


def list_windows():
    """Print every visible titled window, to confirm what the client is called."""
    titles = []

    def collect(handle, _):
        if win32gui.IsWindowVisible(handle):
            title = win32gui.GetWindowText(handle)
            if title:
                titles.append((handle, title))

    win32gui.EnumWindows(collect, None)

    print('--- visible windows ---')
    for handle, title in titles:
        marker = ' <-- target' if title == window.WINDOW_TITLE else ''
        print(f'  {handle:>10}  {title}{marker}')


def report_geometry(handle):
    """Print the window rect, the client rect, and the difference between them."""
    win_left, win_top, win_width, win_height = window.get_window_rect(handle)
    cli_left, cli_top, cli_width, cli_height = window.get_client_rect(handle)

    awareness = ctypes.c_int()
    try:
        ctypes.windll.shcore.GetProcessDpiAwareness(None, ctypes.byref(awareness))
        awareness = awareness.value
    except (AttributeError, OSError):
        awareness = 'unknown'

    dpi = ctypes.windll.user32.GetDpiForWindow(handle)

    print('--- geometry ---')
    print(f'  dpi awareness   : {awareness} (2 = per monitor)')
    print(f'  window dpi      : {dpi} ({dpi / 96:.0%} scaling)')
    print(f'  window rect     : left={win_left} top={win_top} {win_width}x{win_height}')
    print(f'  client rect     : left={cli_left} top={cli_top} {cli_width}x{cli_height}')
    print(f'  border / title  : x={cli_left - win_left} y={cli_top - win_top}')

    if (cli_width, cli_height) != (position.REFERENCE_WIDTH, position.REFERENCE_HEIGHT):
        print(
            f'  NOTE: client area is not the '
            f'{position.REFERENCE_WIDTH}x{position.REFERENCE_HEIGHT} the ratios '
            f'were calibrated at. The game UI does not scale linearly, so the '
            f'ratios likely need to be re-measured at this size.'
        )

    return cli_left, cli_top, cli_width, cli_height


def draw_overlay(handle, client_rect):
    """Capture the client area and mark every coordinate position.py resolves to."""
    # ImageGrab captures whatever is on screen at those coordinates, so anything
    # covering the game would be measured instead of the game.
    try:
        win32gui.SetForegroundWindow(handle)
        time.sleep(1)
    except win32gui.error as error:
        print(f'  could not raise the game window ({error}); '
              f'click on it yourself and run this again')

    left, top, width, height = client_rect
    image = ImageGrab.grab((left, top, left + width, top + height), all_screens=True)
    image = image.convert('RGB')
    draw = ImageDraw.Draw(image)

    for name in position.REGIONS:
        r_left, r_top, r_right, r_bottom = getattr(position, name)
        draw.rectangle(
            (r_left - left, r_top - top, r_right - left, r_bottom - top),
            outline=(0, 200, 255),
            width=2,
        )
        draw.text((r_left - left, r_top - top - 11), name, fill=(0, 200, 255))

    for name in position.POINTS:
        x, y = getattr(position, name)
        x, y = x - left, y - top
        draw.line((x - 7, y, x + 7, y), fill=(255, 40, 40), width=2)
        draw.line((x, y - 7, x, y + 7), fill=(255, 40, 40), width=2)
        draw.text((x + 9, y - 5), name, fill=(255, 40, 40))

    image.save(OVERLAY_PATH)
    print(f'--- overlay ---')
    print(f'  wrote {OVERLAY_PATH}')


def main():
    list_windows()

    try:
        handle = window.find_window()
    except RuntimeError as error:
        print(f'\n{error}')
        print('Pick the real title out of the list above and set '
              'WINDOW_TITLE in window.py to it.')
        return

    client_rect = report_geometry(handle)
    if client_rect[2] == 0:
        print('\nThe game window is minimized; restore it and run this again.')
        return

    position.refresh()
    draw_overlay(handle, client_rect)


if __name__ == '__main__':
    main()
