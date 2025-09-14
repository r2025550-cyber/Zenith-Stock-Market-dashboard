from flask import Flask, render_template, request
import requests, os, pandas as pd, json
from datetime import datetime

app = Flask(__name__)

# Railway / Heroku Environment Variables
ALPHA_KEY = os.environ.get("alpha_vantage_api_key")
BOT_TOKEN = os.environ.get("telegram_bot_token")
CHAT_ID = os.environ.get("telegram_chat_id")

# In-memory storage (simple). For production use a database.
stocks_tracked = []
alerts_sent = []

def fetch_stock(symbol):
    """Fetch intraday series from Alpha Vantage and return latest price and dataframe."""
    if not ALPHA_KEY:
        return None, None
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={ALPHA_KEY}"
    r = requests.get(url).json()
    if "Time Series (5min)" not in r:
        return None, None
    ts = r["Time Series (5min)"]
    df = pd.DataFrame(ts).T.astype(float).sort_index()
    latest_price = df.iloc[-1]["1. open"]
    # Basic signal logic (customize as needed)
    signal = "BUY" if latest_price > 1000 else "HOLD"
    # Send Telegram alert if BOT_TOKEN and CHAT_ID are set
    if BOT_TOKEN and CHAT_ID:
        try:
            msg = f"📊 {symbol}\n💰 Price: ₹{latest_price:.2f}\n📈 Signal: {signal}"
            requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", params={"chat_id": CHAT_ID, "text": msg}, timeout=5)
        except Exception:
            pass
    # Store a short alert history
    alerts_sent.append({
        "symbol": symbol,
        "price": f"{latest_price:.2f}",
        "signal": signal,
        "time": datetime.now().strftime("%H:%M:%S")
    })
    return latest_price, df

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    global stocks_tracked
    stock_data = {}

    if request.method == 'POST':
        symbol = request.form.get('symbol', '').upper().strip()
        if symbol and symbol not in stocks_tracked:
            stocks_tracked.append(symbol)

    # Gather watched stocks
    for symbol in stocks_tracked:
        price, df = fetch_stock(symbol)
        if df is not None:
            stock_data[symbol] = {
                'price': f"{price:.2f}",
                'time': df.index.tolist()[-20:],
                'history': df['1. open'].tolist()[-20:]
            }

    # Trending stocks (always show)
    trending_stocks = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS"]
    trending_data = {}
    for symbol in trending_stocks:
        price, df = fetch_stock(symbol)
        if df is not None:
            trending_data[symbol] = {
                'price': f"{price:.2f}",
                'time': df.index.tolist()[-20:],
                'history': df['1. open'].tolist()[-20:]
            }

    return render_template('index.html',
                           stock_data=json.dumps(stock_data),
                           trending_data=json.dumps(trending_data),
                           alerts=alerts_sent)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
