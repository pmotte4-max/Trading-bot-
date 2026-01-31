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

# --- BYBIT API LOGIK (Extrem stabil) ---
def get_bybit_apr():
    # Wir probieren den stabilsten Endpunkt
    url = "https://api.bybit.com/v5/earn/product/search"
    params = {"category": "FLEXIBLE"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        data = response.json()
        
        # Prüfen ob Daten da sind, bevor wir sortieren
        if data and data.get("retCode") == 0 and data.get("result"):
            products = data["result"].get("productList", [])
            if products:
                # Sicherer Sortier-Vorgang
                return sorted(products, key=lambda x: float(x.get("estimateApr", 0)), reverse=True)
        return [] # Leere Liste statt None zurückgeben
    except Exception as e:
        print(f"Bybit Fehler: {e}")
        return []

# --- TELEGRAM BEFEHLE ---
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if "status" in message.text.lower():
        bot.reply_to(message, "Suche beste APRs... 🔍")
        data = get_bybit_apr()
        if data and len(data) > 0:
            top_3 = data[:3]
            res = "🚀 **Top 3 Bybit APR:**\n\n"
            for item in top_3:
                apr = float(item.get('estimateApr', 0)) * 100
                res += f"💰 **{item.get('coin')}**: {apr:.2f}% APR\n"
            bot.send_message(message.chat.id, res, parse_mode="Markdown")
        else:
            bot.reply_to(message, "Bybit liefert gerade keine Daten. Ich versuche es gleich nochmal! ⏳")

# --- TICKER (Alle 15 Min) ---
def scheduled_ticker():
    while True:
        time.sleep(900)
        data = get_bybit_apr()
        if data and len(data) > 0:
            top = data[0]
            apr = float(top.get('estimateApr', 0)) * 100
            msg = f"🔔 **Update:** {top.get('coin')} bei {apr:.2f}% APR!"
            try:
                bot.send_message(CHAT_ID, msg)
            except: pass

@app.route('/')
def health(): return "OK", 200

if __name__ == "__main__":
    threading.Thread(target=scheduled_ticker, daemon=True).start()
    threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
