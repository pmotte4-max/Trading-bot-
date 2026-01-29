import os
import ccxt
import time
from flask import Flask
import threading
import sys

app = Flask(__name__)

@app.route('/')
def home():
    return "Trading Bot Frankfurt ist ONLINE und aktiv!"

def run_scanner():
    # Verbindung zu Bybit
    exchange = ccxt.bybit({
        'apiKey': os.environ.get('BINANCE_API_KEY'),
        'secret': os.environ.get('BYBIT_API_KEY'),
        'enableRateLimit': True,
    })

    print("--- 🛰️ STARTE APR-SCANNER (FRANKFURT) ---", flush=True)

    while True:
        try:
            # Kontostand abrufen
        