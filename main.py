import win32gui
import time
import pyautogui
import datetime
import load_file
import action
import click
import position
import window
import copy
import threading
import keyboard  # To detect 'q' key press
import random

pyautogui.FAILSAFE = False

# The server forces everyone out for maintenance every morning around 07:00.
# Orders are cancelled from MAINTENANCE_STOP on, and the bot logs back in at
# RELOGIN_AT, once maintenance is surely over.
MAINTENANCE_STOP = datetime.time(6, 50)
RELOGIN_AT = datetime.time(9, 0)

class AlbionGoldSystem:
    def __init__(self):
        self.wait_time = 1800
        self.running = True
        self.valuation_previous = 0
        self.start_datetime = datetime.datetime.now().replace(microsecond=0)
        self.showing_time = time.time()
        self.buying = False
        self.selling = False
        self.valuation_start = 0

    def stop(self):
        """Stop the program when 'q' is pressed."""
        keyboard.wait('q')
        self.running = False

    def main(self):
        """Main function of the Albion Gold System."""
        self.start_datetime = datetime.datetime.now().replace(microsecond=0)

        total_gold, total_silver, buy_price, sell_price = action.get_info()
        self.valuation_start = total_gold * buy_price + total_silver
        load_file.show_total_history(self.valuation_start)

        print(f'Asset gold={total_gold}, asset silver={total_silver}, buy price:{buy_price}, sell price:{sell_price}')

        buying_price = selling_price = 0

        while self.running:
            time.sleep(random.uniform(5, 10))
            total_gold, total_silver, buy_price, sell_price = action.get_info()

            click.click(position.Order)

            # Buying logic
            if not self.buying:
                if buy_price - sell_price > 2:
                    sell_price += 1

                unit = total_silver // sell_price - 2

                if unit > 0:
                    action.Buy_GoldCoin(unit, sell_price, refresh=False)
                    buying_time = time.time()
                    self.buying = True
                    buying_price = copy.deepcopy(sell_price)

            # Selling logic
            if not self.selling:
                if buy_price - sell_price > 2:
                    buy_price -= 1

                unit = total_gold - 2

                if unit > 0:
                    action.Sell_GoldCoin(unit, buy_price, refresh=False)
                    selling_time = time.time()
                    self.selling = True
                    selling_price = copy.deepcopy(buy_price)

            # Check if bought
            if self.buying and action.check_bought(refresh=False):
                self.buying = False
                        
            # Cancel buying if conditions met
            elif self.buying and (time.time() - buying_time > self.wait_time or buying_price < sell_price):
                action.Buy_GoldCoin_Cancel(refresh=False)
                self.buying = False

            # Check if sold
            if self.selling and action.check_sold(refresh=False):
                self.selling = False

            # Cancel selling if conditions met
            elif self.selling and (time.time() - selling_time > self.wait_time or selling_price > buy_price):
                action.Sell_GoldCoin_Cancel(refresh=False)
                self.selling = False

            # Periodic display
            if time.time() - self.showing_time > 60 * 30:
                self.handle_periodic_display()

            # Daily reset
            if MAINTENANCE_STOP <= datetime.datetime.now().time() < RELOGIN_AT:
                self.handle_daily_reset()

    def handle_periodic_display(self):
        """Handle periodic display and reset of buying/selling."""
        self.showing_time = time.time()
        if self.buying:
            action.Buy_GoldCoin_Cancel()
            self.buying = False
        if self.selling:
            action.Sell_GoldCoin_Cancel()
            self.selling = False

        
        total_gold, total_silver, buy_price, sell_price = action.get_info()
        valuation = total_gold * (buy_price - 1) + total_silver - self.valuation_start
        # print("----------------------------------------------------------------")
        # print(f'Asset gold={total_gold}, asset silver={total_silver}, buy price:{buy_price}, sell price:{sell_price}')
        print(f'Valuation: {(valuation / 1000000):.3f} m, Rate: {((valuation - self.valuation_previous) * 2 / 1000000):.3f} (m/hr), Duration: {datetime.datetime.now().replace(microsecond=0) - self.start_datetime}')
        self.valuation_previous = copy.deepcopy(valuation)

    def handle_daily_reset(self):
        """Handle the daily reset logic."""
        if self.buying:
            action.Buy_GoldCoin_Cancel()
            self.buying = False
        if self.selling:
            action.Sell_GoldCoin_Cancel()
            self.selling = False

        print(f'Waiting out server maintenance, logging in again at {RELOGIN_AT:%H:%M}')
        self.wait_until(RELOGIN_AT)
        if not self.running:
            return
        action.login()

        self.start_datetime = datetime.datetime.now().replace(microsecond=0)
        # after_login, because a client that has just logged back in can show
        # a fraction of the real assets until it finishes syncing.
        total_gold, total_silver, buy_price, sell_price = action.get_info(after_login=True)
        self.valuation_start = total_gold * buy_price + total_silver
        load_file.show_total_history(self.valuation_start)

        self.showing_time = time.time()
        self.valuation_previous = 0

    def wait_until(self, target):
        """Sleep until the wall clock reaches target today, or until 'q' is pressed."""
        while self.running and datetime.datetime.now().time() < target:
            time.sleep(5)

if __name__ == '__main__':
    print('----- START -----')
    time.sleep(2)

    window_handle = window.find_window()
    win32gui.SetForegroundWindow(window_handle)

    albion_system = AlbionGoldSystem()
    # Daemon, so that if main() dies the process exits instead of silently
    # hanging on the 'q' listener.
    stop_thread = threading.Thread(target=albion_system.stop, daemon=True)
    stop_thread.start()

    # Lets 'q' interrupt the long waits inside action, such as sitting out a
    # server outage.
    action.should_stop = lambda: not albion_system.running

    try:
        albion_system.main()
    except action.Stopped:
        print('----- STOPPED -----')