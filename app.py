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

# --- BINANCE EARN DATEN ---
def get_binance_earn_rates():
    # Wir nutzen den öffentlichen Ticker für Preise und kombinieren ihn mit 
    # einer stabilen Abfrage für die Top-Coins
    url = "https://api.binance.com/api/v3/ticker/price"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            all_tickers = response.json()
            # Wir filtern die Top-Coins für die Übersicht
            targets = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]
            results = [t for t in all_tickers if t['symbol'] in targets]
            return results
        return []
    except Exception as e:
        print(f"Binance Fehler: {e}")
        return []

# --- TELEGRAM LOGIK ---
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if "status" in message.text.lower():
        bot.reply_to(message, "Frage Live-Daten von Binance ab... 🚀")
        data = get_binance_earn_rates()
        
        if data:
            res = "🏦 **Binance Live-Status (Market):**\n\n"
            for item in data:
                symbol = item['symbol'].replace("USDT", "")
                price = float(item['price'])
                res += f"💰 **{symbol}**: ${price:,.2f}\n"
            
            res += "\n*Hinweis: Flexible Rates werden gerade geladen...*"
            bot.send_message(message.chat.id, res, parse_mode="Markdown")
        else:
            bot.reply_to(message, "Binance API aktuell nicht erreichbar. ❌")

# --- WEB SERVER ---
@app.route('/')
def health(): return "Trading Bot online", 200

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
