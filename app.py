import os
import time
import requests
import threading
import telebot
from flask import Flask

# --- KONFIGURATION ---
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- BYBIT API LOGIK ---
def get_bybit_apr():
    url = "https://api.bybit.com/v5/asset/staking/product/list"
    params = {"coin": "", "productType": "FLEXIBLE"}
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data.get("retCode") == 0:
            products = data["result"]["list"]
            # Liste sortieren nach APR (höchste zuerst)
            sorted_list = sorted(products, key=lambda x: float(x.get("estimateApr", 0)), reverse=True)
            return sorted_list
        return None
    except Exception as e:
        print(f"Bybit Error: {e}")
        return None

# --- TELEGRAM BEFEHLE ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Willkommen beim Trading Bot! 📈\nSchreibe 'Status', um die aktuellen Top 3 APRs zu sehen.")

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    text = message.text.lower()
    if "status" in text:
        bot.reply_to(message, "Abfrage läuft... 📊")
        data = get_bybit_apr()
        if data:
            top_3 = data[:3]
            res = "🚀 **Top 3 Bybit APR (Flexible):**\n\n"
            for item in top_3:
                res += f"💰 {item['coin']}: {float(item['estimateApr'])*100:.2f}% APR\n"
            bot.send_message(message.chat.id, res, parse_mode="Markdown")
        else:
            bot.reply_to(message, "Konnte Daten von Bybit nicht laden. ❌")
    else:
        bot.reply_to(message, "Ich verstehe nur 'Status'. Versuche es mal! 😉")

# --- AUTOMATISCHER TICKER (Alle 15 Min) ---
def scheduled_ticker():
    while True:
        data = get_bybit_apr()
        if data:
            top = data[0]
            msg = f"🔔 **15-Minuten Update:**\nDer Top-Coin ist aktuell **{top['coin']}** mit {float(top['estimateApr'])*100:.2f}% APR!"
            bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
        time.sleep(900) # 900 Sekunden = 15 Minuten

# --- FLASK WEB-SERVER (Für Render & Cron-Job) ---
@app.route('/')
def health_check():
    return "Trading Bot is running!", 200

if __name__ == "__main__":
    # Ticker-Thread starten
    threading.Thread(target=scheduled_ticker, daemon=True).start()
    # Bot-Thread starten
    threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()
    
    # Port für Render setzen
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
