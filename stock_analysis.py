import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

def get_stock_data(ticker, start='2020-01-01', end='2025-01-01'):
    stock = yf.Ticker(ticker)
    data = stock.history(start=start, end=end)
    return data

def plot_stock_data(data, ticker):
    fig, ax = plt.subplots(figsize=(12,6))
    ax.plot(data['Close'], label=f'{ticker} Closing Price')
    ax.set_title(f'{ticker} Stock Price Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.legend()
    st.pyplot(fig)

def calculate_moving_averages(data, short_window=50, long_window=200):
    data['SMA50'] = data['Close'].rolling(window=short_window).mean()
    data['SMA200'] = data['Close'].rolling(window=long_window).mean()
    return data

def plot_moving_averages(data, ticker):
    fig, ax = plt.subplots(figsize=(12,6))
    ax.plot(data['Close'], label='Closing Price', color='black')
    ax.plot(data['SMA50'], label='50-day SMA', color='blue')
    ax.plot(data['SMA200'], label='200-day SMA', color='red')
    ax.set_title(f'{ticker} Moving Averages')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.legend()
    st.pyplot(fig)

def analyze_stock(ticker):
    data = get_stock_data(ticker)
    data = calculate_moving_averages(data)
    
    latest_price = data['Close'].iloc[-1]
    sma50 = data['SMA50'].iloc[-1]
    sma200 = data['SMA200'].iloc[-1]
    
    signal = ""
    if sma50 > sma200:
        signal = "Bullish trend - Consider buying"
    elif sma50 < sma200:
        signal = "Bearish trend - Consider caution"
    else:
        signal = "Neutral trend"
    
    st.write(f"**Latest price:** {latest_price:.2f}")
    st.write(f"**50-day SMA:** {sma50:.2f}")
    st.write(f"**200-day SMA:** {sma200:.2f}")
    st.write(f"### Investment Signal: {signal}")
    
    plot_stock_data(data, ticker)
    plot_moving_averages(data, ticker)

def get_top_stocks():
    watchlist = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    recommendations = {}
    
    for ticker in watchlist:
        data = get_stock_data(ticker, start='2024-01-01')
        data = calculate_moving_averages(data)
        
        sma50 = data['SMA50'].iloc[-1]
        sma200 = data['SMA200'].iloc[-1]
        
        if sma50 > sma200:
            recommendations[ticker] = "Bullish trend - Consider buying"
        else:
            recommendations[ticker] = "Bearish/Neutral trend - Observe"
    
    return recommendations

def main():
    st.title("Stock Analysis Tool")
    menu = ["Search for a Stock", "Daily Recommendations"]
    choice = st.sidebar.selectbox("Choose an option", menu)
    
    if choice == "Search for a Stock":
        ticker = st.text_input("Enter stock ticker:").upper()
        if ticker:
            analyze_stock(ticker)
    elif choice == "Daily Recommendations":
        recommendations = get_top_stocks()
        for ticker, signal in recommendations.items():
            st.write(f"**{ticker}:** {signal}")

if __name__ == "__main__":
    main()
