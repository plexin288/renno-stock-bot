from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <html>
    <head>
        <title>RENNO DASHBOARD</title>
        <style>
            body{
                background:#0f172a;
                color:white;
                font-family:Arial;
                text-align:center;
                padding-top:100px;
            }
        </style>
    </head>
    <body>
        <h1>🚀 RENNO DASHBOARD ACTIVE</h1>
        <p>Railway + Flask berhasil jalan</p>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
