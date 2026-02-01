import os
import time
import requests
import threading
import telebot
from flask import Flask

# --- KONFIGURATION ---
# Die Variablen ziehen wir sicher aus den Render-Environment-Einstellungen
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- DATEN-ABFRAGE (Binance Live-Daten) ---
def get_crypto_data():
    # Wir holen die Top-Coins, die für Earn-Rates am wichtigsten sind
    url = "https://api.binance.com/api/v3/ticker/24hr"
    targets = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "USDCUSDT"]
    try:
        # Timeout erhöht auf 15s für stabile Verbindung
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            all_data = response.json()
            # Filtert nur die gewünschten Coins aus der riesigen Liste
            return [item for item in all_data if item['symbol'] in targets]
        return []
    except Exception as e:
        print(f"Fehler bei Binance-Abfrage: {e}")
        return []

# --- TELEGRAM BEFEHLE ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Trading Bot ist bereit! 📈\nSchreibe 'Status', um die Live-Werte zu sehen.")

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    text = message.text.lower()
    
    if "status" in text:
        bot.reply_to(message, "Rufe Marktdaten ab... 📊")
        data = get_crypto_data()
        
        if data:
            res = "🚀 **Live Markt-Update (Binance):**\n\n"
            for coin in data:
                # Formatierung der Symbole (z.B. BTCUSDT -> BTC)
                sym = coin['symbol'].replace("USDT", "")
                price = float(coin['lastPrice'])
                change = float(coin['priceChangePercent'])
                
                # Dynamisches Emoji je nach Kursverlauf
                emoji = "📈" if change > 0 else "📉"
                
                # Preis-Formatierung: Kleine Preise genauer, große Preise mit Tausender-Trennzeichen
                if price < 10:
                    res += f"💰 **{sym}**: ${price:.4f} ({emoji} {change:+.2f}%)\n"
                else:
                    res += f"💰 **{sym}**: ${price:,.2f} ({emoji} {change:+.2f}%)\n"
            
            res += "\n_Hinweis: CoinMarketCap Earn-Rates werden als nächstes integriert._"
            bot.send_message(message.chat.id, res, parse_mode="Markdown")
        else:
            bot.reply_to(message, "Konnte keine Daten von Binance empfangen. Bitte versuche es in einer Minute nochmal! ⏳")

# --- FLASK WEB-SERVER FÜR RENDER ---
@app.route('/')
def health_check():
    # Dieser Endpunkt sagt Render, dass der Bot noch "lebt"
    return "Bot is online and running!", 200

if __name__ == "__main__":
    # 1. Telegram Polling in einem eigenen Thread starten
    threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()
    
    # 2. Flask Web-Server auf dem von Render zugewiesenen Port starten
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
