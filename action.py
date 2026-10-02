import click
import load_file
import position
import screen
import window
import pyautogui
import numpy as np
from PIL import ImageGrab 
import detect_number
import time
import random

def Buy_GoldCoin(gold_num, silver_num, refresh=True):
    """
    Function to automate the process of buying gold coins.
    It inputs the specified number of gold and silver coins and performs the necessary clicks.
    """
    if refresh:
        click.click(position.Order)
    click.click(position.Buy_coin_num_position)

    # Input gold number with random sleep to mimic human behavior
    for char in str(gold_num):
        pyautogui.press(char)
        time.sleep(random.uniform(0.1, 0.3))

    click.click(position.Buy_silver_num_position)

    # Input silver number with random sleep
    for char in str(silver_num):
        pyautogui.press(char)
        time.sleep(random.uniform(0.1, 0.3))

    click.click(position.Buy_button_position)
    click.click(position.Buy_check_position)
    click.click(position.Bought_Sold_check_position)
    
def Sell_GoldCoin(gold_num, silver_num, refresh=True):
    """
    Function to automate the process of selling gold coins.
    Similar to the Buy_GoldCoin function, it inputs the number of coins and performs the necessary actions.
    """
    if refresh:
        click.click(position.Order)
    click.click(position.Sell_coin_num_position)

    # Input gold number
    for char in str(gold_num):
        pyautogui.press(char)
        time.sleep(random.uniform(0.1, 0.3))

    click.click(position.Sell_silver_num_position)

    # Input silver number
    for char in str(silver_num):
        pyautogui.press(char)
        time.sleep(random.uniform(0.1, 0.3))

    click.click(position.Sell_button_position)
    click.click(position.Bought_Sold_check_position)

def Buy_GoldCoin_Cancel(refresh=True):
    """
    Function to cancel a gold coin buying order.
    It navigates through the interface and performs the necessary clicks to cancel the order.
    """
    if refresh:
        click.click(position.Order)
    # click.click(position.Have_bought_sold_check_position)
    click.click(position.Buy_cancel_button_position)
    click.click(position.Cancel_check_position)

def Sell_GoldCoin_Cancel(refresh=True):
    """
    Function to cancel a gold coin selling order.
    Similar to the Buy_GoldCoin_Cancel function, it cancels the selling order.
    """
    if refresh:
        click.click(position.Order)
    # click.click(position.Have_bought_sold_check_position)
    click.click(position.Sell_cancel_button_position)
    click.click(position.Cancel_check_position)

def check_bought(refresh=True):
    """
    Function to check if the buying order is successful.
    It grabs a screenshot of the relevant area and checks if the sum of pixel values meets a threshold.
    """
    if refresh:
        click.click(position.GetCoin)
        click.click(position.Order)
    click.click(position.Have_bought_sold_check_position)
    image = ImageGrab.grab(position.Buy_button_position_img, all_screens=True).convert('L').resize((8, 50))
    image = np.array(image)
    return image.sum() > 27000
    
def check_sold(refresh=True):
    """
    Function to check if the selling order is successful.
    Similar to the check_bought function, it checks for a selling order.
    """
    if refresh:
        click.click(position.GetCoin)
        click.click(position.Order)
    click.click(position.Have_bought_sold_check_position)
    image = ImageGrab.grab(position.Sell_button_position_img, all_screens=True).convert('L').resize((8, 50))
    image = np.array(image)
    return image.sum() > 27000
    
# Panels that open by themselves after entering the world and cover the game.
# Each needs its own reference and close button: the close artwork is not the
# same from panel to panel, so one generic button match would not find them.
# A new pop-up shows up as a saved incident screenshot; add it here with
# debug/capture_reference.py.
BLOCKING_DIALOGS = (
    # First, because it is modal: while it is up nothing else can be clicked,
    # not even the market's own close button. It appears when an order is
    # submitted and is normally acknowledged right away, but a slow server
    # reply can leave it on screen after the acknowledging click has gone.
    ('order_confirm', 'Bought_Sold_check_position'),
    ('activity', 'Close_activity_position'),
)

