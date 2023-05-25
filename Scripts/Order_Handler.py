from fastapi import FastAPI
import json
import os
from Logs import logInfo, logError

app = FastAPI()

# Load the user profiles from the JSON file
with open("../Jsons/user_profile.json") as f:
    user_profiles = json.load(f)

# Extract strategies and instruments
strategy_instruments = {}
for profile in user_profiles.values():
    for strategy, instruments in profile.items():
        if strategy not in strategy_instruments:
            strategy_instruments[strategy] = []
        strategy_instruments[strategy].extend(instruments)

# Load existing buy orders from the database
buy_orders_file = "../Jsons/buy_orders.json"

if not os.path.exists(buy_orders_file) or os.stat(buy_orders_file).st_size == 0:
    buy_orders = {}
    with open(buy_orders_file, 'w') as f:
        json.dump(buy_orders, f)
else:
    with open(buy_orders_file) as f:
        buy_orders = json.load(f)

@app.post("/create_order")
def process_payload(payload: dict):

    strategy = payload.get('STRATEGY')
    instrument = payload.get('INSTRUMENT')
    position = payload.get('POSITION')

    # Check if the order is valid
    if strategy is None or instrument is None or position not in ["BUY", "SELL"]:
        logError("Invalid order received.")
        return {"RESPONSE": "Invalid order."}
    elif strategy not in strategy_instruments:
        logError("Invalid order received.")
        return {"RESPONSE": "Invalid order."}
    elif instrument not in strategy_instruments[strategy]:
        logError("Invalid order received.")
        return {"RESPONSE": "Invalid order."}
    
    if position == "SELL":
        # Check if a corresponding buy order exists for the strategy and instrument
        if strategy in buy_orders and instrument in buy_orders[strategy]:
            # Remove the buy order
            del buy_orders[strategy][instrument]
            if not buy_orders[strategy]:
                del buy_orders[strategy]
            logInfo("Sell order processed.")
            return {"RESPONSE": "Sell order processed."}
        else:
            logError("No buy order found for the given strategy and instrument.")
            return {"RESPONSE": "No buy order found."}
    elif position == "BUY":
        # Check if a buy order already exists for the strategy and instrument
        if strategy not in buy_orders:
            buy_orders[strategy] = {}
        
        if instrument in buy_orders[strategy]:
            logError("Duplicate buy order received for the given strategy and instrument.")
            return {"RESPONSE": "Duplicate buy order."}
        
        # Add the buy order to the database
        buy_orders[strategy][instrument] = True
        logInfo("Buy order processed.")
        return {"RESPONSE": "Buy order processed."}


@app.on_event("shutdown")
def save_buy_orders():
    # Save the buy orders to the database before shutting down
    with open("../Jsons/buy_orders.json", 'w') as f:
        json.dump(buy_orders, f, indent=4)

# Additional code to implement the order log
@app.get("/order_log")
def get_order_log():
    global order_log
    order_log = []

    with open("../Jsons/order_log.json") as f:
        order_log = json.load(f)
    return {"order_log": order_log}

@app.post("/order_log")
def append_to_order_log(order: dict):
    with open("../Jsons/order_log.json", 'a') as f:
        json.dump(order, f)
        f.write('\n')
    return {"RESPONSE": "Order logged."}

@app.delete("/order_log")
def clear_order_log():
    with open("../Jsons/order_log.json", 'w') as f:
        f.write('')
    return {"RESPONSE": "Order log cleared."}

@app.on_event("startup")
def initialize_order_log():
    with open("../Jsons/order_log.json", 'w') as f:
        f.write('')
    logInfo("Order log initialized.")

@app.on_event("shutdown")
def save_order_log():
    with open("../Jsons/order_log.json", 'a') as f:
        json.dump(order_log, f, indent=4)
