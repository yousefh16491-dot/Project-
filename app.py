import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go


# =========================
# Fetch Stock Data
# =========================
def get_stock_data(symbol, period="1mo"):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)

        if hist.empty:
            return None, "Invalid stock symbol or no data available."

        try:
            info = stock.info
        except:
            info = {}

        stock_name = info.get("longName", symbol)

        current_price = info.get("currentPrice")
        if current_price is None:
            current_price = hist["Close"].iloc[-1]

        return {
            "hist": hist,
            "info": info,
            "name": stock_name,
            "price": current_price
        }, None

    except Exception as e:
        return None, f"API Error: {str(e)}"


# =========================
# Process Data
# =========================
def process_data(data_dict):
    df = data_dict["hist"].copy()

    df = df[["Open", "High", "Low", "Close", "Volume"]]

    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["Daily Change"] = df["Close"].diff()

    return df


# =========================
# Create Chart
# =========================
def create_charts(df, stock_name):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["Close"],
        name="Close Price"
    ))

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["MA20"],
        name="20-Day Moving Average"
    ))

    fig.update_layout(
        title=f"{stock_name} Stock Trend Analysis",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_white",
        hovermode="x unified"
    )

    return fig


# =========================
# Main App
# =========================
def main():
    st.set_page_config(
        page_title="Stocker Dashboard",
        layout="wide"
    )

    st.title("📊 Stocker - Stock Market Analysis Dashboard")
    st.markdown("---")

    col1, col2 = st.columns([1, 3])

    with col1:
        symbol = st.text_input(
            "Enter Stock Symbol",
            value="AAPL"
        ).strip().upper()

        period = st.selectbox(
            "Select Period",
            ["1wk", "1mo", "3mo", "1y", "5y"],
            index=1
        )

    if symbol:
        data, error = get_stock_data(symbol, period)

        if error:
            st.error(error)

        elif data:
            with col2:
                st.subheader(f"Results for {data['name']}")

                st.metric(
                    "Current Price",
                    f"${data['price']:.2f}"
                )

                processed_df = process_data(data)

                chart = create_charts(
                    processed_df,
                    data["name"]
                )

                st.plotly_chart(
                    chart,
                    use_container_width=True
                )

                with st.expander("Historical Data"):
                    st.dataframe(processed_df.tail(10))


if __name__ == "__main__":
    main()
