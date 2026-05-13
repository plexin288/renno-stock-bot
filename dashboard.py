from flask import Flask, render_template_string
import yfinance as yf

app = Flask(__name__)

stocks = [
    "BBCA.JK","BBRI.JK","BMRI.JK","BBNI.JK","TLKM.JK",
    "ASII.JK","ADRO.JK","GOTO.JK","AMRT.JK","ICBP.JK",
    "INDF.JK","UNVR.JK","MDKA.JK","ANTM.JK","PGAS.JK"
]

@app.route("/")
def dashboard():

    results = []

    for stock in stocks:

        try:
            data = yf.download(stock, period="5d", progress=False)

            if data.empty:
                continue

            close_price = round(float(data["Close"].iloc[-1]), 2)
            prev_price = round(float(data["Close"].iloc[-2]), 2)

            change = round(
                ((close_price - prev_price) / prev_price) * 100,
                2
            )

            signal = "BUY" if change > 0 else "WAIT"

            trend = (
                "BULLISH"
                if change > 1
                else "SIDEWAYS"
            )

            results.append({
                "stock": stock,
                "price": close_price,
                "change": change,
                "trend": trend,
                "signal": signal
            })

        except:
            pass

    html = """

    <!DOCTYPE html>
    <html>
    <head>
        <title>RENNO STOCK DASHBOARD</title>

        <style>

            body{
                background:#0f172a;
                color:white;
                font-family:Arial;
                padding:40px;
            }

            h1{
                font-size:50px;
                margin-bottom:10px;
            }

            table{
                width:100%;
                border-collapse:collapse;
                margin-top:30px;
                background:#1e293b;
                border-radius:20px;
                overflow:hidden;
            }

            th, td{
                padding:18px;
                border-bottom:1px solid #334155;
                text-align:left;
            }

            th{
                background:#111827;
                color:#94a3b8;
            }

            tr:hover{
                background:#334155;
            }

            .green{
                color:#22c55e;
                font-weight:bold;
            }

            .yellow{
                color:#facc15;
                font-weight:bold;
            }

        </style>
    </head>

    <body>

        <h1>🚀 RENNO STOCK DASHBOARD</h1>
        <p>Realtime IDX Market Monitor</p>

        <table>

            <thead>
                <tr>
                    <th>Stock</th>
                    <th>Price</th>
                    <th>Change</th>
                    <th>Trend</th>
                    <th>Signal</th>
                </tr>
            </thead>

            <tbody>

                {% for s in results %}

                <tr>

                    <td><b>{{ s.stock }}</b></td>

                    <td>{{ s.price }}</td>

                    <td class="{{ 'green' if s.change > 0 else 'yellow' }}">
                        {{ s.change }}%
                    </td>

                    <td>{{ s.trend }}</td>

                    <td class="{{ 'green' if s.signal == 'BUY' else 'yellow' }}">
                        {{ s.signal }}
                    </td>

                </tr>

                {% endfor %}

            </tbody>

        </table>

    </body>
    </html>

    """

    return render_template_string(html, results=results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
