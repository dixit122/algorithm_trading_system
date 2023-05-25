from fastapi import FastAPI
import json
from Logs import logError, logWarning, logCritical, logInfo

#############################################################
# The API that handles incoming orders. Your code goes here #
#############################################################

app = FastAPI()


@app.post("/create_order")
def process_payload(payload: dict):

    print(payload)

    strategy = payload.get('STRATEGY')
    instrument = payload.get('INSTRUMENT')
    position = payload.get('POSITION')

    if strategy is None or instrument is None or position is None:
        logError("The order does is mission one of the values")
        return {"RESPONSE": "Invalid_Order"}
    elif strategy not in valid_strategy_data:
        logError("The given strategy is not present in any of the user_profile")
        return {"RESPONSE": "Invalid_Order"}
    elif instrument not in valid_strategy_data[strategy]:
        logError("The given instrument does not belongs to particular stretegy")
        return {"RESPONSE": "Invalid_Order"}

    if position == "BUY":
        if strategy not in buy_order_data:
            buy_order_data[strategy] = {}
            buy_order_data[strategy][instrument] = True
            buy_sell_valid_data.append(
                strategy + " " + instrument + " " + position)
            logInfo("The buy order has been placed")
            return {"RESPONSE": "Valid Order. The buy order has been placed"}
        elif instrument not in buy_order_data[strategy]:
            buy_order_data[strategy][instrument] = True
            buy_sell_valid_data.append(
                strategy + " " + instrument + " " + position)
            logInfo("The buy order has been placed")
            return {"RESPONSE": "Valid Order. The buy order has been placed"}
        else:
            logError("Duplicate Buy Order found")
            return {"RESPONSE": "Invalid_Order"}
    else:
        if strategy not in buy_order_data:
            logError("the instrument has not been bought yet")
            return {"RESPONSE": "Invalid_Order"}
        elif instrument not in buy_order_data[strategy]:
            logError("the instrument has not been bought yet")
            return {"RESPONSE": "Invalid_Order"}
        else:
            del buy_order_data[strategy][instrument]
            buy_sell_valid_data.append(
                strategy + " " + instrument + " " + position)
            logInfo("The sell order has been placed")
            return {"RESPONSE": "Valid Order. The sell order has been placed"}

    return {"RESPONSE": "Blank response"}


@app.on_event("startup")
def get_data_from_user_profile():
    global data
    data = {}

    global buy_order_data
    buy_order_data = {}

    global valid_strategy_data
    valid_strategy_data = {}

    global buy_sell_valid_data
    buy_sell_valid_data = []

    try:
        with open('../Jsons/Buy_Orders.json', 'w+') as buy_order:
            buy_order_data = json.load(buy_order)
    except json.decoder.JSONDecodeError:
        buy_order_data = {}

    with open('../Jsons/user_profile.json') as f:
        data = json.load(f)

    for user_name in data:
        for strategy in data[user_name]:
            if strategy not in valid_strategy_data:
                valid_strategy_data[strategy] = data[user_name][strategy]


@app.on_event("shutdown")
def store_the_buy_orders():
    with open('../Jsons/Buy_Orders.json', 'r+') as buy_orders:
        json.dump(buy_order_data, buy_orders)

    existing_data = []

    try:
        with open('../Jsons/Buy_Sell_data.json', 'w+') as f:
            existing_data = json.load(f)
    except json.decoder.JSONDecodeError:
        existing_data = []

    existing_data.extend(buy_sell_valid_data)
    with open('../Jsons/Buy_Sell_data.json', 'a+') as f:
        json.dump(buy_sell_valid_data, f)
