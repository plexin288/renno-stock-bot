from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

import yfinance as yf
import pandas as pd
import os
import asyncio

# =========================================
# TOKEN BOT
# =========================================

TOKEN = os.getenv("TOKEN")

# =========================================
# WATCHLIST MOMENTUM IDX
# =========================================

IDX_STOCKS = [

    # ENERGY & COAL
    "ADRO.JK","ADMR.JK","ITMG.JK","PTBA.JK",
    "HRUM.JK","INDY.JK","BUMI.JK","DOID.JK",
    "MEDC.JK","PGAS.JK","ESSA.JK",

    # NICKEL & MINING
    "CUAN.JK","MDKA.JK","INCO.JK","BRMS.JK",
    "PTRO.JK","BREN.JK","CDIA.JK",

    # TECHNOLOGY
    "GOTO.JK","BUKA.JK","DNET.JK","EDGE.JK",

    # PROPERTY
    "BSDE.JK","PWON.JK","CTRA.JK","SMRA.JK,
    "CBDK.JK",

    # LOW PRICE MOMENTUM
    "ABBA.JK","HUMA.JK","CBRE.JK","DOOH.JK",
    "SOTS.JK","NICL.JK","KKGI.JK","WIFI.JK",
    "RBMS.JK","TMAS.JK","BAPA.JK","CARE.JK",
    "JGLE.JK","ZYRX.JK","GPSO.JK","MHKI.JK",

    # RETAIL & CONSUMER
    "AMRT.JK","ACES.JK","ERAA.JK","MAPI.JK",
    "MYOR.JK","ICBP.JK","INDF.JK",

    # TELEKOMUNIKASI
    "EXCL.JK","ISAT.JK","TLKM.JK",

    # HEALTHCARE
    "HEAL.JK","MIKA.JK","SILO.JK",

    # INDUSTRIAL
    "UNTR.JK","SMGR.JK","JPFA.JK","CPIN.JK",

    # HIGH MOMENTUM
    "BREN.JK","CUAN.JK","TPIA.JK","RAJA.JK",
    "WIFI.JK","ARTO.JK","TMAS.JK","PANI.JK",
    "FILM.JK","NCKL.JK","MBMA.JK"
]

# =========================================
# ANALISA SAHAM
# =========================================