# Advertising panels change with every campaign, so they are recognized by the
# close button they all share rather than by their artwork: a reference per
# campaign stopped the bot twice, once for a starter pack and once for Twitch
# Drops. The market's own close button is different enough not to match, which
# matters, since closing the market here would undo the work.
POPUP_CLOSE_SIZE = 28
MAX_POPUPS = 3


def dismiss_dialogs():
    """Close any pop-up panel sitting over the game. Returns how many were closed."""
    closed = 0
    for name, close_position in BLOCKING_DIALOGS:
        if screen.is_showing(name):
            print(f'Closing the {name} window.')
            click.click(getattr(position, close_position))
            closed += 1

    # Several can be stacked: today's promo said "1/2" at the bottom.
    for _ in range(MAX_POPUPS):
        if not screen.has_reference('popup_close'):
            break
        score, (x, y) = screen.match('popup_close')
        if score < screen.MATCH_THRESHOLD:
            break
        left, top, _, _ = window.get_client_rect(window.find_window())
        print(f'Closing an advertising window at ({x}, {y}).')
        click.click((left + x + POPUP_CLOSE_SIZE // 2, top + y + POPUP_CLOSE_SIZE // 2))
        closed += 1

    return closed


def open_coin_market():
    """
    Put the coin market on screen, opening the bag first if it is not already.

    The market is entered by clicking the coin icon inside the bag, so the bag
    has to be open: clicking there while it is shut lands on the game world and
    moves the character. 'i' toggles the bag, so it is only pressed when the bag
    is known to be closed, never blind.
    """
    position.refresh()
    dismiss_dialogs()

    if screen.is_showing('bag') is False:
        pyautogui.press('i')
        time.sleep(random.uniform(1, 2))
        if screen.is_showing('bag') is False:
            # Usually means the client is not in the game at all, which the
            # caller handles. Clicking on regardless would hit the world.
            print('The bag is not open; leaving the market alone.')
            return False

    click.click(position.Close_coin_market_position)
    click.click(position.Enter_coin_market_position)
    return True


# How long the market may stay unreadable before something is treated as wrong,
# and how many times recovery may be attempted before giving up. Reading fails
# briefly all the time, while the panel opens or a tab is switching.
READ_TIMEOUT = 60
MAX_RECOVERIES = 3

# A logged out client is treated differently: the server itself can be down,
# as it was on 2026-09-23, and there is nothing to do but wait for it.
OUTAGE_RETRY_INTERVAL = 15 * 60
OUTAGE_TIME_LIMIT = 2 * 60 * 60

# A reading whose total assets differ from the last recorded total by more than
# this is treated as the client not having synced yet. After a re-login it once
# reported 17 m of assets when 647 m were there, and every later figure was off
# by that much.
PLAUSIBLE_DEVIATION = 0.30

# Replaced by main.py so that long waits can still be stopped with 'q'.
should_stop = lambda: False


class Stopped(Exception):
    """Raised when 'q' is pressed during a long wait."""


def wait(seconds):
    """Sleep, but in short steps so that 'q' does not have to wait it out."""
    deadline = time.time() + seconds
    while time.time() < deadline:
        if should_stop():
            raise Stopped()
        time.sleep(min(5, max(0, deadline - time.time())))


def plausible(reading, expected_total):
    """Whether a reading's total assets are close enough to the last recorded total."""
    gold, silver, buy_price, _ = reading
    total = gold * buy_price + silver
    return abs(total - expected_total) <= expected_total * PLAUSIBLE_DEVIATION


def read_market():
    """
    Read the four market numbers, or None if any of them could not be read.
    """
    gold = detect_number.detect_number(ImageGrab.grab(position.total_coin_img, all_screens=True).convert('L'))
    silver = detect_number.detect_number(ImageGrab.grab(position.total_silver_img, all_screens=True).convert('L'))
    buy = detect_number.detect_number(ImageGrab.grab(position.Buy_silver_price_img, all_screens=True).convert('L'))
    sell = detect_number.detect_number(ImageGrab.grab(position.Sell_silver_price_img, all_screens=True).convert('L'))

    if all([gold != 0, silver != 0, buy != 0, sell != 0]):
        return gold, silver, buy, sell
    return None


def get_info(after_login=False):
    """
    Function to retrieve current market information.
    It navigates through the interface, grabs screenshots, and uses detect_number to obtain numerical values.

    A logged out client shows no numbers at all, so reading is given a deadline
    rather than retried forever: the old loop span for 20 hours after a
    disconnect, never returning, so not even the daily reset could run.
    """
    recoveries = 0
    outage_started = None
    unsynced = None
    # Only worth checking against the recorded total just after logging in,
    # when the client may not have synced yet. At any other time the figure is
    # legitimately far from it, because assets committed to open orders do not
    # count towards what the market panel shows as held.
    expected_total = load_file.read_last_total() if after_login else None

    while True:
        if open_coin_market():
            deadline = time.time() + READ_TIMEOUT
            previous = None
            while time.time() < deadline:
                reading = read_market()

                # A half drawn panel can still produce four plausible numbers,
                # which is how a re-login once recorded 334 m of assets instead
                # of 637 m. A settled panel reads the same twice in a row.
                if reading is not None and reading == previous:
                    if expected_total is None or plausible(reading, expected_total):
                        return reading
                    # Steady, but nowhere near the assets last recorded: the
                    # client is probably still syncing. Keep looking.
                    unsynced = reading
                previous = reading

            if unsynced is not None:
                total = unsynced[0] * unsynced[2] + unsynced[1]
                print(f'Assets read as {total / 1000000:.3f} m against '
                      f'{expected_total / 1000000:.3f} m recorded.')
            else:
                print(f'Market unreadable for {READ_TIMEOUT}s.')
            screen.save_incident('unsynced' if unsynced is not None else 'unreadable')
        else:
            screen.save_incident('not_in_game')

        if recoveries >= MAX_RECOVERIES:
            if unsynced is not None:
                # Believe it after all: the assets really may have changed by
                # this much, and stopping would end the session over a guess.
                print('Still the same figure after retrying; taking it as correct.')
                return unsynced
            raise RuntimeError(
                f'Could not get back to the market after {MAX_RECOVERIES} attempts. '
                f'See the saved screenshots in debug/incidents.'
            )
        recoveries += 1
        state = recover_session()

        if state in ('logged_out', 'character_select'):
            # Reading again straight after logging back in, so the sync check
            # applies from here on even if the caller did not ask for it.
            expected_total = load_file.read_last_total()

        if state == 'logged_out':
            # The server can be down rather than the client being confused, so
            # this waits it out instead of spending the retries in a minute.
            if outage_started is None:
                outage_started = time.time()
            elif time.time() - outage_started > OUTAGE_TIME_LIMIT:
                raise RuntimeError(
                    f'Still logged out {OUTAGE_TIME_LIMIT // 3600} hours after the first '
                    f'attempt. The server may be down; see debug/incidents.'
                )
            recoveries = 0
            print(f'Trying to log in again in {OUTAGE_RETRY_INTERVAL // 60} minutes.')
            wait(OUTAGE_RETRY_INTERVAL)


def recover_session():
    """
    Get back into the game after a disconnect, a maintenance kick, or an idle
    logout, which all leave the client sitting on the login screen. Returns what
    it found, so the caller can be patient about a server that is down.
    """
    position.refresh()

    if screen.is_showing('login'):
        print('Logged out: logging back in.')
        login()
        return 'logged_out'
    elif screen.is_showing('character_select'):
        print('At character select: entering the world.')
        enter_world()
        return 'character_select'
    else:
        # Some other screen: a dialog, a loading screen, or the market simply
        # being slow. Clicking blind here would be worse than waiting.
        print('Unrecognized screen; waiting before trying again.')
        wait(30)
        return 'unknown'


def enter_world():
    """Enter the game from the character select screen, with the character it defaults to."""
    position.refresh()
    click.click(position.Enter_game_buttom)
    # The world was still loading 19 s after this click on 2026-09-22, so the
    # original 15 s was not enough to start reading the market.
    time.sleep(30)


def login():
    """
    Function to automate the login process.
    It performs the necessary clicks and waits for the interface to load.

    Nothing is typed: the client keeps the credentials, so this only presses
    the buttons a player would.
    """
    position.refresh()
    click.click(position.Login_buttom)
    time.sleep(10)
    enter_world()
    open_coin_market()
