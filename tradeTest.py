import alpaca_trade_api as tradeapi
import time
from tradeFile import *

API_KEY = "PKJ8QUHRRFZQQSEKKEX1"
API_SECRET = "GfDwaxWouFZF7l6wt8wbopMAtKqrx8ufmIfxVnhX"
APCA_API_BASE_URL = "https://paper-api.alpaca.markets"

api = tradeapi.REST(API_KEY, API_SECRET, APCA_API_BASE_URL, 'v2')

def my_order_id(BorS):
    if BorS=='Buy':
        return str(time.time())+'_Buy_METX'
    else:
        return str(time.time())+'_Sell_METX'

myOrderId=my_order_id('Buy')

api.submit_order(
    symbol='METX',
    qty=1,
    side='buy',
    type='limit',
    time_in_force='day',
    limit_price=2.10,
    client_order_id=myOrderId
)

my_order = api.get_order_by_client_order_id(myOrderId)
print('Got order #{}'.format(my_order.id))

api.cancel_order(my_order.id)

my_order = api.get_order_by_client_order_id(myOrderId)
print('Got order #{}'.format(my_order))



#------------------------------------------------------------

tradeParas = readtradeParasFromFile()
print(tradeParas)
tradeQty = 200

def generateBuyOrder():
    m_buy_order_id = str(time.time()) + '_Buy_METX'
    api.submit_order(
        symbol='METX',
        qty=tradeQty,
        side='buy',
        type='limit',
        time_in_force='day',
        limit_price=tradeParas['LastBuyPrice'] - tradeParas['PriceStep'],
        client_order_id=my_buy_order_id
    )
    return m_buy_order_id

def generateSellOrder():
    m_sell_order_id = str(time.time()) + '_Sell_METX'
    api.submit_order(
        symbol='METX',
        qty=tradeQty,
        side='sell',
        type='limit',
        time_in_force='day',
        limit_price=tradeParas['LastBuyPrice'] + tradeParas['ProfitStep'],
        client_order_id=my_buy_order_id
    )
    return m_sell_order_id

my_buy_order_id = generateBuyOrder()
my_sell_order_id = generateSellOrder()

while True:
    buy_order = api.get_order_by_client_order_id(my_buy_order_id)
    sell_order = api.get_order_by_client_order_id(my_sell_order_id)

    if(int(buy_order.filled_qty) == tradeQty) and (int(sell_order.filled_qty) == tradeQty):
        appendTradeRecord("Buy "+buy_order.filled_qty+" METX @Price:"+buy_order.filled_avg_price
                          + " and Sell "+sell_order.filled_qty+" METX @Price:"+sell_order.filled_avg_price)
        my_buy_order_id = generateBuyOrder()
        my_sell_order_id = generateSellOrder()

    elif int(buy_order.filled_qty) == tradeQty:
        appendTradeRecord("Buy "+buy_order.filled_qty+" METX @Price:"+buy_order.filled_avg_price)

        sellOrderCanceled = False
        while not sellOrderCanceled:
            time.sleep(0.1)
            api.cancel_order(sell_order.id)
            time.sleep(0.1)
            sell_order = api.get_order_by_client_order_id(my_sell_order_id)
            if sell_order.canceled_at != None or int(sell_order.filled_qty) == tradeQty:
                sellOrderCanceled = True

        tradeParas['LastBuyPrice'] = tradeParas['LastBuyPrice'] - tradeParas['PriceStep']
        savetradeParasToFile(tradeParas)
        my_buy_order_id = generateBuyOrder()
        my_sell_order_id = generateSellOrder()

    elif int(sell_order.filled_qty) == tradeQty:
        appendTradeRecord("Sell " + sell_order.filled_qty + " METX @Price:" + sell_order.filled_avg_price)

        buyOrderCanceled = False
        while not buyOrderCanceled:
            time.sleep(0.1)
            api.cancel_order(buy_order.id)
            time.sleep(0.1)
            buy_order = api.get_order_by_client_order_id(my_buy_order_id)
            if buy_order.canceled_at != None or int(buy_order.filled_qty) == tradeQty:
                buyOrderCanceled = True

        tradeParas['LastBuyPrice'] = tradeParas['LastBuyPrice'] - tradeParas['PriceStep']
        savetradeParasToFile(tradeParas)
        my_buy_order_id = generateBuyOrder()
        my_sell_order_id = generateSellOrder()

    time.sleep(0.05)
