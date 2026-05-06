import streamlit as st
from datetime import date
from utils import api_post, api_get, api_delete, require_login, handle_response_error
from styles import GLOBAL_CSS, page_header_html, navbar_html, animated_bg_html

st.set_page_config(page_title="Health Records — HealthAI", page_icon="📋", layout="wide")
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
st.markdown(navbar_html(active="Records", initials=initials, is_light=is_light), unsafe_allow_html=True)

col_back, col_space = st.columns([2, 10])
with col_back:
    if st.button("← Back to Dashboard", key="back_hr"):
        st.switch_page("pages/1_🏠_Dashboard.py")

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(page_header_html("Health Records", "View and manage your medical records", "📋", "#22c55e"), unsafe_allow_html=True)

# ── Add New Record ────────────────────────────────────────────────────────────
with st.expander("➕  Add New Health Record", expanded=False):
    with st.form("add_record_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Title *", placeholder="Annual Blood Test")
            record_type = st.selectbox(
                "Record Type *",
                ["blood_test", "xray", "mri", "prescription", "vaccination", "surgery", "checkup", "other"]
            )
            record_date = st.date_input("Record Date *", value=date.today())
        with col2:
            doctor_name   = st.text_input("Doctor Name", placeholder="Dr. Smith")
            hospital_name = st.text_input("Hospital / Clinic", placeholder="City Hospital")

        description = st.text_area("Description / Notes", placeholder="Enter details about the record…")
        submitted   = st.form_submit_button("Add Record", type="primary", use_container_width=True)

    if submitted:
        if not title:
            st.error("Title is required.")
        else:
            payload = {
                "title":         title,
                "record_type":   record_type,
                "record_date":   str(record_date),
                "description":   description or None,
                "doctor_name":   doctor_name or None,
                "hospital_name": hospital_name or None,
            }
            response = api_post("/health-records/", payload)
            if response and response.status_code == 200:
                st.success("✅ Record added!")
                st.rerun()
            else:
                handle_response_error(response)

# ── Display Records ───────────────────────────────────────────────────────────
st.markdown("""
<div style="font-size:0.72rem;font-weight:700;color:var(--muted);text-transform:uppercase;
            letter-spacing:0.1em;margin:1rem 0 0.8rem;display:flex;align-items:center;gap:0.5rem;">
    📄 Your Records
    <span style="flex:1;height:1px;background:var(--border);display:inline-block;"></span>
</div>
""", unsafe_allow_html=True)

response = api_get("/health-records/")
if response and response.status_code == 200:
    records = response.json()
    if records:
        for record in records:
            type_icons = {
                "blood_test": "🩸", "xray": "🦴", "mri": "🧠",
                "prescription": "💊", "vaccination": "💉",
                "surgery": "🏥", "checkup": "🩺", "other": "📄"
            }
            icon = type_icons.get(record["record_type"], "📄")
            with st.expander(f"{icon}  {record['title']} — {record['record_date']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Type:** {record['record_type'].replace('_', ' ').title()}")
                    if record.get("doctor_name"):
                        st.markdown(f"**Doctor:** {record['doctor_name']}")
                with col2:
                    if record.get("hospital_name"):
                        st.markdown(f"**Hospital:** {record['hospital_name']}")
                    st.markdown(f"**Date:** {record['record_date']}")
                if record.get("description"):
                    st.markdown("---")
                    st.markdown(record["description"])
                if st.button("🗑️ Delete", key=f"del_rec_{record['id']}"):
                    del_response = api_delete(f"/health-records/{record['id']}")
                    if del_response and del_response.status_code == 200:
                        st.rerun()
    else:
        st.info("No health records yet. Add your first record above!")
else:
    handle_response_error(response)