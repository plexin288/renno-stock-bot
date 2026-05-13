import streamlit as st
import yfinance as yf
import pandas as pd

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="RENNO STOCK DASHBOARD",
    layout="wide"
)

# =========================================
# WATCHLIST 30 SAHAM
# =========================================

IDX_STOCKS = [

    "BREN.JK","CUAN.JK","TPIA.JK","RAJA.JK",
    "WIFI.JK","ARTO.JK","TMAS.JK","PANI.JK",
    "FILM.JK","NCKL.JK","MBMA.JK","ABBA.JK",

    "HUMA.JK","CBRE.JK","DOOH.JK","SOTS.JK",
    "NICL.JK","KKGI.JK","BKSL.JK","CARE.JK",

    "GOTO.JK","BUKA.JK","DNET.JK","EDGE.JK",

    "ADRO.JK","ANTM.JK","MDKA.JK","BRMS.JK",

    "EXCL.JK","ISAT.JK"
]

# =========================================
# TITLE
# =========================================

st.title("🚀 RENNO STOCK DASHBOARD")

st.markdown("""
Monitor saham harian IDX
""")

# =========================================
# SCAN FUNCTION
# =========================================

def scan_stock(stock):

    try:

        df = yf.download(
            stock,
            period="6mo",
            interval="1d",
            progress=False,
            auto_adjust=True,
            threads=False
        )

        if df.empty or len(df) < 50:
            return None

        close = df["Close"]
        high = df["High"]
        volume = df["Volume"]

        close_now = float(close.iloc[-1])
        close_prev = float(close.iloc[-2])

        volume_now = float(volume.iloc[-1])

        # CHANGE %
        change_percent = (
            (close_now - close_prev)
            / close_prev
        ) * 100

        change_percent = round(change_percent, 2)

        # RSI
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

        # MACD
        exp1 = close.ewm(span=12).mean()
        exp2 = close.ewm(span=26).mean()

        macd = exp1 - exp2
        signal = macd.ewm(span=9).mean()

        macd_now = float(macd.iloc[-1])
        signal_now = float(signal.iloc[-1])

        macd_bullish = (
            macd_now > signal_now
        )

        # VOLUME SURGE
        avg_volume = float(
            volume.tail(20).mean()
        )

        volume_surge = (
            volume_now > avg_volume * 1.5
        )

        # BREAKOUT
        resistance = float(
            high.tail(20).max()
        )

        breakout_valid = (
            close_now >= resistance * 0.99
        )

        # STATUS
        status = "WEAK"

        if (
            macd_bullish and
            volume_surge
        ):

            status = "GOOD"

        if (
            breakout_valid and
            volume_surge and
            macd_bullish
        ):

            status = "STRONG BUY"

        # SCORE
        score = 0

        if macd_bullish:
            score += 2

        if volume_surge:
            score += 2

        if breakout_valid:
            score += 3

        return {

            "Stock": stock,
            "Price": round(close_now, 0),
            "Change %": change_percent,
            "RSI": current_rsi,
            "Volume Surge": (
                "YES"
                if volume_surge
                else "NO"
            ),
            "Breakout": (
                "VALID"
                if breakout_valid
                else "NO"
            ),
            "Score": score,
            "Status": status

        }

    except:
        return None

# =========================================
# SCANNING
# =========================================

results = []

progress = st.progress(0)

for i, stock in enumerate(IDX_STOCKS):

    result = scan_stock(stock)

    if result:
        results.append(result)

    progress.progress(
        (i + 1) / len(IDX_STOCKS)
    )

# =========================================
# DISPLAY
# =========================================

if results:

    df_results = pd.DataFrame(results)

    df_results = df_results.sort_values(
        by=["Score", "Change %"],
        ascending=False
    )

    # METRICS
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "📊 Total Stocks",
        len(df_results)
    )

    col2.metric(
        "🔥 Strong Buy",
        len(
            df_results[
                df_results["Status"]
                == "STRONG BUY"
            ]
        )
    )

    col3.metric(
        "🚀 Top Gainer",
        f"{df_results.iloc[0]['Change %']}%"
    )

    st.divider()

    st.subheader("📈 STOCK MONITOR")

    st.dataframe(
        df_results,
        use_container_width=True
    )

else:

    st.warning(
        "Tidak ada data saham."
    )
