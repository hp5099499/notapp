import streamlit as st
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import uuid
import json
import re
from streamlit_navigation_bar import st_navbar


# analysis page
def analysis():
    import streamlit as st
    import pandas as pd
    import yfinance as yf
    from datetime import datetime, timedelta
    import plotly.graph_objects as go
    from ta.volatility import BollingerBands
    from ta.trend import MACD, EMAIndicator, SMAIndicator
    from ta.momentum import RSIIndicator
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import r2_score, mean_absolute_error
    import time
    
    
    st.subheader('Stock Price Predictions')
    
    def main():
        option = st.sidebar.selectbox('Make a choice', ['Visualize', 'Recent Data', 'Predict'])
        if option == 'Visualize':
            tech_indicators()
        elif option == 'Recent Data':
            update_data_and_plot()
            # st.markdown("[more...](https://predictre.streamlit.app)")
    
        elif option == 'Predict':
            predict()
        
    
    @st.cache_resource
    def download_data(op, start_date, end_date):
        df = yf.download(op, start=start_date, end=end_date, progress=False)
        return df
    
    option = st.sidebar.text_input('Enter a Stock Symbol', value='SPY')
    option = option.upper()
    today = datetime.today().date()
    duration = st.sidebar.number_input('Enter the duration', value=3000)
    before = today - timedelta(days=duration)
    start_date = st.sidebar.date_input('Start Date', value=before)
    end_date = st.sidebar.date_input('End date', today)
    if st.sidebar.button('Send'):
        if start_date < end_date:
            st.sidebar.success('Start date: `%s`\n\nEnd date: `%s`' % (start_date, end_date))
            data = download_data(option, start_date, end_date)
        else:
            st.sidebar.error('Error: End date must fall after start date')
    
    data = download_data(option, start_date, end_date)
    scaler = StandardScaler()
    
    # Compute the price difference and percentage change
    p_d = data.Close.iloc[-1] - data.Open.iloc[1]
    pd_p = (p_d / data.Open.iloc[1]) * 100
    
    def tech_indicators():
        st.header('Technical Indicators')
        option = st.radio('Choose a Technical Indicator to Visualize', ['Close', 'BB', 'MACD', 'RSI', 'SMA', 'EMA'])
    
        # Bollinger bands
        bb_indicator = BollingerBands(data.Close)
        bb = data.copy()
        bb['bb_h'] = bb_indicator.bollinger_hband()
        bb['bb_l'] = bb_indicator.bollinger_lband()
        # Creating a new dataframe
        bb = bb[['Close', 'bb_h', 'bb_l']]
        # MACD
        macd = MACD(data.Close).macd()
        # RSI
        rsi = RSIIndicator(data.Close).rsi()
        # SMA
        sma = SMAIndicator(data.Close, window=14).sma_indicator()
        # EMA
        ema = EMAIndicator(data.Close).ema_indicator()
    
        if option == 'Close':
            st.write('Close Price')
            st.line_chart(data['Close'])
        elif option == 'BB':
            st.write('BollingerBands')
            st.line_chart(bb)
        elif option == 'MACD':
            st.write('Moving Average Convergence Divergence')
            st.line_chart(macd)
        elif option == 'RSI':
            st.write('Relative Strength Indicator')
            st.line_chart(rsi)
        elif option == 'SMA':
            st.write('Simple Moving Average')
            st.line_chart(sma)
        else:
            st.write('Exponential Moving Average')
            st.line_chart(ema)
    
    def fetch_stock_data(ticker, period="1d", interval="1m"):
        return yf.Ticker(ticker).history(period=period, interval=interval)
    
    def update_data_and_plot():
        st.title("Real-Time Stock Data")
        ticker=option
        time_range = st.selectbox("Select the time range:", ["1d"])
    
        # Time range mapping
        time_range_map = {
            "1d": ("1d", "5m"),
        }
    
        if ticker and time_range:
            period, interval = time_range_map.get(time_range, ("1d", "5m"))
            data = fetch_stock_data(ticker, period, interval)
    
            # Initialize session state
            if "historical_data" not in st.session_state:
                st.session_state.historical_data = pd.DataFrame()
            if "last_data_point" not in st.session_state:
                st.session_state.last_data_point = None
            if "same_data_time" not in st.session_state:
                st.session_state.same_data_time = None
            if "last_update_time" not in st.session_state:
                st.session_state.last_update_time = datetime.now()
            if "auto_update" not in st.session_state:
                st.session_state.auto_update = False
            if "update_stopped" not in st.session_state:
                st.session_state.update_stopped = False
    
            chart_placeholder = st.empty()
            table_placeholder = st.empty()
    
            def update_data_and_plot():
                new_data = fetch_stock_data(ticker, period, interval)
                if not new_data.empty:
                    current_data_point = new_data.iloc[-1]['Close']
                    if st.session_state.last_data_point == current_data_point:
                        if st.session_state.same_data_time is None:
                            st.session_state.same_data_time = datetime.now()
                        elif datetime.now() - st.session_state.same_data_time > timedelta(minutes=5):
                            st.write("Data unchanged for 5 minutes. Stopping updates.")
                            st.session_state.auto_update = False
                            st.session_state.update_stopped = True
                            return
                    else:
                        st.session_state.same_data_time = None
    
                    st.session_state.last_data_point = current_data_point
                    st.session_state.historical_data = pd.concat([st.session_state.historical_data, new_data]).drop_duplicates()
    
                    fig = go.Figure(data=[go.Candlestick(
                        x=st.session_state.historical_data.index,
                        open=st.session_state.historical_data['Open'],
                        high=st.session_state.historical_data['High'],
                        low=st.session_state.historical_data['Low'],
                        close=st.session_state.historical_data['Close'],
                        increasing_line_color='green',
                        decreasing_line_color='red'
                    )])
                    fig.update_layout(title=f"{ticker} - Real-Time Data", xaxis_title="Time", yaxis_title="Price")
                    chart_placeholder.plotly_chart(fig, use_container_width=True)
                    st.session_state.last_update_time = datetime.now()
                    st.session_state.update_stopped = False
                    table_placeholder.dataframe(st.session_state.historical_data)
    
            if st.button("Live data"):
                st.session_state.auto_update = True
                st.session_state.update_stopped = False
    
            if st.button("Stop"):
                st.session_state.auto_update = False
                st.session_state.update_stopped = True
    
            if st.session_state.auto_update:
                 update_data_and_plot()
                 time.sleep(15)
                 if st.session_state.auto_update:  # Ensure re-run only when auto-update is True
                    st.rerun()
    
    
            if st.session_state.update_stopped:
                st.write("Updates have stopped. Showing the last updated data.")
                fig = go.Figure(data=[go.Candlestick(
                    x=st.session_state.historical_data.index,
                    open=st.session_state.historical_data['Open'],
                    high=st.session_state.historical_data['High'],
                    low=st.session_state.historical_data['Low'],
                    close=st.session_state.historical_data['Close'],
                    increasing_line_color='green',
                    decreasing_line_color='red'
                )])
              
                fig.update_layout(title=f"{ticker} - Last Updated Data", xaxis_title="Time", yaxis_title="Price")
                chart_placeholder.plotly_chart(fig, use_container_width=True)
                table_placeholder.dataframe(st.session_state.historical_data)
                high=st.session_state.historical_data['High'],
                low=st.session_state.historical_data['Low'],
                # Assuming 'historical_data' is a DataFrame stored in session state
                close = st.session_state.historical_data['Close']
                
                # Get the latest value
                latest_value = close.iloc[-1]
                
                # Create a slider that ranges from the minimum to maximum value of 'Close'
                # You can set the default value to the latest value
                min_value = close.min()
                max_value = close.max()
                
                st.slider(
                    label="Price",
                    min_value=float(min_value),
                    max_value=float(max_value),
                    value=float(latest_value)
                )
    
    def predict():
        num = st.number_input('How many days forecast?', value=5)
        num = int(num)
        if st.button('Predict'):
            model_engine(num)
    
    def model_engine(num):
        # getting only the closing price
        df = data[['Close']]
        # shifting the closing price based on number of days forecast
        df['preds'] = data.Close.shift(-num)
        # scaling the data
        x = df.drop(['preds'], axis=1).values
        x = scaler.fit_transform(x)
        # storing the last num_days data
        x_forecast = x[-num:]
        # selecting the required values for training
        x = x[:-num]
        # getting the preds column
        y = df.preds.values
        # selecting the required values for training
        y = y[:-num]
    
        # splitting the data
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=.2, random_state=7)
        # training the model
        model = LinearRegression()
        model.fit(x_train, y_train)
        preds = model.predict(x_test)
        col1, col2 = st.columns(2)
        with col1:
            st.info(f'Accuracy score: {r2_score(y_test, preds) * 100:.2f}%')
        with col2:
            st.info(f'MAE: {mean_absolute_error(y_test, preds):.2f}')
        # predicting stock price based on the number of days
        forecast_pred = model.predict(x_forecast)
        forecast_dates = pd.date_range(start=data.index[-1], periods=num + 1).tolist()[1:]
        forecast_df = pd.DataFrame(forecast_pred, index=forecast_dates, columns=['Forecast'])
    
        # Combine historical data with forecast data
        combined_df = pd.concat([data[['Close']], forecast_df])
    
        st.line_chart(combined_df)
    
    if __name__ == '__main__':
        main()


