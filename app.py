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

# --- BYBIT DATEN (Robustere Abfrage) ---
def get_bybit_apr():
    url = "https://api.bybit.com/v5/earn/product/search"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    try:
        # Wir fügen verify=False hinzu, falls SSL-Zertifikate Probleme machen
        response = requests.get(url, params={"category": "FLEXIBLE"}, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("retCode") == 0:
                products = data["result"].get("productList", [])
                return sorted(products, key=lambda x: float(x.get("estimateApr", 0)), reverse=True)
        return []
    except Exception as e:
        print(f"Abfrage-Fehler: {e}")
        return []

# --- TELEGRAM BEFEHLE ---
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if "status" in message.text.lower():
        bot.reply_to(message, "Frage Bybit-Daten ab... 📊")
        data = get_bybit_apr()
        if data:
            res = "🚀 **Top APR (Bybit):**\n\n"
            for item in data[:3]:
                apr = float(item.get('estimateApr', 0)) * 100
                res += f"💰 **{item.get('coin')}**: {apr:.2f}% APR\n"
            bot.send_message(message.chat.id, res, parse_mode="Markdown")
        else:
            bot.reply_to(message, "Bybit blockiert aktuell die Anfrage. Ich versuche es im Hintergrund weiter! 🔄")

# --- WEB SERVER FÜR RENDER ---
@app.route('/')
def health(): return "Bot is online", 200

if __name__ == "__main__":
    # Startet das Polling in einem eigenen Thread
    threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
