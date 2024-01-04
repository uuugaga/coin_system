import win32gui
import time
import pyautogui
import datetime
import load_file
import action
import click
import position
import copy
import threading
import keyboard  # To detect 'q' key press
import random

pyautogui.FAILSAFE = False

class AlbionGoldSystem:
    def __init__(self):
        self.wait_time = 1800
        self.running = True
        self.valuation_previous = 0
        self.start_datetime = datetime.datetime.now().replace(microsecond=0)
        self.showing_time = time.time()
        self.buying = False
        self.selling = False
        self.buying_price_record = 0
        self.selling_price_record = 0
        self.valuation_start = 0

    def stop(self):
        """Stop the program when 'q' is pressed."""
        keyboard.wait('q')
        self.running = False

    def main(self):
        """Main function of the Albion Gold System."""
        self.start_datetime = datetime.datetime.now().replace(microsecond=0)

        total_gold, total_silver, buy_price, sell_price = action.get_info(0)
        self.valuation_start = total_gold * buy_price + total_silver
        load_file.show_total_history(self.valuation_start)

        print(f'Asset gold={total_gold}, asset silver={total_silver}, buy price:{buy_price}, sell price:{sell_price}')

        buying_price = selling_price = 0

        while self.running:
            time.sleep(random.uniform(5, 10))
            average_price_record = (self.buying_price_record + self.selling_price_record) // 2
            total_gold, total_silver, buy_price, sell_price = action.get_info(average_price_record)
            self.buying_price_record, self.selling_price_record = copy.deepcopy(buy_price), copy.deepcopy(sell_price)


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

            click.click(position.Order)
            # Check if bought
            if self.buying and action.check_bought(refresh=False):
                self.buying = False
            # Cancel buying if conditions met
            elif self.buying and (time.time() - buying_time > self.wait_time or buying_price < sell_price):
                action.Buy_GoldCoin_Cancel(refresh=False)
                self.buying = False

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

            # Check if sold
            if self.selling and action.check_sold(refresh=False):
                self.selling = False
            # Cancel selling if conditions met
            elif self.selling and (time.time() - selling_time > self.wait_time or selling_price > buy_price):
                action.Sell_GoldCoin_Cancel(refresh=False)
                self.selling = False

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

            # Periodic display
            if time.time() - self.showing_time > 60 * 30:
                self.handle_periodic_display()

            # Daily reset
            localtime = time.localtime(time.time())
            if localtime.tm_hour == 6 and 49 < localtime.tm_min < 59:
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

        
        total_gold, total_silver, buy_price, sell_price = action.get_info(0)
        valuation = total_gold * (buy_price - 1) + total_silver - self.valuation_start
        # print("----------------------------------------------------------------")
        # print(f'Asset gold={total_gold}, asset silver={total_silver}, buy price:{buy_price}, sell price:{sell_price}')
        print(f'Valuation:{(valuation / 1000000):3f}m, Rate:{((valuation - self.valuation_previous) * 6 / 1000000):3f}(m/hr), Duration:\"{datetime.datetime.now().replace(microsecond=0) - self.start_datetime}\"')
        self.valuation_previous = copy.deepcopy(valuation)

    def handle_daily_reset(self):
        """Handle the daily reset logic."""
        if self.buying:
            action.Buy_GoldCoin_Cancel()
            self.buying = False
        if self.selling:
            action.Sell_GoldCoin_Cancel()
            self.selling = False

        time.sleep(60 * 30)  # Sleep for 30 minutes
        action.login()

        self.start_datetime = datetime.datetime.now().replace(microsecond=0)
        total_gold, total_silver, buy_price, sell_price = action.get_info(self.average_price_record)
        self.valuation_start = total_gold * buy_price + total_silver
        load_file.show_total_history(self.valuation_start)
        self.buying_price_record = copy.deepcopy(buy_price)
        self.selling_price_record = copy.deepcopy(sell_price)

        self.showing_time = time.time()
        self.valuation_previous = 0

if __name__ == '__main__':
    print('----- START -----')
    time.sleep(2)

    window_handle = win32gui.FindWindow(None, "Albion Online Client")
    win32gui.SetForegroundWindow(window_handle)

    albion_system = AlbionGoldSystem()
    stop_thread = threading.Thread(target=albion_system.stop)
    stop_thread.start()
    albion_system.main()