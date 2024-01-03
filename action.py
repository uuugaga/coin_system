import click
import position
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
    # click.click(position.Bought_Sold_check_position)
    click.click(position.Buy_cancel_button_position)
    click.click(position.Cancel_check_position)

def Sell_GoldCoin_Cancel(refresh=True):
    """
    Function to cancel a gold coin selling order.
    Similar to the Buy_GoldCoin_Cancel function, it cancels the selling order.
    """
    if refresh:
        click.click(position.Order)
    # click.click(position.Bought_Sold_check_position)
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
    # click.click(position.Buy_check_position)
    image = ImageGrab.grab(position.Buy_button_position_img).convert('L').resize((8, 50))
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
    # click.click(position.Buy_check_position)
    image = ImageGrab.grab(position.Sell_button_position_img).convert('L').resize((8, 50))
    image = np.array(image)
    return image.sum() > 27000
    
def get_info(average):
    """
    Function to retrieve current market information.
    It navigates through the interface, grabs screenshots, and uses detect_number to obtain numerical values.
    """
    click.click(position.Close_coin_market_position)
    click.click(position.Enter_coin_market_position)

    while True:
        gold = detect_number.detect_number(ImageGrab.grab(position.total_coin_img).convert('L'), 0)
        silver = detect_number.detect_number(ImageGrab.grab(position.total_silver_img).convert('L'), 0)
        buy = detect_number.detect_number(ImageGrab.grab(position.Buy_silver_price_img).convert('L'), average)
        sell = detect_number.detect_number(ImageGrab.grab(position.Sell_silver_price_img).convert('L'), average)
        
        if all([gold != 0, silver != 0, buy != 0, sell != 0]):
            break

    return gold, silver, buy, sell

def login():
    """
    Function to automate the login process.
    It performs the necessary clicks and waits for the interface to load.
    """
    click.click(position.Login_buttom)
    time.sleep(10)
    click.click(position.Enter_game_buttom)
    time.sleep(15)
    pyautogui.press('i')
    time.sleep(2)
    click.click(position.Enter_coin_market_position)
