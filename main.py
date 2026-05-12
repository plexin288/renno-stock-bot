from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

import yfinance as yf
import pandas as pd
import numpy as np
import asyncio
import os

# =========================================
# TOKEN BOT
# =========================================

TOKEN = os.getenv("TOKEN")

# =========================================
# LIST SAHAM IDX
# =========================================

IDX_STOCKS = [

    "AALI.JK","ABBA.JK","ABDA.JK","ACES.JK",
    "ACST.JK","ADHI.JK","ADMR.JK","ADRO.JK",
    "AGII.JK","AKRA.JK","AMRT.JK","ANTM.JK",
    "ASII.JK","BBCA.JK","BBNI.JK","BBRI.JK",
    "BBTN.JK","BMRI.JK","BRIS.JK","BRMS.JK",
    "BSDE.JK","BUMI.JK","BUKA.JK","CPIN.JK",
    "CTRA.JK","DOID.JK","ELSA.JK","EMTK.JK",
    "ERAA.JK","ESSA.JK","EXCL.JK","GOTO.JK",
    "HEAL.JK","HMSP.JK","HRUM.JK","ICBP.JK",
    "INCO.JK","INDF.JK","INDY.JK","INTP.JK",
    "ISAT.JK","ITMG.JK","JPFA.JK","KLBF.JK",
    "LSIP.JK","MAPI.JK","MDKA.JK","MEDC.JK",
    "MIKA.JK","MYOR.JK","PGAS.JK","PTBA.JK",
    "PWON.JK","SIDO.JK","SILO.JK","SMGR.JK",
    "SMRA.JK","TLKM.JK","TPIA.JK","UNTR.JK",
    "UNVR.JK","ADMF.JK","BFIN.JK","BJBR.JK",
    "BJTM.JK","CMRY.JK","CUAN.JK","BREN.JK",
    "CBRE.JK","HUMA.JK","SOTS.JK","DOOH.JK"
]

# =========================================
# ANALISA SAHAM
# =========================================

def analyze_stock(df, stock):

    try:

        close_now = df['Close'].iloc[-1]
        close_prev = df['Close'].iloc[-2]

        change_percent = (
            (close_now - close_prev)
            / close_prev
        ) * 100

        # FILTER NAIK >7%
        if change_percent < 7:
            return None

        # RSI
        delta = df['Close'].diff()

        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()

        rs = avg_gain / avg_loss

        rsi = 100 - (100 / (1 + rs))

        current_rsi = round(rsi.iloc[-1], 2)

        # MACD
        exp1 = df['Close'].ewm(span=12).mean()
        exp2 = df['Close'].ewm(span=26).mean()

        macd = exp1 - exp2
        signal = macd.ewm(span=9).mean()

        macd_bullish = (
            macd.iloc[-1] > signal.iloc[-1]
        )

        # VOLUME
        avg_volume = df['Volume'].tail(20).mean()
        today_volume = df['Volume'].iloc[-1]

        volume_surge = (
            today_volume > avg_volume * 1.5
        )

        # FILTER SAHAM TIDUR
        if today_volume < 500000:
            return None

        # SUPPORT RESISTANCE
        support = int(
            df['Low'].tail(20).min()
        )

        resistance = int(
            df['High'].tail(20).max()
        )

        # FOREIGN FLOW
        open_price = df['Open'].iloc[-1]
        high_price = df['High'].iloc[-1]

        transaction_value = (
            close_now * today_volume
        )

        foreign_flow = "Neutral"

        if (
            close_now > open_price and
            today_volume > avg_volume * 2 and
            close_now >= high_price * 0.98 and
            transaction_value > 10_000_000_000
        ):

            foreign_flow = "Strong Inflow"

        elif (
            close_now < open_price and
            today_volume > avg_volume * 2
        ):

            foreign_flow = "Outflow"

        # BANDAR DETECTOR
        ma20 = df['Close'].rolling(20).mean()

        bandar_detected = False

        if (
            close_now > ma20.iloc[-1] and
            today_volume > avg_volume * 1.8 and
            close_now >= high_price * 0.97 and
            change_percent > 5
        ):

            bandar_detected = True

        # SCORE
        score = 0

        if volume_surge:
            score += 2

        if macd_bullish:
            score += 2

        if bandar_detected:
            score += 3

        if foreign_flow == "Strong Inflow":
            score += 3

        # AI ANALYSIS
        analysis = ""

        if macd_bullish:
            analysis += "MACD bullish. "

        if volume_surge:
            analysis += "Volume surge tinggi. "

        if bandar_detected:
            analysis += "Terindikasi akumulasi bandar. "

        if foreign_flow == "Strong Inflow":
            analysis += "Ada indikasi foreign inflow. "

        if current_rsi < 70:
            analysis += "Belum overbought."

        # OUTPUT
        result_text = f"""
🚀 {stock}

📈 Change: {change_percent:.2f}%
⭐ Score: {score}/10

📊 RSI: {current_rsi}
📦 Volume Surge: {"YES" if volume_surge else "NO"}

🌍 Foreign Flow:
{foreign_flow}

🏦 Bandar Detector:
{"ACCUMULATION DETECTED" if bandar_detected else "NO DETECTION"}

🛡 Support: {support}
🎯 Resistance: {resistance}

🧠 AI Analysis:
{analysis}
"""

        return {
            "change": change_percent,
            "score": score,
            "text": result_text
        }

    except Exception as e:

        print(f"{stock} ERROR: {e}")

        return None

# =========================================
# COMMAND /SCAN
# =========================================

async def scan(update: Update,
               context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🔎 Scanning saham IDX..."
    )

    results = []

    for stock in IDX_STOCKS:

        try:

            df = yf.download(
                stock,
                period="3mo",
                interval="1d",
                progress=False,
                threads=False
            )

            if df.empty or len(df) < 50:
                continue

            result = analyze_stock(df, stock)

            if result:
                results.append(result)

            await asyncio.sleep(0.3)

        except Exception as e:

            print(f"{stock} ERROR: {e}")

    if not results:

        await update.message.reply_text(
            "❌ Tidak ada saham naik >7% hari ini."
        )

        return

    results = sorted(
        results,
        key=lambda x: (
            x["score"],
            x["change"]
        ),
        reverse=True
    )

    top_25 = results[:25]

    final_text = "🔥 TOP GAINERS IDX\n\n"

    for item in top_25:

        final_text += item["text"]
        final_text += "\n\n"

    final_text = final_text[:4000]

    await update.message.reply_text(final_text)

# =========================================
# COMMAND /START
# =========================================

async def start(update: Update,
                context: ContextTypes.DEFAULT_TYPE):

    text = """
🤖 RENNO STOCK SCANNER

📊 Features:
- Filter saham naik >7%
- RSI 14
- MACD
- Volume Surge
- Foreign Flow
- Bandar Detector
- AI Analysis

Commands:
/scan
"""

    await update.message.reply_text(text)

# =========================================
# MAIN BOT
# =========================================

app = (
    ApplicationBuilder()
    .token(TOKEN)
    .build()
)

app.add_handler(
    CommandHandler("start", start)
)

app.add_handler(
    CommandHandler("scan", scan)
)

print("BOT RUNNING...")

app.run_polling()
