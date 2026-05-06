import streamlit as st
from utils import api_post, api_get, api_delete, require_login, handle_response_error
from styles import GLOBAL_CSS, navbar_html, animated_bg_html

st.set_page_config(page_title="MediScan — HealthAI", page_icon="💊", layout="wide")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
require_login()

is_light = st.session_state.get("theme_light", False)
if is_light:
    st.markdown("""<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
  background-color: #F9FAFB !important; color: #0f172a !important; }
.hn-wrap { background: rgba(255,255,255,0.95) !important; }
</style>""", unsafe_allow_html=True)

st.markdown(animated_bg_html(is_light), unsafe_allow_html=True)
user_name = st.session_state.get("user_name", "User")
initials  = (user_name[0] + (user_name.split()[1][0] if len(user_name.split()) > 1 else "")).upper()

# ── Navbar ────────────────────────────────────────────────────────────────────
st.markdown(navbar_html(active="Scans", initials=initials, is_light=is_light), unsafe_allow_html=True)

# ── Back + Actions row ────────────────────────────────────────────────────────
col_back, col_clear, col_space = st.columns([2, 2, 8])
with col_back:
    if st.button("← Back to Dashboard", key="back_ms"):
        st.switch_page("pages/1_🏠_Dashboard.py")
with col_clear:
    if st.button("🗑️ Clear History", key="clear_ms"):
        response = api_delete("/mediscan/history")
        if response and response.status_code == 200:
            st.rerun()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="mg-header">
    <div class="mg-logo" style="background:linear-gradient(135deg,#06b6d4,#0891b2);box-shadow:0 0 24px rgba(6,182,212,0.35);">💊</div>
    <div>
        <div class="mg-title">MediScan</div>
        <div class="mg-subtitle">Medicine Intelligence — Text &amp; Image Analysis &nbsp;·&nbsp; {user_name}</div>
    </div>
</div>
<div class="mg-divider"></div>
""", unsafe_allow_html=True)

st.info("⚕️ **Disclaimer:** MediScan provides general medicine information only. Always consult a qualified healthcare professional before taking any medication.")

# ── Search Card ───────────────────────────────────────────────────────────────
st.markdown('<div class="search-card">', unsafe_allow_html=True)

tab_text, tab_image = st.tabs(["🔤  Search by Name", "📷  Scan from Image"])

with tab_text:
    st.markdown('<div class="search-label">Medicine Name</div>', unsafe_allow_html=True)
    col_search, col_btn = st.columns([4, 1])
    with col_search:
        medicine_name = st.text_input(
            "Medicine name", placeholder="e.g., Paracetamol, Amoxicillin, Metformin...",
            label_visibility="collapsed", key="text_input"
        )
    with col_btn:
        search_clicked = st.button("🔍 Scan", use_container_width=True, type="primary", key="text_btn")

    if search_clicked and medicine_name:
        with st.spinner(f"Analyzing {medicine_name}…"):
            response = api_post("/mediscan/scan", {"medicine_name": medicine_name})
        if response and response.status_code == 200:
            data = response.json()
            st.markdown(f'<div class="result-card"><div class="result-title">✅ Results for {data["medicine_name"]}</div></div>', unsafe_allow_html=True)
            st.markdown(data["scan_result"])
        else:
            handle_response_error(response)
    elif search_clicked:
        st.warning("⚠️ Please enter a medicine name.")

with tab_image:
    st.markdown('<div class="search-label">Upload Medicine Image</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.82rem;color:var(--muted);margin-bottom:12px;">Upload a photo of a medicine strip, bottle, or prescription label — AI will extract and explain all medicine details.</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload image", type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed", key="image_uploader"
    )

    img_col1, img_col2 = st.columns([3, 2])
    if uploaded_file:
        with img_col2:
            st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

    with img_col1:
        image_clicked = st.button("📷 Analyze Image", use_container_width=True, type="primary", key="image_btn")

    if image_clicked and uploaded_file:
        with st.spinner("Scanning image for medicine details…"):
            files    = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            response = api_post("/mediscan/scan-image", files=files)
        if response and response.status_code == 200:
            data = response.json()
            st.markdown(f'<div class="result-card"><div class="result-title">✅ Scan Complete: {data.get("medicine_name", "Detected Medicine")}</div></div>', unsafe_allow_html=True)
            st.markdown(data["scan_result"])
        else:
            handle_response_error(response)
    elif image_clicked:
        st.warning("⚠️ Please upload an image first.")

st.markdown('</div>', unsafe_allow_html=True)

# ── Scan History ──────────────────────────────────────────────────────────────
st.markdown('<div class="mg-divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="font-size:0.72rem;font-weight:700;color:var(--muted);text-transform:uppercase;
            letter-spacing:0.1em;margin-bottom:0.9rem;display:flex;align-items:center;gap:0.5rem;">
    📜 Your Scan History
    <span style="flex:1;height:1px;background:var(--border);display:inline-block;"></span>
</div>
""", unsafe_allow_html=True)

response = api_get("/mediscan/history")
if response and response.status_code == 200:
    scans = response.json()
    if scans:
        for scan in scans:
            date_str  = scan["scanned_at"][:10] if scan.get("scanned_at") else "Unknown date"
            scan_type = scan.get("scan_type", "text")
            type_icon = "📷" if scan_type == "image" else "💊"
            with st.expander(f"{type_icon}  {scan['medicine_name']}  ·  {date_str}"):
                st.markdown(scan["scan_result"])
    else:
        st.info("🔍 No scans yet. Search for a medicine or upload an image above!")
else:
    handle_response_error(response)