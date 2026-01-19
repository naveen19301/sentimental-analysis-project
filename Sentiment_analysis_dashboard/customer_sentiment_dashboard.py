import streamlit as st
import pandas as pd
import json
import os
import hashlib
from pathlib import Path
import sys
import streamlit.components.v1 as components

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Customer Sentiment Analytics Hub",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# HIDE DEFAULT STREAMLIT MULTIPAGE SIDEBAR
# =====================================================
st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] {display: none !important;}
    section[data-testid="stSidebarNav"] {display: none !important;}
    </style>
    """,
    unsafe_allow_html=True
)

# =====================================================
# PROJECT PATH FIX
# =====================================================
ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))

# =====================================================
# EXCEL DATA LOADER
# =====================================================
from utils.excel_loader import load_excel_data

# =====================================================
# AUTH CONFIG
# =====================================================
USERS_FILE = ROOT_DIR / "users.json"

def sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

def ensure_user_db():
    if not os.path.exists(USERS_FILE):
        users = {
            "admin": {"pwd": sha256("admin123"), "role": "admin"},
            "viewer": {"pwd": sha256("viewer123"), "role": "viewer"}
        }
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)

def load_users():
    ensure_user_db()
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def authenticate(username: str, password: str):
    users = load_users()
    if username in users and users[username]["pwd"] == sha256(password):
        return True, users[username]["role"]
    return False, None

# =====================================================
# LOGIN SIDEBAR
# =====================================================
def login_sidebar():
    st.sidebar.markdown("## 🔐 Authentication")

    if "logged" not in st.session_state:
        st.session_state.logged = False
        st.session_state.user = None
        st.session_state.role = None

    if st.session_state.logged:
        st.sidebar.success(f"✅ {st.session_state.user}")
        st.sidebar.caption(f"Role: {st.session_state.role}")

        if st.sidebar.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        return True

    with st.sidebar.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", use_container_width=True)

        if submit:
            ok, role = authenticate(username, password)
            if ok:
                st.session_state.logged = True
                st.session_state.user = username
                st.session_state.role = role
                st.rerun()
            else:
                st.sidebar.error("❌ Invalid credentials")

    st.sidebar.info("**Demo Credentials:**\n\n- **Username:** admin\n- **Password:** admin123")
    return False

# =====================================================
# DATA LOADING
# =====================================================
def load_data_once():
    if "df" not in st.session_state:
        try:
            st.session_state.df = load_excel_data()
        except Exception as e:
            st.error(f"❌ Error loading Excel file: {e}")
            st.session_state.df = pd.DataFrame()
    return st.session_state.df

# =====================================================
# CUSTOM CSS FOR HIGHLIGHTED BUTTONS
# =====================================================
def apply_navigation_styles():
    st.markdown(
        """
        <style>
        /* Style for active/selected navigation button */
        div[data-testid="stSidebar"] button[kind="secondary"] {
            background-color: transparent;
            border: 1px solid rgba(250, 250, 250, 0.2);
            transition: all 0.3s ease;
        }
        
        div[data-testid="stSidebar"] button[kind="secondary"]:hover {
            background-color: rgba(151, 166, 195, 0.15);
            border-color: rgba(250, 250, 250, 0.4);
        }
        
        /* Active button style using session state */
        .nav-button-active {
            background: linear-gradient(90deg, rgba(255, 75, 75, 0.3) 0%, rgba(255, 110, 110, 0.2) 100%) !important;
            border-left: 4px solid #ff4b4b !important;
            font-weight: 600 !important;
            box-shadow: 0 2px 8px rgba(255, 75, 75, 0.3) !important;
        }
        
        /* Smooth page transitions */
        .main .block-container {
            animation: fadeIn 0.4s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# =====================================================
# MAIN APP
# =====================================================
def main():
    
    # Apply custom styles
    apply_navigation_styles()

    # ---------------- LOGIN CHECK ----------------
    if not login_sidebar():
        st.markdown(
            """
            <div style='text-align:center;padding:120px'>
                <h1>📊 Customer Sentiment Analytics</h1>
                <p>Please login to access the dashboard</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    # ---------------- LOAD DATA ----------------
    df = load_data_once()

    if df.empty:
        st.error("No data available.")
        return

    # ---------------- NAVIGATION ----------------
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📑 Navigation")

    pages = {
        "📌 Summary": "Summary",
        "💬 Sentiment Analysis": "Sentiment",
        "📊 Emotions & Word Clouds": "Emotions",
        "⏱️ Performance Metrics": "Performance",
        "👥 Ticket Owner Stats": "Owners",
        "🚨 Risk Analysis": "Risk",
        "🧩 Issue Categories": "Category",
        "📄 Ticket Explorer": "Explorer"
    }

    if "page" not in st.session_state:
        st.session_state.page = "Summary"

    # Create buttons with highlighted active state
    for label, pid in pages.items():
        # Determine button type based on active page
        button_type = "primary" if st.session_state.page == pid else "secondary"
        
        # Add custom class for active button styling
        button_key = f"nav_{pid}"
        
        if st.sidebar.button(
            label, 
            use_container_width=True, 
            type=button_type,
            key=button_key
        ):
            st.session_state.page = pid
            st.rerun()

    # # Add visual indicator for current page
    # st.sidebar.markdown("---")
    # st.sidebar.info(f"📍 **Current Page:** {[k for k, v in pages.items() if v == st.session_state.page][0]}")

    # ---------------- ROUTING WITH ROBUST SCROLL ----------------
    # Hidden anchor at the top of the main area
    st.markdown('<div id="top-anchor"></div>', unsafe_allow_html=True)
    
    st.components.v1.html(
        f"""
        <script>
            function forceScroll() {{
                const main = window.parent.document.querySelector('section.main');
                if (main) {{
                    main.scrollTo({{top: 0, behavior: 'auto'}});
                }}
                const anchor = window.parent.document.getElementById('top-anchor');
                if (anchor) {{
                    anchor.scrollIntoView();
                }}
            }}
            forceScroll();
            // Repeat on a slight delay to ensure content is fully loaded
            setTimeout(forceScroll, 50);
            setTimeout(forceScroll, 150);
        </script>
        <!-- State: {st.session_state.page} -->
        """,
        height=0
    )
    
    if st.session_state.page == "Summary":
        from pages import summary
        summary.show(df)

    elif st.session_state.page == "Sentiment":
        from pages import sentiment_analysis
        sentiment_analysis.show(df)

    elif st.session_state.page == "Emotions":
        from pages import emotions_wordcloud
        emotions_wordcloud.show(df)

    elif st.session_state.page == "Performance":
        from pages import performance
        performance.show(df)

    elif st.session_state.page == "Owners":
        from pages import ticket_owners
        ticket_owners.show(df)

    elif st.session_state.page == "Risk":
        from pages import risk_analysis
        risk_analysis.show(df)

    elif st.session_state.page == "Category":
        from pages import ticket_category_analysis
        ticket_category_analysis.show(df)

    elif st.session_state.page == "Explorer":
        from pages import ticket_explorer
        ticket_explorer.show(df)

# =====================================================
if __name__ == "__main__":
    main()