# Load environment variables
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# File for storing user data
USER_DATA_FILE = 'users.json'
RESET_TOKENS_FILE = 'reset_tokens.json'

# Utility Functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_user_data(data):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(data, f)

def load_reset_tokens():
    if os.path.exists(RESET_TOKENS_FILE):
        with open(RESET_TOKENS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_reset_tokens(data):
    with open(RESET_TOKENS_FILE, 'w') as f:
        json.dump(data, f)

def send_reset_email(user_email, token):
    sender_email = "himanshupra67@gmail.com"
    sender_password = 'qcfa vuzq oqpd tdzf'
    receiver_email = user_email


    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = 'Password Reset Request'

    reset_link = f"http://localhost:8501/?token={token}&email={user_email}"
    body = f"Hi,\n\nClick the link below to reset your password:\n{reset_link}"
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False
def validate_email(email):
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_pattern, email)

def validate_password(password):
    # Password validation: at least 8 characters, one digit, one uppercase letter, and one special character
    password_pattern = r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    return re.match(password_pattern, password)
# Signup Page
def signup():
    st.title("Sign Up")
    username = st.text_input("Username", key="signup_username")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
    if username and email:
        if st.button("Sign Up", key="signup_button"):
            user_data = load_user_data()
            if not validate_email(email):
                st.error("Invalid email address.")
            elif not validate_password(password):
                st.error("Password must be at least 8 characters long, include one digit, one uppercase letter, and one special character.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            elif email in user_data:
                st.error("Email already registered.")
            else:
                hashed_password = hash_password(password)
                user_data[email] = {"username": username, "password": hashed_password}
                save_user_data(user_data)
                st.session_state['redirect_to_signin'] = True
                st.success("Sign up successful! You can now log in.")

        else :
            st.error("Please enter the required fields")

# Sign In Page
def signin():
    st.title("Sign In")
    email = st.text_input("Email", key="signin_email")
    password = st.text_input("Password", type="password", key="signin_password")
    if email:
        if st.button("Sign In", key="signin_button"):
            user_data = load_user_data()
            hashed_password = hash_password(password)
            if email in user_data and user_data[email]["password"] == hashed_password:
                st.success(f"Welcome back, {user_data[email]['username']}!")
                st.session_state["logged_in"] = True
                st.session_state["username"] = user_data[email]['username']
            else:
                st.error("Invalid email or password.")

    
 
# Reset Password Page
def reset_password():
    st.subheader("Forgot Password?")
    reset_email = st.text_input("Enter your email to reset your password", key="reset_email")
    if reset_email:
        if st.button("Send Reset Link", key="send_reset_link"):
            if reset_email:
                user_data = load_user_data()
                if reset_email in user_data:
                    token = str(uuid.uuid4())
                    reset_tokens = load_reset_tokens()
                    reset_tokens[token] = reset_email
                    save_reset_tokens(reset_tokens)
                    if send_reset_email(reset_email, token):
                        st.success("A password reset link has been sent to your email.")
                else:
                    st.error("Email not registered.")
            else:
                st.error("Please enter an email address.")

    # Check for token and email in the query parameters
    
    token = st.query_params.get('token', [None])
    email = st.query_params.get('email', [None])
    
    if isinstance(token, list):
        token = tuple(token)
    
    if token and email and token in load_reset_tokens() and load_reset_tokens()[token] == email:
        st.success("Please change the password and confirm!")
        st.title("Reset Password")
        new_password = st.text_input("New Password", type="password", key="new_password")
        confirm_new_password = st.text_input("Confirm New Password", type="password", key="confirm_new_password")

        if st.button("Reset Password", key="reset_password_button"):
            if new_password != confirm_new_password:
                st.error("Passwords do not match.")
            else:
                user_data = load_user_data()
                hashed_password = hash_password(new_password)

                if email in user_data:
                    user_data[email]["password"] = hashed_password
                    save_user_data(user_data)
                    st.success("Password has been reset. You can now log in.")
                    reset_tokens = load_reset_tokens()
                    del reset_tokens[token]
                    save_reset_tokens(reset_tokens)
    else:
        st.warning("Please enter the Email or check the email for the reset link .")

# Logout Function
def logout():
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["email"] = ""
    # st.rerun()

# Main Function with Navigation


if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if 'redirect_to_signin' in st.session_state and st.session_state['redirect_to_signin']:
    st.session_state['redirect_to_signin'] = False
    st.experimental_rerun()
if st.session_state["logged_in"]:
    st.sidebar.markdown(
    f"Welcome<h3 style='color:green;'>{st.session_state['username'].upper()}!</h3><p>You have successfully logged into StockAi</p>",
    unsafe_allow_html=True)


    st.sidebar.button("Logout",on_click=logout)
    choice = st_navbar(["Home", "Dashboard", "Analysis","About","Profile"])
    if choice == "Home":
        import dashboard
        dashboard.display()
        # Load dashboard page
    elif choice == "Dashboard":
        import Homepage
        Homepage.display()
        # Load account settings page
    elif choice=="About":
        import Aboutpage
        Aboutpage.display()
    elif choice == "Analysis":
        analysis()
    elif choice=="Profile":
        import loginpage
        loginpage.display()
    
else:
    tabs = st.tabs(["Sign In", "Sign Up", "Reset Password"])
    # Display the content based on the selected tab
    with tabs[0]:
        signin()
    with tabs[1]:
        signup()
    with tabs[2]:
        reset_password()

