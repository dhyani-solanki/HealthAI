import streamlit as st
from utils import api_post, api_get, api_delete, require_login, handle_response_error
from styles import GLOBAL_CSS, navbar_html, animated_bg_html

st.set_page_config(page_title="MediGenius — HealthAI", page_icon="💬", layout="wide")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
require_login()

is_light = st.session_state.get("theme_light", False)
if is_light:
    st.markdown("""<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
  background-color: #F9FAFB !important; color: #0f172a !important; }
.stat-card, .feature-card, .activity-card, .db-header, .page-header, .mg-logo { background: #FFFFFF !important; }
.hn-wrap { background: rgba(255,255,255,0.95) !important; }
</style>""", unsafe_allow_html=True)

st.markdown(animated_bg_html(is_light), unsafe_allow_html=True)
user_name = st.session_state.get("user_name", "User")
initials  = (user_name[0] + (user_name.split()[1][0] if len(user_name.split()) > 1 else "")).upper()

# ── Navbar ────────────────────────────────────────────────────────────────────
st.markdown(navbar_html(active="Chats", initials=initials, is_light=is_light), unsafe_allow_html=True)

# ── Back + Actions row ────────────────────────────────────────────────────────
col_back, col_clear, col_space = st.columns([2, 2, 8])
with col_back:
    if st.button("← Back to Dashboard", key="back_mg"):
        st.switch_page("pages/1_🏠_Dashboard.py")
with col_clear:
    if st.button("🗑️ Clear History", key="clear_mg"):
        response = api_delete("/medigenius/history")
        if response and response.status_code == 200:
            st.session_state.mg_messages = []
            st.rerun()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="mg-header">
    <div class="mg-logo">💬</div>
    <div>
        <div class="mg-title">MediGenius</div>
        <div class="mg-subtitle">AI-Powered Health Intelligence &nbsp;·&nbsp; Logged in as <strong>{user_name}</strong></div>
    </div>
</div>
<div class="mg-divider"></div>
""", unsafe_allow_html=True)

# ── Load chat history ─────────────────────────────────────────────────────────
if "mg_messages" not in st.session_state:
    response = api_get("/medigenius/history")
    if response and response.status_code == 200:
        st.session_state.mg_messages = [
            {"role": msg["role"], "content": msg["content"], "source": msg.get("source")}
            for msg in response.json()
        ]
    else:
        st.session_state.mg_messages = []

# ── Empty state ───────────────────────────────────────────────────────────────
if not st.session_state.mg_messages:
    st.markdown("""
<div style="text-align:center; padding:3rem 1rem; color:var(--muted);">
    <div style="font-size:3.5rem; margin-bottom:12px; filter:drop-shadow(0 0 20px rgba(59,130,246,0.3));">🩺</div>
    <div style="font-size:1.25rem; font-weight:600; color:var(--text2); margin-bottom:8px;">How can I help you today?</div>
    <div style="font-size:0.85rem; color:var(--muted); max-width:320px; margin:0 auto; line-height:1.65;">
        Ask me about symptoms, medications, conditions, or general health information.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Disclaimer ────────────────────────────────────────────────────────────────
st.info("⚕️ **Disclaimer:** MediGenius provides general health information only. Always consult a qualified healthcare professional for medical advice.")

# ── Display messages ──────────────────────────────────────────────────────────
source_badges = {
    "RAG": "🟢 Medical Database",
    "LLM": "🔵 AI Model",
    "Wikipedia": "🟡 Wikipedia",
    "Tavily": "🟠 Web Search",
    "error": "🔴 Error",
}

for msg in st.session_state.mg_messages:
    avatar = "🧑" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("source"):
            badge = source_badges.get(msg["source"], f"⚪ {msg['source']}")
            st.caption(f"Source: {badge}")

# ── Chat input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask me any medical question…"):
    st.session_state.mg_messages.append({"role": "user", "content": prompt, "source": None})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Analyzing your question…"):
            response = api_post("/medigenius/chat", {"message": prompt})

        if response and response.status_code == 200:
            data   = response.json()
            reply  = data["reply"]
            source = data.get("source", "Unknown")
            st.markdown(reply)
            badge = source_badges.get(source, f"⚪ {source}")
            st.caption(f"Source: {badge}")
            st.session_state.mg_messages.append({"role": "assistant", "content": reply, "source": source})
        else:
            handle_response_error(response)