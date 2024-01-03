import win32gui


window_handle = win32gui.FindWindow(None, "Albion Online Client")

x1, y1, x2, y2 = win32gui.GetWindowRect(window_handle)
width = x2 - x1
height = y2 - y1


GetCoin = (x1 + width * 0.3, y1 + height * 0.9)
Order = (x1 + width * 0.44, y1 + height * 0.9)
Buy_coin_num_position = (x1 + width * 0.3326, y1 + height * 0.67)
Sell_coin_num_position = (x1 + width * 0.3326, y1 + height * 0.7971)
Buy_silver_num_position = (x1 + width * 0.44, y1 + height * 0.67)
Sell_silver_num_position = (x1 + width * 0.4282, y1 + height * 0.7971)
Buy_button_position = (x1 + width * 0.7292, y1 + height * 0.6680)
Sell_button_position = (x1 + width * 0.7292, y1 + height * 0.7945)
Buy_cancel_button_position = (x1 + width * 0.7307, y1 + height * 0.6851)
Sell_cancel_button_position = (x1 + width * 0.7283, y1 + height * 0.8142)
Cancel_check_position = (x1 + width * 0.4212, y1 + height * 0.5019)
Buy_check_position = (x1 + 798, y1 + 451)
Bought_Sold_check_position = (x1 + 648, y1 + 378)
Buy_button_position_img = (x1 + width * 0.7292 - 25, y1 + height * 0.6680 - 5, x1 + width * 0.7292 + 25, y1 + height * 0.6680 + 3)
Sell_button_position_img = (x1 + width * 0.7292 - 25, y1 + height * 0.7891 - 5, x1 + width * 0.7292 + 25, y1 + height * 0.7891 + 3)

Buy_silver_price_img = (x1 + width * 0.4730, y1 + height * 0.6640, x1 + width * 0.5247, y1 + height * 0.6943)
Sell_silver_price_img = (x1 + width * 0.4722, y1 + height * 0.7931, x1 + width * 0.5231, y1 + height * 0.8221)

total_coin_img = (x1 + width * 0.2980, y1 + height * 0.4980, x1 + width * 0.3426, y1 + height * 0.5210)
total_silver_img = (x1 + width * 0.2986, y1 + height * 0.5283, x1 + width * 0.3573, y1 + height * 0.5520)

Enter_coin_market_position = (x1 + width * 0.7924, y1 + height * 0.4664)
Close_coin_market_position = (x1 + width * 0.7593, y1 + height * 0.1910)

Login_buttom = (x1 + width * 0.5694, y1 + height * 0.7088)
Enter_game_buttom = (x1 + width * 0.6273, y1 + height * 0.8103)