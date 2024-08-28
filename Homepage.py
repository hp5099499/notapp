import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from stocknews import StockNews 

def display():
    # Title of the app
    
    # Time range mapping
    time_range_map = {
        "1m": ("1mo", "1d"),
        "6m": ("6mo", "1wk"),
        "1y": ("1y", "1d"),
        "5y": ("5y", "1mo"),
        "all": ("max", "3mo")
    }
    
    # Option to choose between time range or fixed date range
    range_option = st.sidebar.radio("Select Range Type", ["1 Week", "Time Range"])
    
    # Input for stock ticker
    ticker = st.sidebar.text_input('Enter Stock Ticker', 'AAPL')
    
    if ticker:
        if range_option == "Time Range":
            # Selector for time range
            time_range = st.sidebar.selectbox("Select Time Range", list(time_range_map.keys()))
    
            # Get the period and interval from time_range_map
            period, interval = time_range_map[time_range]
    
            # Download the stock data
            stock_data = yf.download(ticker, period=period, interval=interval)
    
            # st.write(f'Stock data for {ticker} with {time_range} range')
    
        elif range_option == "1 Week":
            # Calculate the date range
            end_date = datetime.now() - timedelta(days=1)  # Yesterday
            start_date = end_date - timedelta(days=7)  # One week ago
    
            # Convert dates to strings
            end_date_str = end_date.strftime('%Y-%m-%d')
            start_date_str = start_date.strftime('%Y-%m-%d')
    
            # Download the stock data
            stock_data = yf.download(ticker, start=start_date_str, end=end_date_str)
    
            # st.write(f'Stock data for {ticker} from {start_date_str} to {end_date_str}')
    
        # Ensure stock_data is not empty before proceeding
        if not stock_data.empty:
            # Define the dates you want to remove
            dates_to_remove = [datetime(2024, 7, 27), datetime(2024, 7, 28)]  # Update these dates as needed
    
            # Convert the list of dates to strings in the format used by stock_data.index
            dates_to_remove_str = [date.strftime('%Y-%m-%d') for date in dates_to_remove]
    
            # Check if these dates are present in the stock data
            available_dates_to_remove = [date for date in dates_to_remove_str if date in stock_data.index.strftime('%Y-%m-%d')]
    
            # Filter out specific dates if they exist
            if available_dates_to_remove:
                stock_data = stock_data.loc[~stock_data.index.strftime('%Y-%m-%d').isin(available_dates_to_remove)]
    
            # Display the stock data
            # st.dataframe(stock_data)
    
            # Create a container with columns for buttons
            st.markdown(ticker.upper())        
            st.header(f"{stock_data.Close.iloc[-1]:.2f}" )        
    
            p_d=stock_data.Close.iloc[-1]-stock_data.Open[1]
            pd_p=(p_d/stock_data.Open[1])*100
            color = "green" if p_d >= 0 else "red"
            st.markdown(f"<h1 style='color:{color};font-size: 15px;padding:0px'>{p_d:.2f} ({pd_p:.2f})%</h1>", unsafe_allow_html=True)        
            st.write('Stock Data Viewer with Various Charts')
            
            col1, col2, col3 ,col4= st.tabs(["LineChart","OHLC chart","Candles stick","Bar chart"])
    
            with col1:
                    
                        if not stock_data.empty:
                            # Line plot of stock data for prediction (example implementation)
                            fig = px.line(stock_data, x=stock_data.index, y='Close', title=f'{ticker} Price Over Time')
                            st.plotly_chart(fig)
                        else:
                            st.write('No data available for sentiment prediction.')
    
            with col2:
                    
                        if not stock_data.empty:
                            # OHLC chart of stock data (example implementation)
                            fig = go.Figure(data=[go.Ohlc(
                                x=stock_data.index,
                                open=stock_data['Open'],
                                high=stock_data['High'],
                                low=stock_data['Low'],
                                close=stock_data['Close']
                            )])
                            fig.update_layout(
                                title=f'OHLC Chart for {ticker}',
                                xaxis_title='Date',
                                yaxis_title='Price',
                                xaxis_rangeslider_visible=False
                            )
                            st.plotly_chart(fig)
                        else:
                            st.write('No data available for OHLC chart.')
    
            with col3:
                    
                        if not stock_data.empty:
                            # Create the candlestick chart
                            fig = go.Figure(data=[go.Candlestick(
                                x=stock_data.index,
                                open=stock_data['Open'],
                                high=stock_data['High'],
                                low=stock_data['Low'],
                                close=stock_data['Close']
                            )])
                
                            # Calculate missing dates for range breaks
                            all_days = set(stock_data.index.date)
                            dates_to_remove_dates = set(date.date() for date in dates_to_remove)
                            missing_dates = sorted(dates_to_remove_dates - all_days)
    
                            # Convert missing dates to a list of Timestamp objects
                            missing_dates_timestamps = [pd.Timestamp(date) for date in missing_dates]
                
                            # Update the layout of the chart
                            fig.update_layout(
                                title=f'Candlestick Chart for {ticker}',
                                xaxis_title='Date',
                                yaxis_title='Price',
                                xaxis_rangeslider_visible=False
                            )
                
                            # Add range breaks to exclude missing dates
                            if missing_dates_timestamps:
                                fig.update_xaxes(rangebreaks=[dict(values=missing_dates_timestamps)])
                
                            # Display the candlestick chart
                            st.plotly_chart(fig)
                        else:
                            st.write('No data available for the selected date range.')
            
            with col4:
                        if not stock_data.empty:
                            # Bar chart of stock data (example implementation)
                            fig = px.bar(stock_data, x=stock_data.index, y='Volume', title=f'{ticker} Trading Volume Over Time')
                            st.plotly_chart(fig)
                        else:
                            st.write('No data available for bar chart.')
        
    
            # Creating tabs for different sections
            performance_metrics, fundamental_data, news = st.tabs(["Performance Metrics","Fundamental Data","Top 10 News"])        
    
            # Pricing Data Section
            with performance_metrics:
                st.markdown("<div class='section-header'>Performance Metrics</div>", unsafe_allow_html=True)
                st.markdown("<hr>", unsafe_allow_html=True)        
    
                st.markdown("<div class='sub-header'>Price Movement</div>", unsafe_allow_html=True)        
    
                data2 = stock_data.copy()
                data2['% Change'] = stock_data['Adj Close'] / stock_data['Adj Close'].shift(1) - 1
                data2.dropna(inplace=True)
                st.write(data2)        
    
                # Calculating annual return, standard deviation, and risk-adjusted return
                annual_return = data2['% Change'].mean() * 252 * 100
                stdev = np.std(data2['% Change']) * np.sqrt(252)
                risk_adj_return = annual_return / stdev if stdev != 0 else 0        
    
                # Displaying formatted values with growth symbols
                col1,col2,col3=st.columns(3)
                with col1:
                      growth_symbol = lambda x: "📈" if x > 0 else "📉" if x < 0 else ""
                      st.header(f"{annual_return:.2f}% {growth_symbol(annual_return)}")
                      st.write("Annual Return (%)")
                with col2:
                      st.header(f"{stdev * 100:.2f}% {growth_symbol(stdev)}")
                      st.write('Standard Deviation (%)')
                with col3:
                   st.header(f"{risk_adj_return:.2f} {growth_symbol(risk_adj_return)}")
                   st.write('Risk Adj. Return')        
    
            # Fundamental Data Section (using yfinance for some fundamental data)
            with fundamental_data:        
    
            # Layout the section header
                st.markdown("<div class='section-header'>Fundamental Data</div>", unsafe_allow_html=True)
                st.markdown("<hr>", unsafe_allow_html=True)
                
                try:
                    info = yf.Ticker(ticker).info
                 
                    # General Info
                    st.markdown("<div class='sub-header'>General Info</div>", unsafe_allow_html=True)
                    general_info = {
                         "Company Name": [info.get('longName', 'N/A')],
                         "Sector": [info.get('sector', 'N/A')],
                         "Industry": [info.get('industry', 'N/A')],
                         "Country": [info.get('country', 'N/A')]
                     }
                    general_info_df = pd.DataFrame(general_info)
                    st.table(general_info_df)        
    
                     # Key Stats
                    st.markdown("<div class='sub-header'>Key Stats</div>", unsafe_allow_html=True)
                    key_stats = {
                         "Market Cap": [f"{info.get('marketCap', 'N/A'):,}" if info.get('marketCap') else 'N/A'],
                         "Forward PE Ratio": [info.get('forwardPE', 'N/A')],
                         "Dividend Yield": [f"{info.get('dividendYield', 0):.2%}" if info.get('dividendYield') else 'N/A']
                     }
                    key_stats_df = pd.DataFrame(key_stats)
                    st.table(key_stats_df)
                        
    
                except Exception as e:
                    st.warning("Could not retrieve fundamental data.")
                    st.write(f"Error: {e}")        
            
    
            # News Section
            with news:
                st.markdown("<div class='section-header'>News</div>", unsafe_allow_html=True)
                sn = StockNews(ticker, save_news=False)
                df_news = sn.read_rss()        
    
                # Displaying top 10 news articles
                for i in range(min(10, len(df_news))):
                    st.markdown("<hr>", unsafe_allow_html=True)
                    st.markdown("<div class='news-item'>", unsafe_allow_html=True)
                    st.markdown(f"<div class='news-title'>{df_news['title'][i]}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='news-details'><b>Published:</b> {df_news['published'][i]}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='news-details'>{df_news['summary'][i]}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='news-details'><b>Title Sentiment:</b> {df_news['sentiment_title'][i]}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='news-details'><b>News Sentiment:</b> {df_news['sentiment_summary'][i]}</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
