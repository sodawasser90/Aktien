import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import requests

def get_stock_data(ticker, start='2020-01-01'):
    stock = yf.Ticker(ticker)
    data = stock.history(start=start)
    return data, stock.info.get('longName', ticker)

def get_external_ratings(ticker):
    rating_sources = {
        "Yahoo Finance": f"https://finance.yahoo.com/quote/{ticker}/analysis",
        "Morningstar": f"https://www.morningstar.com/stocks/xnas/{ticker}/quote",
        "Seeking Alpha": f"https://seekingalpha.com/symbol/{ticker}",
    }
    return rating_sources

def get_ticker_by_name(name):
    try:
        search_url = f"https://query1.finance.yahoo.com/v1/finance/search?q={name}&quotesCount=1&newsCount=0"
        response = requests.get(search_url).json()
        return response['quotes'][0]['symbol'] if 'quotes' in response and response['quotes'] else None
    except:
        return None

def plot_stock_data_interactive(data, ticker):
    fig = px.line(data, x=data.index, y='Close', title=f'Aktienkursverlauf von {ticker}', labels={'Close': 'Preis', 'index': 'Datum'})
    st.plotly_chart(fig)

def calculate_moving_averages(data, short_window=50, long_window=200):
    data['SMA50'] = data['Close'].rolling(window=short_window).mean()
    data['SMA200'] = data['Close'].rolling(window=long_window).mean()
    return data

def analyze_stock(ticker):
    data, name = get_stock_data(ticker)
    data = calculate_moving_averages(data)
    
    latest_price = data['Close'].iloc[-1]
    sma50 = data['SMA50'].iloc[-1]
    sma200 = data['SMA200'].iloc[-1]
    
    signal = ""
    reason = ""
    if sma50 > sma200:
        signal = "Kaufsignal"
        reason = "Der 50-Tage-Durchschnitt liegt über dem 200-Tage-Durchschnitt, was auf einen Aufwärtstrend hindeutet."
    elif sma50 < sma200:
        signal = "Vorsicht geboten"
        reason = "Der 50-Tage-Durchschnitt liegt unter dem 200-Tage-Durchschnitt, was auf eine mögliche Abwärtsbewegung hindeutet."
    else:
        signal = "Neutral"
        reason = "Die Durchschnitte liegen nahe beieinander, was keine klare Richtung signalisiert."
    
    st.write(f"### {name} ({ticker})")
    st.write(f"**Aktueller Preis:** {latest_price:.2f} USD")
    st.write(f"**50-Tage-SMA:** {sma50:.2f}")
    st.write(f"**200-Tage-SMA:** {sma200:.2f}")
    st.write(f"**Empfehlung:** {signal}")
    st.write(f"**Begründung:** {reason}")
    
    st.write("### Externe Bewertungen")
    for source, url in get_external_ratings(ticker).items():
        st.write(f"[{source}]({url})")
    
    plot_stock_data_interactive(data, ticker)

def get_top_stocks():
    recommendations = {}
    watchlist = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    
    for ticker in watchlist:
        data, name = get_stock_data(ticker)
        data = calculate_moving_averages(data)
        
        sma50 = data['SMA50'].iloc[-1]
        sma200 = data['SMA200'].iloc[-1]
        
        if sma50 > sma200:
            recommendations[ticker] = (name, "Kaufsignal")
    
    return recommendations

def main():
    st.title("Aktienanalyse Tool")
    menu = ["Aktie suchen", "Tägliche Empfehlungen"]
    choice = st.sidebar.selectbox("Wähle eine Option", menu)
    
    if choice == "Aktie suchen":
        search_query = st.text_input("Gib den Namen oder das Kürzel der Aktie ein:")
        ticker = get_ticker_by_name(search_query) if search_query and not search_query.isupper() else search_query.upper()
        
        if ticker:
            analyze_stock(ticker)
        else:
            st.write("Aktie nicht gefunden. Bitte überprüfe deine Eingabe.")
    elif choice == "Tägliche Empfehlungen":
        recommendations = get_top_stocks()
        if not recommendations:
            st.write("### Keine Millionen drin heute")
        else:
            for ticker, (name, signal) in recommendations.items():
                st.write(f"### {name} ({ticker})")
                st.write(f"**Empfehlung:** {signal}")
                analyze_stock(ticker)

if __name__ == "__main__":
    main()
