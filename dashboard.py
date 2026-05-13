from flask import Flask, render_template_string
import yfinance as yf
import pandas as pd
import os

app = Flask(__name__)

stocks = [
    "BBCA.JK",
    "BBRI.JK",
    "BMRI.JK",
    "BBNI.JK",
    "TLKM.JK",
    "ASII.JK",
    "ANTM.JK",
    "MDKA.JK",
    "GOTO.JK",
    "ADRO.JK"
]

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>RENNO STOCK DASHBOARD</title>

    <meta http-equiv="refresh" content="300">

    <style>
        body{
            background:#0f172a;
            color:white;
            font-family:Arial;
            padding:20px;
        }

        h1{
            text-align:center;
            color:#38bdf8;
            margin-bottom:30px;
        }

        .container{
            display:grid;
            grid-template-columns:repeat(auto-fit, minmax(300px,1fr));
            gap:20px;
        }

        .card{
            background:#1e293b;
            padding:20px;
            border-radius:20px;
            box-shadow:0 0 15px rgba(0,0,0,0.3);
        }

        .green{
            color:#22c55e;
        }

        .red{
            color:#ef4444;
        }

        .signal{
            font-size:20px;
            font-weight:bold;
            margin-top:10px;
        }
    </style>
</head>

<body>

    <h1>🚀 RENNO STOCK DASHBOARD</h1>

    <div class="container">

    {% for stock in data %}
        <div class="card">

            <h2>{{ stock.symbol }}</h2>

            <p>Price: <b>{{ stock.price }}</b></p>

            {% if stock.change >= 0 %}
                <p class="green">Change: +{{ stock.change }}%</p>
            {% else %}
                <p class="red">Change: {{ stock.change }}%</p>
            {% endif %}

            <p>Volume: {{ stock.volume }}</p>

            <p>MA20: {{ stock.ma20 }}</p>
            <p>MA50: {{ stock.ma50 }}</p>

            <div class="signal">
                Signal: {{ stock.signal }}
            </div>

        </div>
    {% endfor %}

    </div>

</body>
</html>
"""

@app.route("/")
def home():

    data = []

    for symbol in stocks:

        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="3mo")

            if hist.empty:
                continue

            close = hist["Close"]

            last_price = round(close.iloc[-1], 2)
            prev_price = close.iloc[-2]

            change = round(
                ((last_price - prev_price) / prev_price) * 100,
                2
            )

            volume = int(hist["Volume"].iloc[-1])

            ma20 = round(close.rolling(20).mean().iloc[-1], 2)
            ma50 = round(close.rolling(50).mean().iloc[-1], 2)

            signal = "WATCH"

            if last_price > ma20 and ma20 > ma50:
                signal = "BUY"

            if change > 5:
                signal = "BREAKOUT"

            data.append({
                "symbol": symbol,
                "price": last_price,
                "change": change,
                "volume": f"{volume:,}",
                "ma20": ma20,
                "ma50": ma50,
                "signal": signal
            })

        except Exception as e:
            print(f"ERROR {symbol}: {e}")

    return render_template_string(HTML, data=data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
