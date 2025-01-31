import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import requests
import numpy as np

def get_stock_data(ticker, start='2020-01-01'):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(start=start)
        if data.empty:
            return None, None, None
        return data, stock.info.get('longName', ticker), stock.info
    except:
        return None, None, None

def get_external_ratings(ticker):
    rating_sources = {
        "Yahoo Finance": f"https://finance.yahoo.com/quote/{ticker}/analysis",
        "Morningstar": f"https://www.morningstar.com/stocks/xnas/{ticker}/quote",
        "Seeking Alpha": f"https://seekingalpha.com/symbol/{ticker}",
    }
    return rating_sources

def get_ticker_by_name_or_isin(query):
    try:
        search_url = f"https://query1.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=5&newsCount=0"
        response = requests.get(search_url).json()
        if 'quotes' in response and response['quotes']:
            return [q['symbol'] for q in response['quotes']]
    except:
        return []
    return []

def find_valid_ticker(query):
    possible_tickers = get_ticker_by_name_or_isin(query)
    suffixes = ["", ".TO", ".DE", ".PA", ".L", ".F", ".SW", ".MI"]  # Häufige Börsen-Suffixe
    valid_ticker = None
    checked_tickers = []
    
    for ticker in possible_tickers:
        for suffix in suffixes:
            full_ticker = ticker + suffix
            checked_tickers.append(full_ticker)
            data, name, info = get_stock_data(full_ticker)
            if data is not None:
                return full_ticker, []
    
    return None, checked_tickers

def plot_stock_data_interactive(data, ticker):
    fig = px.line(data, x=data.index, y='Close', title=f'Aktienkursverlauf von {ticker}', labels={'Close': 'Preis', 'index': 'Datum'})
    st.plotly_chart(fig)

def calculate_indicators(data):
    data['SMA50'] = data['Close'].rolling(window=50).mean()
    data['SMA200'] = data['Close'].rolling(window=200).mean()
    data['RSI'] = 100 - (100 / (1 + (data['Close'].diff().clip(lower=0).rolling(14).mean() / data['Close'].diff().clip(upper=0).abs().rolling(14).mean())))
    data['MACD'] = data['Close'].ewm(span=12, adjust=False).mean() - data['Close'].ewm(span=26, adjust=False).mean()
    data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()
    data['Bollinger_Upper'] = data['Close'].rolling(window=20).mean() + (data['Close'].rolling(window=20).std() * 2)
    data['Bollinger_Lower'] = data['Close'].rolling(window=20).mean() - (data['Close'].rolling(window=20).std() * 2)
    return data

def calculate_score(sma50, sma200, rsi, macd, signal_line):
    score = 0
    score += 0.4 if sma50 > sma200 else -0.4
    score += 0.2 if rsi < 70 else -0.2
    score += 0.2 if macd > signal_line else -0.2
    return round(score, 2)

def analyze_stock(ticker):
    data, name, info = get_stock_data(ticker)
    if data is None:
        st.write("❌ Aktie nicht gefunden oder keine Daten verfügbar.")
        return
    
    data = calculate_indicators(data)
    latest_price = data['Close'].iloc[-1]
    sma50 = data['SMA50'].iloc[-1]
    sma200 = data['SMA200'].iloc[-1]
    rsi = data['RSI'].iloc[-1]
    macd = data['MACD'].iloc[-1]
    signal_line = data['Signal_Line'].iloc[-1]
    pe_ratio = info.get('trailingPE', 'N/A')
    dividend_yield = info.get('dividendYield', 'N/A')
    
    score = calculate_score(sma50, sma200, rsi, macd, signal_line)
    signal = "Neutral"
    reason = "Keine klare Kauf- oder Verkaufsempfehlung."
    
    if score > 0.5:
        signal = "Kaufsignal"
        reason = "Der berechnete Score zeigt eine insgesamt positive Marktstruktur."
    elif score < -0.5:
        signal = "Vorsicht geboten"
        reason = "Der berechnete Score zeigt eine negative Marktstruktur."
    
    st.write(f"### {name} ({ticker})")
    st.write(f"**Aktueller Preis:** {latest_price:.2f} USD")
    st.write(f"**Score:** {score}")
    st.write(f"**Empfehlung:** {signal}")
    st.write(f"**Begründung:** {reason}")
    plot_stock_data_interactive(data, ticker)

def main():
    st.title("Aktienanalyse Tool")
    menu = ["Aktie suchen", "Tägliche Empfehlungen"]
    choice = st.sidebar.selectbox("Wähle eine Option", menu)
    
    if choice == "Aktie suchen":
        search_query = st.text_input("Gib den Namen, das Kürzel oder die ISIN der Aktie ein:")
        ticker, checked_tickers = find_valid_ticker(search_query)
        
        if ticker:
            analyze_stock(ticker)
        else:
            st.write("❌ Aktie nicht gefunden. Bitte überprüfe deine Eingabe.")
            if checked_tickers:
                st.write("🔍 Mögliche getestete Alternativen:")
                for alt in checked_tickers:
                    st.write(f"- {alt}")

if __name__ == "__main__":
    main()
