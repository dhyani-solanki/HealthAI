import streamlit as st
import requests
from utils import require_login, BASE_URL
from styles import GLOBAL_CSS, page_header_html, navbar_html, animated_bg_html

st.set_page_config(page_title="Family Reports — HealthAI", page_icon="👪", layout="wide")
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
st.markdown(navbar_html(active="Family Reports", initials=initials, is_light=is_light), unsafe_allow_html=True)

col_back, col_space = st.columns([2, 10])
with col_back:
    if st.button("← Back to Dashboard", key="back_fr"):
        st.switch_page("pages/1_🏠_Dashboard.py")

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(page_header_html(
    "Family Reports",
    "View and manage medical reports uploaded for family members",
    "👪", "#8b5cf6"
), unsafe_allow_html=True)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.fr-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 1rem;
    padding: 1.4rem;
    margin-bottom: 1rem;
    transition: transform .2s, box-shadow .2s;
}
.fr-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(139,92,246,0.15);
}
.fr-member-name {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #e8f4f8;
    margin-bottom: .25rem;
}
.fr-count {
    font-size: .78rem;
    color: #7a9ab5;
}
.fr-report-item {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: .75rem;
    padding: .8rem 1rem;
    margin: .4rem 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.fr-report-type {
    font-family: 'Syne', sans-serif;
    font-size: .88rem;
    font-weight: 600;
    color: #e8f4f8;
}
.fr-report-date {
    font-size: .72rem;
    color: #7a9ab5;
}
.fr-status-badge {
    font-size: .68rem;
    padding: .15rem .5rem;
    border-radius: .5rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .04em;
}
.fr-badge-analysed { background: rgba(0,255,136,.08); color: #00ff88; border: 1px solid rgba(0,255,136,.2); }
.fr-badge-uploaded { background: rgba(255,200,0,.08); color: #ffc800; border: 1px solid rgba(255,200,0,.2); }
.fr-empty {
    text-align: center;
    padding: 3rem;
    color: #7a9ab5;
}
.fr-empty-icon { font-size: 3rem; margin-bottom: .75rem; }
.fr-param {
    display: flex;
    align-items: center;
    gap: .6rem;
    padding: .45rem .8rem;
    border-bottom: 1px solid rgba(255,255,255,.03);
}
.fr-dot { width:7px; height:7px; border-radius:50%; flex-shrink:0; }
.fr-pname { font-size:.82rem;color:#7a9ab5;flex:1; }
.fr-pval  { font-size:.88rem;font-weight:700;color:#e8f4f8; }
.fr-punit { font-size:.72rem;color:#536b83;margin-left:.15rem; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
TOKEN = st.session_state.get("access_token", "")

def _hdrs():
    return {"Authorization": f"Bearer {TOKEN}"}

STATUS_COLOR = {
    "low": "#ff6b6b", "high": "#ff6b6b", "borderline": "#ffa502", "normal": "#00ff88"
}
STATUS_EMOJI = {
    "low": "🔴", "high": "🔴", "borderline": "🟡", "normal": "🟢"
}
RELATION_ICONS = {
    "Father": "👨", "Mother": "👩", "Brother": "🧑", "Sister": "👧",
    "Spouse": "💑", "Son": "👦", "Daughter": "👧", "Unknown": "👤",
}

# ── Fetch family reports ──────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def fetch_family_reports():
    try:
        r = requests.get(f"{BASE_URL}/medreport/family-reports", headers=_hdrs(), timeout=15)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {"family_members": []}

data = fetch_family_reports()
members = data.get("family_members", [])

# ── Quick actions ─────────────────────────────────────────────────────────────
col_a1, col_a2, col_a3 = st.columns([3, 3, 6])
with col_a1:
    if st.button("📤 Upload Family Report", type="primary", use_container_width=True, key="fr_upload"):
        st.switch_page("pages/8_📊_Data_Insights.py")
with col_a2:
    if st.button("🔄 Refresh", use_container_width=True, key="fr_refresh"):
        st.cache_data.clear()
        st.rerun()

# ── Display ───────────────────────────────────────────────────────────────────
if not members:
    st.markdown("""
    <div class="fr-empty">
        <div class="fr-empty-icon">👪</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;color:#e8f4f8;margin-bottom:.4rem;">
            No Family Reports Yet</div>
        <div style="color:#7a9ab5;font-size:.85rem;">
            Upload a medical report from the Data Insights page and select "Family Member" to get started.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    # Overview cards
    st.markdown("""
    <div style="font-size:.72rem;font-weight:700;color:var(--muted);text-transform:uppercase;
                letter-spacing:.1em;margin:1rem 0 .8rem;display:flex;align-items:center;gap:.5rem;">
        👪 Family Members
        <span style="flex:1;height:1px;background:var(--border);display:inline-block;"></span>
    </div>""", unsafe_allow_html=True)

    # Member cards
    for member in members:
        name = member.get("name", "Unknown")
        icon = RELATION_ICONS.get(name, "👤")
        count = member.get("report_count", 0)
        reports = member.get("reports", [])

        with st.expander(f"{icon} {name} — {count} report{'s' if count != 1 else ''}", expanded=False):
            for rep in reports:
                report_type = rep.get("report_label", rep.get("report_type", "Unknown"))
                upload_date = rep.get("upload_date", "")[:10]
                status = rep.get("status", "uploaded")
                badge_cls = "fr-badge-analysed" if status == "analysed" else "fr-badge-uploaded"
                rep_id = rep.get("id", "")

                st.markdown(f"""
                <div class="fr-report-item">
                    <div>
                        <div class="fr-report-type">📋 {report_type}</div>
                        <div class="fr-report-date">📅 {upload_date} · 📄 {rep.get('file_name', 'N/A')}</div>
                    </div>
                    <span class="fr-status-badge {badge_cls}">{status}</span>
                </div>""", unsafe_allow_html=True)

                # Show parameters if analysed
                params = rep.get("parameters", [])
                if params:
                    for p in params:
                        color = STATUS_COLOR.get(p.get("status", "normal"), "#00ff88")
                        emoji = STATUS_EMOJI.get(p.get("status", "normal"), "🟢")
                        nr = p.get("normal_range", "")
                        insight = p.get("insight", "")
                        st.markdown(f"""
                        <div class="fr-param">
                            <div class="fr-dot" style="background:{color};box-shadow:0 0 7px {color}55;"></div>
                            <div class="fr-pname">{p['name']}</div>
                            <div style="text-align:right">
                                <span class="fr-pval">{p['value']}</span>
                                <span class="fr-punit">{p.get('unit','')}</span>
                                <div style="font-size:.7rem;color:#536b83;">{emoji} {p.get('status','').title()}{'  ·  Ref: ' + nr if nr else ''}</div>
                                {f'<div style="font-size:.68rem;color:#ffa502;margin-top:.1rem;">💡 {insight}</div>' if insight else ''}
                            </div>
                        </div>""", unsafe_allow_html=True)

                # Show summary
                summary = rep.get("summary", "")
                if summary:
                    st.markdown(f"""
                    <div style="margin:.5rem 0;padding:.6rem .8rem;background:rgba(139,92,246,.06);
                                border-radius:.6rem;border:1px solid rgba(139,92,246,.12);">
                        <div style="font-size:.75rem;font-weight:600;color:#8b5cf6;margin-bottom:.3rem;">🤖 AI Summary</div>
                        <div style="font-size:.8rem;color:#e8f4f8;line-height:1.5;">{summary}</div>
                    </div>""", unsafe_allow_html=True)

                # Delete button
                if st.button(f"🗑️ Delete", key=f"del_fr_{rep_id}"):
                    try:
                        del_r = requests.delete(
                            f"{BASE_URL}/medreport/reports/{rep_id}",
                            headers=_hdrs(), timeout=15
                        )
                        if del_r.status_code == 200:
                            st.success("✅ Report deleted!")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete report.")
                    except Exception:
                        st.error("❌ Connection error.")

                st.markdown("---")
