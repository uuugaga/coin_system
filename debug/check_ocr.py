"""
Show exactly what the OCR sees, to tell a bad crop from a bad reading.

Open the coin market, then run:

    python debug/check_ocr.py

For every region it prints the raw OCR text and the parsed number, and writes
debug/ocr/<region>.png (the crop, enlarged) next to
debug/ocr/<region>_context.png (the same crop with 20 px of surroundings, so a
digit falling outside the region is visible). Only captures; never clicks.
"""
import os
import sys
import time

import win32gui
from PIL import Image, ImageDraw, ImageGrab

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import detect_number
import position
import window

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ocr')
CONTEXT = 20
SCALE = 4


def main():
    handle = window.find_window()
    try:
        win32gui.SetForegroundWindow(handle)
        time.sleep(1)
    except win32gui.error as error:
        print(f'could not raise the game window ({error}); click on it and retry')

    if window.get_client_rect(handle)[2] == 0:
        print('The game window is minimized, so there is nothing to read. '
              'Restore it, open the coin market, and run this again.')
        return 1

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    position.refresh()

    for name in ('total_coin_img', 'total_silver_img', 'Buy_silver_price_img', 'Sell_silver_price_img'):
        left, top, right, bottom = getattr(position, name)

        crop = ImageGrab.grab((left, top, right, bottom), all_screens=True).convert('L')
        crop.resize((crop.width * SCALE, crop.height * SCALE), Image.NEAREST).save(
            os.path.join(OUTPUT_DIR, f'{name}.png'))

        # The same area plus a margin, with the region outlined, so a digit that
        # falls just outside the crop can be seen.
        context = ImageGrab.grab(
            (left - CONTEXT, top - CONTEXT, right + CONTEXT, bottom + CONTEXT),
            all_screens=True).convert('RGB')
        context = context.resize((context.width * SCALE, context.height * SCALE), Image.NEAREST)
        ImageDraw.Draw(context).rectangle(
            (CONTEXT * SCALE, CONTEXT * SCALE,
             context.width - CONTEXT * SCALE - 1, context.height - CONTEXT * SCALE - 1),
            outline=(255, 40, 40), width=2)
        context.save(os.path.join(OUTPUT_DIR, f'{name}_context.png'))

        raw = detect_number.ocr_model.ocr_for_single_line(
            detect_number.prepare(crop))['text']
        print(f'{name:<22} {right - left:>3}x{bottom - top:<3} px  '
              f'raw {raw!r:<14} -> {detect_number.detect_number(crop)}')

    print(f'\nwrote crops to {OUTPUT_DIR}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
