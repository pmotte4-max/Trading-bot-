import os
import time
import requests
import threading
import telebot
from flask import Flask
from datetime import datetime

app = Flask(__name__)

# --- CONFIG (Werte kommen sicher aus Render) ---
TELEGRAM_TOKEN = "8597158635:AAFL3ah1yxQwXV9ntnChwY9sZRl6mcemt5s"
TELEGRAM_CHAT_ID = 5810124088
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Diese Namen müssen exakt mit deinen Render-Variablen übereinstimmen:
BYBIT_API_KEY = os.getenv('BYBIT_API_KEY')
BYBIT_API_SECRET = os.getenv('BYBIT_API_SECRET')

# --- BYBIT API LOGIK ---
def get_bybit_apr_live():
    """Holt die echten Live-APR von Bybit Flexible Savings"""
    url = "https://api.bybit.com/v5/earn/product-info"
    params = {"category": "FlexibleSaving"}
    try:
        response = requests.get(url, params=params, timeout=10).json()
        if response.get("retCode") == 0:
            products = response["result"]["list"]
            # Umrechnung und Sortierung nach höchster APR
            data = {p["coin"]: float(p["estimateApr"]) * 100 for p in products}
            return dict(sorted(data.items(), key=lambda item: item[1], reverse=True))
    except Exception as e:
        print(f"Bybit API Fehler: {e}")
    return {}

# --- INTERAKTIVE ANTWORT-FUNKTION ---
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    # Nur antworten, wenn du schreibst
    if str(message.chat.id) == str(TELEGRAM_CHAT_ID):
        aprs = get_bybit_apr_live()
        if aprs:
            top_3 = list(aprs.items())[:3]
            reply = "👋 *Ich habe deine Nachricht erhalten!*\n\nHier sind die aktuellen Top 3 APRs:\n"
            for coin, val in top_3:
                reply += f"💰 *{coin}*: {val:.2f}%\n"
            reply += "\nWas möchtest du als Nächstes wissen?"
        else:
            reply = "⚠️ Konnte aktuell keine Daten von Bybit abrufen. Prüfe die API-Keys!"
        
        bot.reply_to(message, reply, parse_mode="Markdown")

# --- 15-MINUTEN AUTOMATIK-TICKER ---
def scheduled_ticker():
    while True:
        # Alle 15 Minuten (900 Sekunden)
        aprs = get_bybit_apr_live()
        if aprs:
            top_5 = list(aprs.items())[:5]
            msg = "📊 *15-Minuten Update (Top Sprünge)*\n\n"
            for coin, val in top_5:
                emoji = "🔥" if val > 50 else "✅"
                msg += f"{emoji} {coin}: {val:.2f}%\n"
            
            bot.send_message(TELEGRAM_CHAT_ID, msg, parse_mode="Markdown")
        
        time.sleep(900)

@app.route('/')
def home():
    return f"Bot ist aktiv. Letzter System-Check: {datetime.now().strftime('%H:%M:%S')}"

# Threads für Hintergrund-Aufgaben starten
if __name__ != "__main__": # Wichtig für Render/Gunicorn
    threading.Thread(target=scheduled_ticker, daemon=True).start()
    threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()

if __name__ == "__main__":
    # Lokaler Start (für Tests)
    threading.Thread(target=scheduled_ticker, daemon=True).start()
    threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
