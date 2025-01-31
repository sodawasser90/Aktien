import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import numpy as np
import time

# Alpha Vantage API-Schlüssel (kostenlos abrufbar unter https://www.alphavantage.co/support/#api-key)
API_KEY = "Y3MDWONI458XYMJ3"
BASE_URL = "https://www.alphavantage.co/query"

# Watchlist für tägliche Empfehlungen (S&P 500 + DAX Beispiele)
WATCHLIST = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN", "NVDA", "SAP", "DTE.DE", "AIR.PA", "NKE"]

def get_stock_data(ticker):
    time.sleep(12)  # Vermeidung von API-Limits (max. 5 Anfragen pro Minute bei Alpha Vantage)
    url = f"{BASE_URL}?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&apikey={API_KEY}&outputsize=compact"
    response = requests.get(url).json()
    
    if "Time Series (Daily)" not in response:
        return None, None
    
    data = pd.DataFrame.from_dict(response["Time Series (Daily)"], orient="index")
    data = data.rename(columns={
        "1. open": "Open",
        "2. high": "High",
        "3. low": "Low",
        "4. close": "Close",
        "5. adjusted close": "Adj Close",
        "6. volume": "Volume"
    }).astype(float)
    data.index = pd.to_datetime(data.index)
    return data[::-1], ticker

def get_ticker_by_isin(isin):
    url = f"{BASE_URL}?function=SYMBOL_SEARCH&keywords={isin}&apikey={API_KEY}"
    response = requests.get(url).json()
    if "bestMatches" in response and response["bestMatches"]:
        return response["bestMatches"][0]["1. symbol"]
    return None

def plot_stock_data_interactive(data, ticker):
    fig = px.line(data, x=data.index, y='Close', title=f'Aktienkursverlauf von {ticker}', labels={'Close': 'Preis', 'index': 'Datum'})
    st.plotly_chart(fig)

def analyze_stock(ticker):
    data, ticker = get_stock_data(ticker)
    if data is None:
        st.write("❌ Aktie nicht gefunden oder keine Daten verfügbar.")
        return
    
    latest_price = data['Close'].iloc[-1]
    
    st.write(f"### {ticker}")
    st.write(f"**Aktueller Preis:** {latest_price:.2f} USD")
    plot_stock_data_interactive(data, ticker)

def get_daily_recommendations():
    recommendations = []
    for ticker in WATCHLIST:
        data, ticker = get_stock_data(ticker)
        if data is not None:
            latest_price = data['Close'].iloc[-1]
            recommendations.append((ticker, latest_price))
    recommendations = sorted(recommendations, key=lambda x: x[1], reverse=True)  # Sortieren nach Preis
    return recommendations[:5]  # Top 5 Empfehlungen anzeigen

def main():
    st.title("Aktienanalyse Tool")
    menu = ["Aktie suchen", "Tägliche Empfehlungen"]
    choice = st.sidebar.selectbox("Wähle eine Option", menu)
    
    if choice == "Aktie suchen":
        search_query = st.text_input("Gib den Namen, das Kürzel oder die ISIN der Aktie ein:")
        
        if search_query:
            ticker = search_query.upper()
            if len(ticker) == 12 and ticker.isalnum():
                ticker = get_ticker_by_isin(ticker)
            
            if ticker:
                analyze_stock(ticker)
            else:
                st.write("❌ Aktie nicht gefunden. Bitte überprüfe deine Eingabe.")
    elif choice == "Tägliche Empfehlungen":
        st.write("### Tägliche Aktienempfehlungen")
        recommendations = get_daily_recommendations()
        if not recommendations:
            st.write("❌ Keine Empfehlungen verfügbar. Bitte später erneut versuchen.")
        else:
            for ticker, price in recommendations:
                st.write(f"**{ticker}:** {price:.2f} USD")
                analyze_stock(ticker)

if __name__ == "__main__":
    main()

