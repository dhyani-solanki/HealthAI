import streamlit as st
from utils import api_post, BASE_URL
from styles import GLOBAL_CSS

st.set_page_config(
    page_title="HealthAI",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# Extra auth-page centering
st.markdown("""
<style>
[data-testid="stSidebar"] { display: none !important; }
.block-container { max-width: 480px !important; padding: 3rem 1.5rem 4rem !important; }
/* Form inputs inside auth card */
.stForm { background: transparent !important; border: none !important; padding: 0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Initialise session state ──────────────────────────────────────────────────
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "theme_light" not in st.session_state:
    st.session_state.theme_light = False

# ── Already logged-in state ───────────────────────────────────────────────────
if st.session_state.access_token:
    st.markdown(f"""
    <div class="auth-card" style="max-width:400px;margin:0 auto;">
        <div class="auth-logo">
            <div class="auth-logo-icon">🏥</div>
            <h1>Welcome back!</h1>
            <p>Logged in as <strong>{st.session_state.user_name}</strong></p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏠 Go to Dashboard", use_container_width=True, type="primary"):
            st.switch_page("pages/1_🏠_Dashboard.py")
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.access_token = None
            st.session_state.user_name = None
            st.rerun()
    st.stop()

# ── Auth card header ──────────────────────────────────────────────────────────
st.markdown("""
<div class="auth-logo" style="text-align:center; margin-bottom:1.5rem;">
    <div class="auth-logo-icon" style="display:inline-flex;">🏥</div>
    <h1 style="font-size:1.6rem;font-weight:800;color:var(--text);letter-spacing:-0.02em;margin:0.75rem 0 0.2rem;">HealthAI</h1>
    <p style="color:var(--muted);font-size:0.88rem;margin:0;">Your personal AI health companion</p>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_login, tab_signup = st.tabs(["🔑  Login", "📝  Sign Up"])

# ── LOGIN FORM ────────────────────────────────────────────────────────────────
with tab_login:
    with st.form("login_form"):
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        login_email    = st.text_input("Email", placeholder="you@example.com")
        login_password = st.text_input("Password", type="password", placeholder="••••••••")
        login_btn      = st.form_submit_button("Login", type="primary", use_container_width=True)

    if login_btn:
        if not login_email or not login_password:
            st.error("Please fill in all fields.")
        else:
            with st.spinner("Logging in…"):
                response = api_post(
                    "/auth/login",
                    {"email": login_email, "password": login_password},
                    authenticated=False
                )
            if response is None:
                st.error("❌ Cannot connect to server. Is the backend running?")
            elif response.status_code == 200:
                data = response.json()
                st.session_state.access_token = data["access_token"]
                st.session_state.user_name    = data["user_name"]
                st.success(f"Welcome back, **{data['user_name']}**! 🎉")
                st.balloons()
                st.rerun()
            else:
                detail = response.json().get("detail", "Login failed")
                st.error(f"❌ {detail}")

# ── SIGNUP FORM ───────────────────────────────────────────────────────────────
with tab_signup:
    with st.form("signup_form"):
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        signup_name  = st.text_input("Full Name *", placeholder="John Doe")
        signup_email = st.text_input("Email *", placeholder="you@example.com")

        col1, col2 = st.columns(2)
        with col1:
            signup_password = st.text_input("Password *", type="password")
        with col2:
            signup_confirm  = st.text_input("Confirm Password *", type="password")

        st.markdown("**Optional Details**")
        col3, col4 = st.columns(2)
        with col3:
            signup_phone  = st.text_input("Phone", placeholder="+1234567890")
            signup_gender = st.selectbox("Gender", ["", "Male", "Female", "Other"])
        with col4:
            signup_dob   = st.date_input("Date of Birth", value=None)
            signup_blood = st.selectbox(
                "Blood Group",
                ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
            )

        signup_btn = st.form_submit_button("Create Account", type="primary", use_container_width=True)

    if signup_btn:
        if not signup_name or not signup_email or not signup_password:
            st.error("Please fill in all required fields.")
        elif signup_password != signup_confirm:
            st.error("Passwords don't match!")
        elif len(signup_password) < 6:
            st.error("Password must be at least 6 characters.")
        else:
            payload = {
                "full_name": signup_name,
                "email":     signup_email,
                "password":  signup_password,
            }
            if signup_phone:  payload["phone"]         = signup_phone
            if signup_gender: payload["gender"]        = signup_gender
            if signup_dob:    payload["date_of_birth"] = str(signup_dob)
            if signup_blood:  payload["blood_group"]   = signup_blood

            with st.spinner("Creating account…"):
                response = api_post("/auth/signup", payload, authenticated=False)

            if response is None:
                st.error("❌ Cannot connect to server.")
            elif response.status_code == 201:
                st.success("✅ Account created! Please login.")
            else:
                detail = response.json().get("detail", "Signup failed")
                st.error(f"❌ {detail}")