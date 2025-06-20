import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

# Set page config
st.set_page_config(
    page_title="Login - AI LECTURER SUPPORT SYSTEM",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Authentication function
def check_credentials(username, password):
    try:
        default_username = os.getenv('DEFAULT_USERNAME')
        default_password = os.getenv('DEFAULT_PASSWORD')
        
        if not default_username or not default_password:
            st.error("❌ Authentication credentials not properly configured. Please check .env file.")
            return False
            
        return username == default_username and password == default_password
    except Exception as e:
        st.error(f"❌ Authentication error: {str(e)}")
        return False

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'login_attempts' not in st.session_state:
    st.session_state.login_attempts = 0

# Redirect if already authenticated
if st.session_state.authenticated:
    st.switch_page("app.py")

# Login page styling
st.markdown("""
<style>
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        background-color: #f8f9fa;
    }
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
        color: #2c3e50;
    }
    .stButton > button {
        width: 100%;
        background-color: #3498db;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #2980b9;
    }
</style>
""", unsafe_allow_html=True)

# Main login interface
st.markdown("<div class='login-container'>", unsafe_allow_html=True)

# Header
st.markdown("""
<div class='login-header'>
    <h1>🎓 AI LECTURER SUPPORT SYSTEM</h1>
    <p>Please login to access the system</p>
</div>
""", unsafe_allow_html=True)

# Login form
with st.form("login_form", clear_on_submit=True):
    st.markdown("### 🔐 Login Credentials")
    
    username = st.text_input(
        "👤 Username",
        placeholder="Enter your username",
        help="Enter the username provided by your administrator"
    )
    
    password = st.text_input(
        "🔒 Password", 
        type="password",
        placeholder="Enter your password",
        help="Enter the password provided by your administrator"
    )
    
    # Login button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        login_button = st.form_submit_button("🚀 Login", use_container_width=True)
    
    # Handle login
    if login_button:
        if not username or not password:
            st.error("⚠️ Please enter both username and password")
        else:
            if check_credentials(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.login_attempts = 0
                st.success("✅ Login successful! Redirecting...")
                st.balloons()
                st.rerun()
            else:
                st.session_state.login_attempts += 1
                if st.session_state.login_attempts >= 3:
                    st.error("🚫 Too many failed login attempts. Please contact your administrator.")
                    st.stop()
                else:
                    remaining_attempts = 3 - st.session_state.login_attempts
                    st.error(f"❌ Invalid username or password. {remaining_attempts} attempts remaining.")

st.markdown("</div>", unsafe_allow_html=True)

# Information section
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 📋 Features
    - 📤 Upload Excel/CSV files
    - 🤖 AI-powered question answering
    - 💬 Chat history management
    - 🔍 Advanced data search
    """)

with col2:
    st.markdown("""
    ### 🛡️ Security
    - 🔐 Secure authentication
    - 👤 User session management
    - 💾 Persistent chat history
    - 🔒 Data privacy protection
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d;'>
    <p>🎓 AI Lecturer Support System v2.0</p>
    <p>For support, contact your system administrator</p>
</div>
""", unsafe_allow_html=True)