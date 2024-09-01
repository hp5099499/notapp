import streamlit as st
import requests
from bs4 import BeautifulSoup
import yfinance as yf
from yahooquery import search
import pandas as pd
import time

# Apply custom CSS styling from file
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Function to fetch Top Gainers from NSE
def fetch_gainers():
    url = 'https://www.nseindia.com/api/live-analysis-variations?index=gainers'
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.nseindia.com/"
    }
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)
    response = session.get(url, headers=headers)

    if response.status_code == 200:
        try:
            data = response.json().get('legends', [])
            selected_legend = st.sidebar.selectbox("Select a Gainer Legend:", [legend[0] for legend in data])
            if selected_legend:
                table = [{
                    "Symbol": item['symbol'],
                    "Open Price": f"{item['open_price']:.2f}",
                    "High Price": f"{item['high_price']:.2f}",
                    "Low Price": f"{item['low_price']:.2f}",
                    "Previous Price": f"{item['prev_price']:.2f}",
                    "Change (%)": f"{item['perChange']:.2f}"
                } for item in response.json()[selected_legend]["data"]]
                # Add index starting from 1
                df = pd.DataFrame(table)
                df.index += 1
                st.table(df)
        except (requests.exceptions.JSONDecodeError, KeyError) as e:
            st.error(f"Failed to parse JSON: {e}")
    else:
        st.error(f"Failed to retrieve data. Status code: {response.status_code}")

# Function to scrape Top Losers from Groww
def scrape_top_losers():
    url = "https://groww.in/markets/top-losers"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find('table')
    if not table:
        return []
    
    headers = [header.get_text() for header in table.find_all('th')]
    rows = [
        dict(zip(headers, [col.get_text(strip=True) for col in row.find_all('td')]))
        for row in table.find_all('tr')[1:] if row.find_all('td')
    ]
    return rows

# Function to get tickers from company names using Yahoo Query
def get_tickers_from_names(companies):
    tickers = {}
    for company in companies:
        try:
            results = search(company).get('quotes', [])
            tickers[company] = results[0]['symbol'] if results else None
        except Exception:
            tickers[company] = None
    return tickers

# Function to fetch stock data using YFinance
def fetch_stock_data(tickers):
    data = {}
    for company, symbol in tickers.items():
        if not symbol:
            data[company] = {key: None for key in ['Open Price', 'High Price', 'Low Price', 'Previous Close', 'Close', 'Change (%)']}
            continue
        
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period='5d')
            if len(hist) >= 2:
                prev_close = hist['Close'].iloc[-2]
                curr_close = hist['Close'].iloc[-1]
                change = curr_close - prev_close
                data[company] = {
                    'Open Price': f"{hist['Open'].iloc[-1]:.2f}",
                    'High Price': f"{hist['High'].iloc[-1]:.2f}",
                    'Low Price': f"{hist['Low'].iloc[-1]:.2f}",
                    'Previous Close': f"{prev_close:.2f}",
                    'Close': f"{curr_close:.2f}",
                    'Change (%)': f"{(change / prev_close) * 100:.2f}"
                }
            else:
                data[company] = {key: None for key in ['Open Price', 'High Price', 'Low Price', 'Previous Close', 'Close', 'Change (%)']}
        except Exception as e:
            st.error(f"Error fetching data for {company}: {e}")
            data[company] = {key: None for key in ['Open Price', 'High Price', 'Low Price', 'Previous Close', 'Close', 'Change (%)']}
    
    return data

# Function to fetch real-time index data
def fetch_indices(indices):
    index_data = {}
    for name, ticker in indices.items():
        try:
            index = yf.Ticker(ticker)
            data = index.history(period="5d")
            if len(data) < 2:
                index_data[name] = {'close': None, 'change': None, 'percent_change': None}
                continue

            previous_close = data['Close'].iloc[-2]
            current_close = data['Close'].iloc[-1]
            change = current_close - previous_close
            percent_change = (change / previous_close) * 100

            index_data[name] = {
                'close': current_close,
                'change': change,
                'percent_change': percent_change
            }
        except Exception as e:
            st.error(f"Error fetching data for {name}: {e}")
            index_data[name] = {'close': None, 'change': None, 'percent_change': None}
    
    return index_data

# Streamlit layout for displaying Top Losers
@st.cache_data(ttl=3600)  # Cache data for 86400 seconds (1 day)
def get_loser_data():
    data = scrape_top_losers()
    if data:
        companies = [item['Company'] for item in data]
        tickers = get_tickers_from_names(companies)
        stock_data = fetch_stock_data(tickers)
        table = [{
            "Symbol": symbol,
            "Open Price": stock_info['Open Price'],
            "High Price": stock_info['High Price'],
            "Low Price": stock_info['Low Price'],
            "Previous Close": stock_info['Previous Close'],
            "Close": stock_info['Close'],
            "Change (%)": stock_info['Change (%)']
        } for symbol, stock_info in stock_data.items()]
        return table
    else:
        return []

# Function to display the cached data
def display_losers():
    with st.spinner('Loading data...'):
        table = get_loser_data()
        if table:
            df = pd.DataFrame(table)
            df.index += 1  # Add index starting from 1
            st.table(df)
        else:
            st.write('No data found or unable to fetch data.')

# Function to display Real-Time Indices Data
# Function to display Real-Time Indices Data
def display_indices():
    indices = {
        "Nifty 50": "^NSEI", "Nifty Bank": "^NSEBANK", "Sensex": "^BSESN",
        "Finnifty": "NIFTY_FIN_SERVICE.NS", "Nifty 100": "^CNX100", 
        "S&P 500": "^GSPC", "Dow Jones": "^DJI"
    }
    
    data = fetch_indices(indices)
    
    # Dynamic column creation based on the number of indices
    num_indices = len(data)
    cols_per_row = 4  # Number of columns per row for better display
    num_rows = (num_indices + cols_per_row - 1) // cols_per_row  # Calculate the required number of rows

    # Iterate over rows
    for row in range(num_rows):
        cols = st.columns(cols_per_row)  # Create columns for the current row
        for col_index in range(cols_per_row):
            index = row * cols_per_row + col_index
            if index < num_indices:
                name, stats = list(data.items())[index]
                cols[col_index].metric(
                    label=name,
                    value=f"{stats['close']:.2f}" if stats['close'] else "N/A",
                    delta=f"{stats['change']:.2f} ({stats['percent_change']:.2f}%)" if stats['change'] else "N/A"
                )
# Main function to run the app
def main():
    st.title("Financial Dashboard")
    fetch_gainers()
    display_losers()
    display_indices()

if __name__ == "__main__":
    main()
