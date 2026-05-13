from flask import Flask, render_template_string
import yfinance as yf

app = Flask(__name__)

stocks = [
    "BBCA.JK","BBRI.JK","BMRI.JK","BBNI.JK","TLKM.JK",
    "ASII.JK","ICBP.JK","INDF.JK","ANTM.JK","MDKA.JK",
    "ADRO.JK","PGAS.JK","UNVR.JK","GOTO.JK","AMRT.JK"
]

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>RENNO STOCK DASHBOARD</title>
    <meta http-equiv="refresh" content="300">
    <style>
        body {
            background: #0f172a;
            color: white;
            font-family: Arial;
            padding: 20px;
        }

        h1 {
            text-align: center;
            color: #38bdf8;
        }

        .card {
            background: #1e293b;
            padding: 15px;
            margin: 10px 0;
            border-radius: 12px;
        }

        .green {
            color: #22c55e;
        }

        .red {
            color: #ef4444;
        }
    </style>
</head>
<body>

<h1>🚀 RENNO STOCK DASHBOARD</h1>

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
</div>
{% endfor %}

</body>
</html>
"""

@app.route("/")
def home():
    data = []

    for symbol in stocks:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")

            if len(hist) < 2:
                continue

            last_price = round(hist["Close"].iloc[-1], 2)
            prev_price = hist["Close"].iloc[-2]

            change = round(((last_price - prev_price) / prev_price) * 100, 2)

            volume = int(hist["Volume"].iloc[-1])

            data.append({
                "symbol": symbol,
                "price": last_price,
                "change": change,
                "volume": f"{volume:,}"
            })

        except Exception as e:
            print(f"Error {symbol}: {e}")

    return render_template_string(HTML, data=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
