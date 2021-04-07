import alpaca_trade_api as tradeapi
import time
from tradeFile import *
DELAY_TIME = 0.1

API_KEY = "PKJ8QUHRRFZQQSEKKEX1"
API_SECRET = "GfDwaxWouFZF7l6wt8wbopMAtKqrx8ufmIfxVnhX"
APCA_API_BASE_URL = "https://paper-api.alpaca.markets"

api = tradeapi.REST(API_KEY, API_SECRET, APCA_API_BASE_URL, 'v2')

tradeParas = readtradeParasFromFile()
print(tradeParas)
tradeQty = 200


def generate_buy_order():
    m_buy_order_id = str(time.time()) + '_Buy_METX'
    time.sleep(DELAY_TIME)
    api.submit_order(
        symbol='METX',
        qty=tradeQty,
        side='buy',
        type='limit',
        time_in_force='day',
        extended_hours=True,
        limit_price=tradeParas['LastBuyPrice'] - tradeParas['PriceStep'],
        client_order_id=m_buy_order_id
    )
    return m_buy_order_id


def generate_sell_order():
    m_sell_order_id = str(time.time()) + '_Sell_METX'
    time.sleep(DELAY_TIME)
    api.submit_order(
        symbol='METX',
        qty=tradeQty,
        side='sell',
        type='limit',
        time_in_force='day',
        extended_hours=True,
        limit_price=tradeParas['LastBuyPrice'] + tradeParas['ProfitStep'],
        client_order_id=m_sell_order_id
    )
    return m_sell_order_id


my_buy_order_id = generate_buy_order()
my_sell_order_id = generate_sell_order()

while True:
    time.sleep(DELAY_TIME)
    buy_order = api.get_order_by_client_order_id(my_buy_order_id)
    time.sleep(DELAY_TIME)
    sell_order = api.get_order_by_client_order_id(my_sell_order_id)

    if (int(buy_order.filled_qty) == tradeQty) and (int(sell_order.filled_qty) == tradeQty):
        appendTradeRecord("Buy " + buy_order.filled_qty + " METX @Price:" + buy_order.filled_avg_price
                          + " and Sell " + sell_order.filled_qty + " METX @Price:" + sell_order.filled_avg_price)
        my_buy_order_id = generate_buy_order()
        my_sell_order_id = generate_sell_order()

    elif int(buy_order.filled_qty) == tradeQty:
        appendTradeRecord("Buy " + buy_order.filled_qty + " METX @Price:" + buy_order.filled_avg_price)

        sellOrderCanceled = False
        while not sellOrderCanceled:
            time.sleep(DELAY_TIME)
            api.cancel_order(sell_order.id)
            time.sleep(DELAY_TIME)
            sell_order = api.get_order_by_client_order_id(my_sell_order_id)
            if sell_order.canceled_at != None or int(sell_order.filled_qty) == tradeQty:
                sellOrderCanceled = True

        tradeParas['LastBuyPrice'] = tradeParas['LastBuyPrice'] - tradeParas['PriceStep']
        savetradeParasToFile(tradeParas)
        my_buy_order_id = generate_buy_order()
        my_sell_order_id = generate_sell_order()

    elif int(sell_order.filled_qty) == tradeQty:
        appendTradeRecord("Sell " + sell_order.filled_qty + " METX @Price:" + sell_order.filled_avg_price)

        buyOrderCanceled = False
        while not buyOrderCanceled:
            time.sleep(DELAY_TIME)
            api.cancel_order(buy_order.id)
            time.sleep(DELAY_TIME)
            buy_order = api.get_order_by_client_order_id(my_buy_order_id)
            if buy_order.canceled_at != None or int(buy_order.filled_qty) == tradeQty:
                buyOrderCanceled = True

        tradeParas['LastBuyPrice'] = tradeParas['LastBuyPrice'] + tradeParas['PriceStep']
        savetradeParasToFile(tradeParas)
        my_buy_order_id = generate_buy_order()
        my_sell_order_id = generate_sell_order()

