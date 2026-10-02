import window

# Size of the game image the layout was calibrated at (in-game UI scale 100%).
REFERENCE_WIDTH = 1280
REFERENCE_HEIGHT = 720

# The original measurements were taken against GetWindowRect of that client in
# standard windowed mode, i.e. including an 8 px frame on the left, right and
# bottom and a 31 px title bar. They are converted to client area fractions
# below, so the result no longer depends on what the window frame looks like.
CALIBRATION_FRAME_X = 8
CALIBRATION_TITLE_Y = 31
CALIBRATION_WINDOW_WIDTH = REFERENCE_WIDTH + 2 * CALIBRATION_FRAME_X
CALIBRATION_WINDOW_HEIGHT = REFERENCE_HEIGHT + CALIBRATION_TITLE_Y + CALIBRATION_FRAME_X


def _window_px(x, y):
    """Convert a pixel offset from the calibration window's corner to a client ratio."""
    return (
        (x - CALIBRATION_FRAME_X) / REFERENCE_WIDTH,
        (y - CALIBRATION_TITLE_Y) / REFERENCE_HEIGHT,
    )


def _window_ratio(ratio_x, ratio_y):
    """Convert a fraction of the calibration window rect to a client ratio."""
    return _window_px(ratio_x * CALIBRATION_WINDOW_WIDTH, ratio_y * CALIBRATION_WINDOW_HEIGHT)


def _window_box(left, top, right, bottom):
    """Convert a box given as window rect fractions to client ratios."""
    return (*_window_ratio(left, top), *_window_ratio(right, bottom))


def _client_px(x, y):
    """Convert a pixel position measured on a 1280x720 client area to a ratio."""
    return x / REFERENCE_WIDTH, y / REFERENCE_HEIGHT


def _client_box(left, top, right, bottom):
    """Convert a box measured in pixels on a 1280x720 client area to ratios."""
    return (
        left / REFERENCE_WIDTH,
        top / REFERENCE_HEIGHT,
        right / REFERENCE_WIDTH,
        bottom / REFERENCE_HEIGHT,
    )


def _button_box(ratio_x, ratio_y):
    """
    Box around a buy/sell button, 25 px to each side and 5 px above / 3 px below
    a center given as window rect fractions.
    """
    center_x, center_y = _window_ratio(ratio_x, ratio_y)
    return (
        center_x - 25 / REFERENCE_WIDTH,
        center_y - 5 / REFERENCE_HEIGHT,
        center_x + 25 / REFERENCE_WIDTH,
        center_y + 3 / REFERENCE_HEIGHT,
    )


# Click targets, as (x, y) fractions of the client area.
POINTS = {
    'GetCoin': _window_ratio(0.3, 0.9),
    'Order': _window_ratio(0.44, 0.9),
    'Buy_coin_num_position': _window_ratio(0.3326, 0.67),
    'Sell_coin_num_position': _window_ratio(0.3326, 0.7971),
    'Buy_silver_num_position': _window_ratio(0.44, 0.67),
    'Sell_silver_num_position': _window_ratio(0.4282, 0.7971),
    'Buy_button_position': _window_ratio(0.7292, 0.6680),
    'Sell_button_position': _window_ratio(0.7292, 0.7945),
    'Buy_cancel_button_position': _window_ratio(0.7307, 0.6851),
    'Sell_cancel_button_position': _window_ratio(0.7283, 0.8142),
    'Cancel_check_position': _window_ratio(0.4212, 0.5019),
    # These three used to be raw pixel offsets added to the window origin, which
    # only lined up while the window was exactly the calibration size.
    'Buy_check_position': _window_px(798, 451),
    'Bought_Sold_check_position': _window_px(648, 378),
    'Have_bought_sold_check_position': _window_px(640, 440),
    # These panels open by themselves on entering the world and cover the
    # screen, so they have to be dismissed before the bag can be used.
    'Close_activity_position': _client_px(893, 88),
    'Close_promo_position': _client_px(971, 116),
    'Close_twitch_position': _client_px(988, 131),
    'Enter_coin_market_position': _window_ratio(0.7924, 0.4664),
    'Close_coin_market_position': _window_ratio(0.7593, 0.1910),
    'Login_buttom': _window_ratio(0.5694, 0.7088),
    # Centered on the enter button; the old ratio sat on its top edge.
    'Enter_game_buttom': _client_px(809, 592),
}

# Screenshot regions, as (left, top, right, bottom) fractions of the client area.
REGIONS = {
    'Buy_button_position_img': _button_box(0.7292, 0.6680),
    'Sell_button_position_img': _button_box(0.7292, 0.7891),
    # The original crops sat 1-4 px inside the last digit of a five digit
    # price, so the OCR read 13,312 as "13.31" and the bot offered a tenth of
    # the real price. These are measured with room for the digits to grow and
    # for the comma's tail, which fell below the old boxes.
    'Buy_silver_price_img': _client_box(603, 470, 688, 502),
    'Sell_silver_price_img': _client_box(603, 567, 688, 599),
    'total_coin_img': _client_box(378, 346, 452, 366),
    'total_silver_img': _client_box(379, 368, 470, 390),
}


def refresh():
    """
    Recompute every coordinate from where the game window is right now.

    The coordinates used to be resolved once at import time, so moving,
    restoring or maximizing the window left the whole table pointing at stale
    screen positions with no way to recover. Returns the client rect it used.
    """
    left, top, width, height = window.get_client_rect(window.find_window())

    for name, (ratio_x, ratio_y) in POINTS.items():
        globals()[name] = (left + width * ratio_x, top + height * ratio_y)

    for name, (r_left, r_top, r_right, r_bottom) in REGIONS.items():
        # ImageGrab expects integers, and truncating floats here keeps the
        # region from wobbling by a pixel between calls.
        globals()[name] = (
            int(left + width * r_left),
            int(top + height * r_top),
            int(left + width * r_right),
            int(top + height * r_bottom),
        )

    return left, top, width, height


def __getattr__(name):
    """Give a useful error if a coordinate is read before refresh() has run."""
    if name in POINTS or name in REGIONS:
        raise AttributeError(
            f'position.{name} is not available yet: call position.refresh() '
            f'once the game window is open.'
        )
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')


# Best effort, so that importing this module while the game is still loading
# does not fail. main.py calls refresh() again before using any coordinate.
try:
    refresh()
except RuntimeError:
    pass
