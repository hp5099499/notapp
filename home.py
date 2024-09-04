import streamlit as st
from PIL import Image
import base64

# Set page configuration (MUST BE THE FIRST Streamlit command)
st.set_page_config(
    page_title="Stock.Ai",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

def get_base64_image(img_path):
    try:
        with open(img_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        return None

# Load and encode logo image
logo_path = 'logo.jpg'  # Path to your logo image
logo_base64 = get_base64_image(logo_path)

# Load and encode description image
description_image_path = 'logo.jpg'  # Path to your description image
description_image_base64 = get_base64_image(description_image_path)

# Inline CSS for styling inspired by modern design trends
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');

        body {
            font-family: 'Roboto', sans-serif;
            background-color: #F7F9FC;
            color: #2E3B4E;
            margin: 0;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 40px;
            background-color: #1E2235;
            color: white;
            border-bottom: 2px solid #3366FF;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.15);
        }

        header h1 {
            margin: 0;
            font-size: 28px;
            font-weight: 700;
            color: #FFFFFF;
            display: flex;
            align-items: center;
        }

        header h1 img {
            border-radius: 50%;
            margin-right: 15px;
            width: 50px;
            height: 50px;
        }

        .nav-container {
            display: flex;
            align-items: center;
            gap: 20px;
        }

        .search-bar {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .search-bar input {
            padding: 10px;
            border-radius: 30px;
            border: 1px solid #B0BEC5;
            font-size: 15px;
            width: 200px;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
        }

        .search-bar input:focus {
            border-color: #3366FF;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.15);
        }

        .search-bar button {
            padding: 8px 15px;
            background-color: #3366FF;
            color: white;
            border: none;
            border-radius: 30px;
            font-size: 15px;
            cursor: pointer;
            transition: background-color 0.3s ease, transform 0.2s ease;
        }

        .search-bar button:hover {
            background-color: #274BDB;
            transform: translateY(-2px);
            box-shadow: 0px 5px 10px rgba(0, 0, 0, 0.2);
        }

        .nav-buttons button {
            padding: 10px 20px;
            background-color: #3366FF;
            color: white;
            border: none;
            border-radius: 30px;
            font-size: 15px;
            cursor: pointer;
            transition: background-color 0.3s ease, transform 0.2s ease;
        }

        .nav-buttons button:hover {
            background-color: #274BDB;
            transform: translateY(-2px);
            box-shadow: 0px 5px 10px rgba(0, 0, 0, 0.2);
        }

        .typing {
            font-size: 26px;
            font-weight: 700;
            color: #3366FF;
            text-align: center;
            margin: 40px 0;
            white-space: nowrap;
            overflow: hidden;
            border-right: 4px solid #3366FF;
            width: 0;
            animation: typing 6s steps(30, end), blink-caret 0.75s step-end infinite;
        }

        @keyframes typing {
            from { width: 0; }
            to { width: 100%; }
        }

        @keyframes blink-caret {
            from, to { border-color: transparent; }
            50% { border-color: #3366FF; }
        }

        footer {
            margin-top: 60px;
            padding: 40px 20px;
            background-color: #2C3E50;
            color: white;
            text-align: center;
            font-size: 15px;
            box-shadow: 0px -4px 10px rgba(0, 0, 0, 0.15);
        }

        footer .footer-content {
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            gap: 20px;
            padding: 20px;
        }

        footer .footer-section {
            flex: 1;
            min-width: 200px;
        }

        footer .footer-section h4 {
            margin-bottom: 15px;
            font-size: 18px;
            font-weight: 700;
            color: #3366FF;
        }

        footer .footer-section a {
            color: #B0BEC5;
            text-decoration: none;
            display: block;
            margin-bottom: 10px;
            transition: color 0.3s ease;
        }

        footer .footer-section a:hover {
            color: #3366FF;
        }

        footer .social-icons a {
            margin: 0 10px;
            font-size: 20px;
            color: #B0BEC5;
            transition: color 0.3s ease;
        }

        footer .social-icons a:hover {
            color: #3366FF;
        }

        footer p {
            margin-top: 30px;
            font-size: 14px;
            color: #B0BEC5;
        }

        @media (max-width: 768px) {
            header {
                flex-direction: column;
                align-items: flex-start;
                padding: 15px 20px;
            }

            .nav-container {
                flex-direction: column;
                gap: 15px;
            }

            .nav-buttons {
                flex-direction: column;
                gap: 10px;
            }

            .search-bar input {
                width: 100%;
            }

            footer .footer-content {
                flex-direction: column;
                align-items: center;
            }

            footer .footer-section {
                text-align: center;
            }

            footer .social-icons {
                margin-top: 20px;
            }
        }
    </style>
""", unsafe_allow_html=True)

# Header with logo, search bar, and updated navigation
if logo_base64:
    st.markdown(f"""
        <header>
            <h1>
                <img src="data:image/jpeg;base64,{logo_base64}" alt="Logo"/>
                Stock.Ai
            </h1>
            <div class="nav-container">
                <div class="search-bar">
                    <input type="text" placeholder="Search for stocks..." id="search_input" aria-label="Stock search"/>
                    <button class="search-button">🔍 Search</button>
                </div>
                <div class="nav-buttons">
                    <button onclick="window.location.href='#'">Login</button>
                    <button onclick="window.location.href='#'">Sign Up</button>
                    <button onclick="window.location.href='#'">About Us</button>
                    <button onclick="window.location.href='#'">Contact Us</button>
                </div>
            </div>
        </header>
    """, unsafe_allow_html=True)

# Typing effect text
st.markdown("""
    <div class="typing">Welcome to the Stock Prediction App</div>
""", unsafe_allow_html=True)

# Description section with an image
st.markdown(f"""
    <div style="text-align: center; margin-top: 40px;">
        <img src="data:image/jpeg;base64,{description_image_base64}" alt="Description Image" style="max-width: 100%; height: auto; border-radius: 10px; margin-bottom: 20px;"/>
        <h2>About Stock.Ai</h2>
        <p>
            Stock.Ai is a powerful web-based application designed to help you make informed investment decisions.
            By leveraging advanced machine learning algorithms and real-time market data, our platform offers 
            accurate stock price predictions, market analysis, and investment insights. Whether you're a seasoned 
            investor or just getting started, Stock.Ai provides the tools and resources to help you navigate the 
            complexities of the stock market with confidence.<br>
            Join thousands of users who trust Stock.Ai for their investment decisions. With our user-friendly interface 
            and cutting-edge technology, you can easily search for stocks, view predictions, and analyze market trends 
            to optimize your portfolio.
        </p>
    </div>
""", unsafe_allow_html=True)

# Footer section
st.markdown("""
    <footer>
        <div class="footer-content">
            <div class="footer-section">
                <h4>About Us</h4>
                <a href="#">Our Story</a>
                <a href="#">Team</a>
                <a href="#">Careers</a>
            </div>
            <div class="footer-section">
                <h4>Support</h4>
                <a href="#">Help Center</a>
                <a href="#">Contact Us</a>
                <a href="#">FAQs</a>
            </div>
            <div class="footer-section">
                <h4>Legal</h4>
                <a href="#">Terms of Service</a>
                <a href="#">Privacy Policy</a>
                <a href="#">Cookie Policy</a>
            </div>
            <div class="footer-section social-icons">
                <h4>Follow Us</h4>
                <a href="#">🔵 Facebook</a>
                <a href="#">🔷 Twitter</a>
                <a href="#">📷 Instagram</a>
                <a href="#">🔗 LinkedIn</a>
            </div>
        </div>
        <p>© 2024 Stock.Ai. All rights reserved.</p>
    </footer>
""", unsafe_allow_html=True)