def analyze_stock(df, stock):

    try:

        # FIX MULTI INDEX
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # VALIDASI
        if df.empty or len(df) < 50:
            return None

        close = df["Close"]
        openp = df["Open"]
        high = df["High"]
        low = df["Low"]
        volume = df["Volume"]

        close_now = float(close.iloc[-1])
        close_prev = float(close.iloc[-2])

        open_now = float(openp.iloc[-1])
        high_now = float(high.iloc[-1])

        volume_now = float(volume.iloc[-1])

        # VALIDASI DATA
        if (
            pd.isna(close_now) or
            pd.isna(close_prev) or
            close_prev == 0
        ):
            return None

        # =========================================
        # CHANGE %
        # =========================================

        change_percent = (
            (close_now - close_prev)
            / close_prev
        ) * 100

        change_percent = round(change_percent, 2)

        # FILTER >7%
        if change_percent < 7:
            return None

        # FILTER VOLUME
        if volume_now < 500000:
            return None

        # FILTER HARGA
        if close_now < 50:
            return None

        # =========================================
        # RSI 14
        # =========================================

        delta = close.diff()

        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()

        rs = avg_gain / avg_loss

        rsi = 100 - (100 / (1 + rs))

        current_rsi = round(
            float(rsi.iloc[-1]),
            2
        )

        # =========================================
        # MACD
        # =========================================

        exp1 = close.ewm(span=12).mean()
        exp2 = close.ewm(span=26).mean()

        macd = exp1 - exp2
        signal = macd.ewm(span=9).mean()

        macd_now = float(macd.iloc[-1])
        signal_now = float(signal.iloc[-1])

        macd_bullish = (
            macd_now > signal_now
        )

        # =========================================
        # MA20 vs MA50
        # =========================================

        ma20 = float(
            close.rolling(20).mean().iloc[-1]
        )

        ma50 = float(
            close.rolling(50).mean().iloc[-1]
        )

        trend_bullish = ma20 > ma50

        # =========================================
        # VOLUME SURGE
        # =========================================

        avg_volume = float(
            volume.tail(20).mean()
        )

        volume_surge = (
            volume_now > avg_volume * 1.5
        )

        # =========================================
        # BREAKOUT DETECTOR
        # =========================================

        recent_resistance = float(
            high.tail(20).max()
        )

        breakout_valid = (
            close_now >= recent_resistance * 0.99
        )

        # =========================================
        # FAKE BREAKOUT FILTER
        # =========================================

        fake_breakout = False

        if (
            breakout_valid and
            volume_now < avg_volume and
            close_now < high_now * 0.97
        ):

            fake_breakout = True

        # SKIP FAKE BREAKOUT
        if fake_breakout:
            return None

        # =========================================
        # SUPPORT & RESISTANCE
        # =========================================

        support = int(
            low.tail(20).min()
        )

        resistance = int(
            high.tail(20).max()
        )

        # =========================================
        # FOREIGN FLOW
        # =========================================

        transaction_value = (
            close_now * volume_now
        )

        foreign_flow = "Neutral"

        if (
            close_now > open_now and
            volume_now > avg_volume * 2 and
            transaction_value > 10_000_000_000
        ):

            foreign_flow = "Strong Inflow"

        elif (
            close_now < open_now and
            volume_now > avg_volume * 2
        ):

            foreign_flow = "Outflow"

        # =========================================
        # BANDAR DETECTOR
        # =========================================

        bandar_detected = False

        if (
            close_now > ma20 and
            volume_now > avg_volume * 1.8 and
            close_now >= high_now * 0.97
        ):

            bandar_detected = True

        # =========================================
        # STATUS SIGNAL
        # =========================================

        status_signal = "WEAK"

        if (
            change_percent >= 7 and
            macd_bullish and
            volume_surge
        ):

            status_signal = "GOOD"

        if (
            change_percent >= 10 and
            macd_bullish and
            volume_surge and
            bandar_detected and
            trend_bullish and
            breakout_valid
        ):

            status_signal = "STRONG BUY"

        # =========================================
        # ENTRY TP SL
        # =========================================

        entry = round(close_now, 0)

        tp1 = round(close_now * 1.05, 0)
        tp2 = round(close_now * 1.10, 0)

        sl = round(support * 0.98, 0)

        # =========================================
        # SCORE
        # =========================================

        score = 0

        if macd_bullish:
            score += 2

        if volume_surge:
            score += 2

        if bandar_detected:
            score += 3

        if trend_bullish:
            score += 2

        if breakout_valid:
            score += 2

        if foreign_flow == "Strong Inflow":
            score += 1

        # =========================================
        # AI ANALYSIS
        # =========================================

        analysis = []

        if breakout_valid:
            analysis.append("Breakout resistance")

        if macd_bullish:
            analysis.append("MACD bullish")

        if volume_surge:
            analysis.append("Volume surge tinggi")

        if bandar_detected:
            analysis.append("Akumulasi bandar")

        if trend_bullish:
            analysis.append("MA20 > MA50")

        if current_rsi < 70:
            analysis.append("Belum overbought")

        ai_text = ". ".join(analysis)

        # =========================================
        # OUTPUT
        # =========================================

        result_text = f"""
🚀 {stock}

📈 Change: +{change_percent}%
⭐ Score: {score}/12
🔥 Status: {status_signal}

📊 RSI: {current_rsi}
📦 Volume Surge: {"YES" if volume_surge else "NO"}
📉 MACD: {"BULLISH" if macd_bullish else "BEARISH"}

📈 Breakout:
{"VALID" if breakout_valid else "NO"}

🚫 Fake Breakout:
{"YES" if fake_breakout else "NO"}

🌍 Foreign Flow:
{foreign_flow}

🏦 Bandar Detector:
{"ACCUMULATION" if bandar_detected else "NO DETECTION"}

🛡 Support: {support}
🎯 Resistance: {resistance}

🎯 ENTRY SETUP
━━━━━━━━━━
💰 Entry : {int(entry)}
🎯 TP1   : {int(tp1)}
🚀 TP2   : {int(tp2)}
🛑 SL    : {int(sl)}

🧠 AI Analysis:
{ai_text}
"""

        return {
            "score": score,
            "change": change_percent,
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
                period="6mo",
                interval="1d",
                progress=False,
                auto_adjust=True,
                threads=False
            )

            result = analyze_stock(df, stock)

            if result:
                results.append(result)

            await asyncio.sleep(0.05)

        except Exception as e:

            print(f"{stock} ERROR: {e}")

    # TIDAK ADA HASIL
    if not results:

        await update.message.reply_text(
            "❌ Tidak ada saham >7% hari ini."
        )

        return

    # SORT
    results = sorted(
        results,
        key=lambda x: (
            x["score"],
            x["change"]
        ),
        reverse=True
    )

    # OUTPUT
    final_text = "🔥 TOP MOMENTUM IDX 🔥\n\n"

    for item in results:

        text_to_add = item["text"] + "\n\n"

        if (
            len(final_text)
            + len(text_to_add)
            > 3900
        ):
            break

        final_text += text_to_add

    await update.message.reply_text(
        final_text
    )

# =========================================
# COMMAND /START
# =========================================

async def start(update: Update,
                context: ContextTypes.DEFAULT_TYPE):

    text = """
🤖 RENNO STOCK SCANNER

📊 FEATURES:
✅ Saham naik >7%
✅ RSI 14
✅ MACD
✅ MA20 vs MA50
✅ Volume Surge
✅ Breakout Detector
✅ Fake Breakout Filter
✅ Foreign Flow
✅ Bandar Detector
✅ Entry TP SL
✅ AI Analysis
✅ Status Signal

📌 COMMAND:
/scan
/status
/help
"""

    await update.message.reply_text(text)

# =========================================
# COMMAND /STATUS
# =========================================

async def status(update: Update,
                 context: ContextTypes.DEFAULT_TYPE):

    text = f"""
🟢 RENNO BOT STATUS

📡 Data Source:
Yahoo Finance

⚡ Scanner:
ACTIVE

📊 Watchlist:
{len(IDX_STOCKS)} saham

🔥 Filter:
Only stocks >7%

🤖 System:
RUNNING NORMAL
"""

    await update.message.reply_text(text)

# =========================================
# COMMAND /HELP
# =========================================

async def help_command(update: Update,
                       context: ContextTypes.DEFAULT_TYPE):

    text = """
📖 RENNO BOT COMMANDS

/start
➡️ Menu utama

/scan
➡️ Scan saham momentum >7%

/status
➡️ Check status bot

/help
➡️ Bantuan command
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

app.add_handler(
    CommandHandler("status", status)
)

app.add_handler(
    CommandHandler("help", help_command)
)

print("🚀 BOT RUNNING...")

app.run_polling()
