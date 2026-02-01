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

# --- DATEN-ABFRAGE (Binance Live-Schnittstelle) ---
def get_binance_data():
    # Wir holen die Top-Coins für Marktübersicht und Earn-Basis
    url = "https://api.binance.com/api/v3/ticker/24hr"
    targets = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "USDCUSDT"]
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            all_data = response.json()
            # Filtert nur die gewünschten Paare heraus
            return [item for item in all_data if item['symbol'] in targets]
        return []
    except Exception as e:
        print(f"API-Fehler: {e}")
        return []

# --- TELEGRAM ANFRAGEN ---
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    text = message.text.lower()
    
    if "status" in text:
        bot.reply_to(message, "Daten werden von Binance (Frankfurt) abgerufen... 📊")
        data = get_crypto_data_summary()
        
        if data:
            res = "🚀 **Live Markt-Update:**\n\n"
            for coin in data:
                sym = coin['symbol'].replace("USDT", "")
                price = float(coin['lastPrice'])
                change = float(coin['priceChangePercent'])
                emoji = "📈" if change > 0 else "📉"
                
                # Schöne Preis-Formatierung
                price_str = f"{price:,.2f}" if price >= 1 else f"{price:.4f}"
                res += f"💰 **{sym}**: ${price_str} ({emoji} {change:+.2f}%)\n"
            
            res += "\n_Tipp: CoinMarketCap Integration folgt für Earn-Rates!_"
            bot.send_message(message.chat.id, res, parse_mode="Markdown")
        else:
            bot.reply_to(message, "Datenquelle aktuell nicht erreichbar. ❌")

def get_crypto_data_summary():
    # Hilfsfunktion für die Datenaufbereitung
    return get_binance_data()

# --- SERVER FÜR RENDER ---
@app.route('/')
def health():
    return "Bot is online!", 200

if __name__ == "__main__":
    # Startet das Polling in einem eigenen Thread, damit der Webserver parallel läuft
    threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()
    
    # Port-Zuweisung durch Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
