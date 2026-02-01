import os
import time
import datetime
import requests
import threading
from flask import Flask

app = Flask(__name__)

# --- PAPIER-TRADE PARAMETER ---
trading_masse = 1000.0   # Startkapital USDC
bnb_reserve = 50.0       # Festgelegte BNB Reserve (50$)
safe_usdc_pool = 0.0     # Ernte-Pool
active_trades = []       
LOT_SIZES = [0.50, 0.35, 0.15]
daily_start_balance = 1000.0

BOT_NAMES = [
    "Genesis-Alpha (Mo)", "Volatility-Rider (Di)", "Midweek-Scalper (Mi)", 
    "Liquidity-Hunter (Do)", "Weekend-Frontrunner (Fr)", "Retail-Pulse (Sa)", "Harvest-Master (So)"
]

def get_market_data():
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        res = requests.get(url, timeout=10)
        return res.json() if res.status_code == 200 else []
    except:
        return []

def run_simulation():
    global trading_masse, safe_usdc_pool, active_trades, daily_start_balance
    
    while True:
        jetzt = datetime.datetime.now()
        tag_idx = jetzt.weekday()
        bot_name = BOT_NAMES[tag_idx]
        
        # 15-MINUTEN LOG
        market_data = get_market_data()
        print(f"\n--- 🕒 {jetzt.strftime('%H:%M')} | Bot: {bot_name} ---")
        print(f"💰 Portfolio: {trading_masse:.2f} USDC | 🎫 BNB: {bnb_reserve:.2f}$ | 🏦 Safe: {safe_usdc_pool:.2f}$")

        # Momentum-Suche (Proxy für APR-Steigerung)
        candidates = sorted([c for c in market_data if float(c['priceChangePercent']) > 2.0], 
                            key=lambda x: float(x['priceChangePercent']), reverse=True)

        # Simulierter Kauf
        if jetzt.hour != 21:
            for coin in candidates:
                if len(active_trades) < 3 and not any(t['symbol'] == coin['symbol'] for t in active_trades):
                    idx = len(active_trades)
                    invest = trading_masse * LOT_SIZES[idx]
                    active_trades.append({
                        "symbol": coin['symbol'], "buy_price": float(coin['lastPrice']),
                        "amount": invest, "slot": idx + 1
                    })
                    print(f"🚀 BUY: {coin['symbol']} im Slot {idx+1} ({LOT_SIZES[idx]*100}%)")

        # PNL Tracking
        total_pnl = 0
        for t in active_trades:
            curr = next((c for c in market_data if c['symbol'] == t['symbol']), None)
            if curr:
                p = float(curr['lastPrice'])
                pnl = (p - t['buy_price']) * (t['amount'] / t['buy_price'])
                total_pnl += pnl
                print(f"📈 {t['symbol']}: {pnl:+.2f} USDC")

        # 21:00 UHR REPORT & WEEKLY HARVEST
        if jetzt.hour == 21 and jetzt.minute < 15:
            current_total = trading_masse + total_pnl
            print(f"\n📢 TAGES-REPORT {bot_name}")
            print(f"Einnahmen heute: {current_total - daily_start_balance:+.2f} USDC")
            
            # Spezial-Logik: Erster Wochen-Payout am Sonntag
            if tag_idx == 6:
                payout = current_total * 0.25
                safe_usdc_pool += payout
                trading_masse = current_total - payout
                print(f"🏦 SONNTAGS-ERNTE: {payout:.2f} USDC -> Safe-Pool")
            else:
                trading_masse = current_total
            
            daily_start_balance = trading_masse
            time.sleep(900)

        time.sleep(900)

@app.route('/')
def home():
    return {
        "bot": BOT_NAMES[datetime.datetime.now().weekday()],
        "trading_masse_usdc": round(trading_masse, 2),
        "bnb_reserve_usd": bnb_reserve,
        "safe_pool_usdc": round(safe_usdc_pool, 2),
        "trades_aktiv": len(active_trades)
    }, 200

if __name__ == "__main__":
    threading.Thread(target=run_simulation, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
