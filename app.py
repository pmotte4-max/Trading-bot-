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

# --- BYBIT API LOGIK (Mit Browser-Tarnung) ---
def get_bybit_apr():
    url = "https://api.bybit.com/v5/earn/product/search"
    params = {"category": "FLEXIBLE"}
    # Diese Zeilen tarnen den Server als echten Webbrowser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        data = response.json()
        
        if data.get("retCode") == 0:
            products = data["result"]["productList"]
            # Sortieren nach APR (höchste zuerst)
            sorted_list = sorted(products, key=lambda x: float(x.get("estimateApr", 0)), reverse=True)
            return sorted_list
        else:
            print(f"Bybit API Fehler: {data.get('retMsg')}")
            return None
    except Exception as e:
        print(f"Verbindungsfehler: {e}")
        return None

# --- TELEGRAM BEFEHLE ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Trading Bot aktiv! 📈\nSchreibe 'Status', um die aktuellen Top APRs von Bybit zu sehen.")

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    text = message.text.lower()
    if "status" in text:
        bot.reply_to(message, "Frage Bybit-Daten ab (via Frankfurt)... 📊")
        data = get_bybit_apr()
        if data:
            top_3 = data[:3]
            res = "🚀 **Top 3 Bybit APR (Flexible):**\n\n"
            for item in top_3:
                apr_val = float(item['estimateApr']) * 100
                res += f"💰 **{item['coin']}**: {apr_val:.2f}% APR\n"
            bot.send_message(message.chat.id, res, parse_mode="Markdown")
        else:
            bot.reply_to(message, "Bybit antwortet gerade nicht. Eventuell wird der Server blockiert. ❌")
    else:
        bot.reply_to(message, "Ich höre nur auf das Wort 'Status'.")

# --- AUTOMATISCHER TICKER (Alle 15 Min) ---
def scheduled_ticker():
    # Kleiner Delay beim ersten Start
    time.sleep(20)
    while True:
        data = get_bybit_apr()
        if data and len(data) > 0:
            top = data[0]
            apr_percent = float(top['estimateApr']) * 100
            msg = f"🔔 **Automatisches Update:**\nBester Coin: **{top['coin']}** mit {apr_percent:.2f}% APR!"
            try:
                bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
            except Exception as e:
                print(f"Ticker Fehler: {e}")
        time.sleep(900) # 15 Minuten

# --- FLASK WEB-SERVER ---
@app.route('/')
def health_check():
    return "Bot is online!", 200

if __name__ == "__main__":
    # Threads starten
    threading.Thread(target=scheduled_ticker, daemon=True).start()
    threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()
    
    # Port für Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
