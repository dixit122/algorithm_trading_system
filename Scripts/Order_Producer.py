import requests
import json
from time import sleep
import random
from Logs import logInfo

#####################################################################
# This script produces random orders at 1 second intervals for 300s #
#####################################################################

with open("../Jsons/raw_details.json") as f:
    raw_details = json.load(f)

strategies = raw_details['STRATEGIES']
instruments = raw_details['INSTRUMENTS']
orders = ['BUY','SELL']

for i in range(300):
    order_payload = {
        "STRATEGY": strategies[random.randint(0,len(raw_details["STRATEGIES"]))-1],
        "INSTRUMENT": instruments[random.randint(0,len(raw_details["INSTRUMENTS"]))-1],
        "POSITION": orders[random.randint(0,len(orders))-1]
    }
    logInfo("Order created: {}".format(order_payload))
    r = requests.post("http://localhost:8080/create_order",json=order_payload)
    logInfo("Order response: {}".format(r.json()['RESPONSE']))
    sleep(1)

