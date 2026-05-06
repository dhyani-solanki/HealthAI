import streamlit as st
from utils import api_post, api_get, api_delete, require_login, handle_response_error
from styles import GLOBAL_CSS, page_header_html, navbar_html, animated_bg_html

st.set_page_config(page_title="Family History — HealthAI", page_icon="👨‍👩‍👧", layout="wide")
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
st.markdown(navbar_html(active="Family", initials=initials, is_light=is_light), unsafe_allow_html=True)

col_back, col_space = st.columns([2, 10])
with col_back:
    if st.button("← Back to Dashboard", key="back_fh"):
        st.switch_page("pages/1_🏠_Dashboard.py")

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(page_header_html("Family History", "Track hereditary conditions and family health patterns", "👨‍👩‍👧", "#f97316"), unsafe_allow_html=True)

# ── Add Family Condition ──────────────────────────────────────────────────────
with st.expander("➕  Add Family Health Condition", expanded=False):
    with st.form("add_family_form"):
        col1, col2 = st.columns(2)
        with col1:
            relation  = st.selectbox("Relation *", ["Father", "Mother", "Sibling", "Grandparent", "Uncle/Aunt", "Other"])
            condition = st.text_input("Condition *", placeholder="e.g., Diabetes, Hypertension")
        with col2:
            age_onset = st.number_input("Age of Onset", min_value=0, max_value=120, value=0)
            severity  = st.selectbox("Severity", ["Mild", "Moderate", "Severe", "Unknown"])

        notes     = st.text_area("Notes", placeholder="Additional details…")
        submitted = st.form_submit_button("Add Condition", type="primary", use_container_width=True)

    if submitted:
        if not condition:
            st.error("Condition is required.")
        else:
            payload = {
                "relation":   relation,
                "condition":  condition,
                "age_onset":  age_onset if age_onset > 0 else None,
                "severity":   severity,
                "notes":      notes or None,
            }
            response = api_post("/health/family-history", payload)
            if response and response.status_code in (200, 201):
                st.success("✅ Condition added!")
                st.rerun()
            else:
                handle_response_error(response)

# ── Display Family History ────────────────────────────────────────────────────
st.markdown("""
<div style="font-size:0.72rem;font-weight:700;color:var(--muted);text-transform:uppercase;
            letter-spacing:0.1em;margin:1rem 0 0.8rem;display:flex;align-items:center;gap:0.5rem;">
    👨‍👩‍👧 Recorded Conditions
    <span style="flex:1;height:1px;background:var(--border);display:inline-block;"></span>
</div>
""", unsafe_allow_html=True)

response = api_get("/health/family-history")
if response and response.status_code == 200:
    entries = response.json()
    if entries:
        relation_icons = {
            "Father": "👨", "Mother": "👩", "Sibling": "🧑",
            "Grandparent": "👴", "Uncle/Aunt": "🧓", "Other": "👤"
        }
        severity_colors = {
            "Mild": "#22c55e", "Moderate": "#f97316",
            "Severe": "#ef4444", "Unknown": "#64748b"
        }
        for entry in entries:
            icon     = relation_icons.get(entry.get("relation", ""), "👤")
            sev      = entry.get("severity", "Unknown")
            sev_col  = severity_colors.get(sev, "#64748b")
            with st.expander(f"{icon} {entry.get('relation', 'Unknown')} — {entry.get('condition', 'N/A')}"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Condition:** {entry.get('condition', 'N/A')}")
                    st.markdown(f"**Relation:** {entry.get('relation', 'N/A')}")
                with c2:
                    if entry.get("age_onset"):
                        st.markdown(f"**Age of Onset:** {entry['age_onset']}")
                    st.markdown(f"**Severity:** <span style='color:{sev_col};font-weight:600;'>{sev}</span>", unsafe_allow_html=True)
                if entry.get("notes"):
                    st.markdown("---")
                    st.markdown(entry["notes"])
                if st.button("🗑️ Delete", key=f"del_fh_{entry.get('id', '')}"):
                    del_r = api_delete(f"/health/family-history/{entry['id']}")
                    if del_r and del_r.status_code == 200:
                        st.rerun()
    else:
        st.info("No family history recorded yet. Add your first entry above!")
else:
    st.info("No family history recorded yet. Add your first entry above!")
