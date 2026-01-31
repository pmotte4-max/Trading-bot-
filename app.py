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

# --- BYBIT API LOGIK (V5 Earn) ---
def get_bybit_apr():
    # Wir nutzen den öffentlichen Endpunkt für Earn-Produkte
    url = "https://api.bybit.com/v5/earn/product/search"
    params = {"category": "FLEXIBLE"}
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data.get("retCode") == 0:
            # Bybit liefert die Liste unter ['result']['productList']
            products = data["result"]["productList"]
            # Sortieren nach APR (höchste zuerst)
            # Hinweis: Bybit liefert APR oft als String wie "0.05" für 5%
            sorted_list = sorted(products, key=lambda x: float(x.get("estimateApr", 0)), reverse=True)
            return sorted_list
        return None
    except Exception as e:
        print(f"Bybit Error: {e}")
        return None

# --- TELEGRAM BEFEHLE ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Trading Bot aktiv! 📈\nSchreibe 'Status', um die aktuellen Top APRs zu sehen.")

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    text = message.text.lower()
    if "status" in text:
        bot.reply_to(message, "Frage Bybit-Daten ab... 📊")
        data = get_bybit_apr()
        if data:
            top_3 = data[:3]
            res = "🚀 **Top 3 Bybit APR (Flexible):**\n\n"
            for item in top_3:
                apr_val = float(item['estimateApr']) * 100
                res += f"💰 **{item['coin']}**: {apr_val:.2f}% APR\n"
            bot.send_message(message.chat.id, res, parse_mode="Markdown")
        else:
            bot.reply_to(message, "Konnte keine Daten von Bybit empfangen. ❌")
    else:
        bot.reply_to(message, "Ich reagiere momentan nur auf das Wort 'Status'.")

# --- AUTOMATISCHER TICKER (Alle 15 Min) ---
def scheduled_ticker():
    while True:
        # Kurze Pause beim Start, damit der Webserver Zeit hat
        time.sleep(10)
        data = get_bybit_apr()
        if data:
            top = data[0]
            apr_percent = float(top['estimateApr']) * 100
            msg = f"🔔 **Intervall-Update:**\nDer Top-Coin ist **{top['coin']}** mit {apr_percent:.2f}% APR!"
            try:
                bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
            except Exception as e:
                print(f"Ticker Error: {e}")
        time.sleep(900) # 15 Minuten

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
