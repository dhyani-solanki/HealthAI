import streamlit as st
from utils import api_get, require_login, handle_response_error
from styles import (
    GLOBAL_CSS, section_label_html, stat_card_html,
    navbar_html, animated_bg_html, page_header_html
)

st.set_page_config(page_title="Dashboard — HealthAI", page_icon="🏥", layout="wide")
require_login()

# ── Session state: theme ──────────────────────────────────────────────────────
if "theme_light" not in st.session_state:
    st.session_state.theme_light = False

is_light = st.session_state.theme_light

# ── Inject global CSS ─────────────────────────────────────────────────────────
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Light mode overrides ──────────────────────────────────────────────────────
if is_light:
    st.markdown("""
<script>document.body.classList.add('light-mode');</script>
<style>
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main {
  background-color: #F9FAFB !important;
  color: #0f172a !important;
}
.stat-card, .feature-card, .activity-card, .db-header, .page-header, .auth-card {
  background: #FFFFFF !important;
}
.hn-wrap {
  background: rgba(255,255,255,0.95) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Animated background ───────────────────────────────────────────────────────
st.markdown(animated_bg_html(is_light), unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def _initials(name: str) -> str:
    parts = (name or "U").split()
    return (parts[0][0] + (parts[1][0] if len(parts) > 1 else "")).upper()

user_name = st.session_state.get("user_name", "User")
initials  = _initials(user_name)

# ════════════════════════════════════════════════════════════════════════
#  1 ▸ HORIZONTAL NAVBAR  (first element — sticky at top)
# ════════════════════════════════════════════════════════════════════════
st.markdown(
    navbar_html(active="", initials=initials, is_light=is_light, user_name=user_name),
    unsafe_allow_html=True
)

# ── Invisible Streamlit buttons wired to navbar via JS ───────────────────────
# Theme-toggle: the navbar pill clicks this hidden button
st.markdown("""
<style>
#hn-toggle-wrap {
  position: fixed; left: -9999px; opacity: 0; pointer-events: none;
  width: 1px; height: 1px; overflow: hidden;
}
</style>
<script>
(function wire() {
  var pill = document.getElementById("theme-pill");
  if (!pill) { setTimeout(wire, 300); return; }
  if (pill._wired) return;
  pill._wired = true;
  pill.style.cursor = "pointer";
  pill.addEventListener("click", function() {
    var btn = document.querySelector("#hn-toggle-wrap button");
    if (btn) btn.click();
  });
})();
</script>
""", unsafe_allow_html=True)

st.markdown('<div id="hn-toggle-wrap">', unsafe_allow_html=True)
_tgl = "☀️" if not is_light else "🌙"
if st.button(_tgl, key="theme_toggle", help="Toggle theme"):
    st.session_state.theme_light = not is_light
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# Logout: the navbar dropdown "Logout" item clicks this hidden button
st.markdown("""
<style>
#hn-logout-wrap {
  position: fixed; left: -9999px; opacity: 0; pointer-events: none;
  width: 1px; height: 1px; overflow: hidden;
}
</style>
<script>
(function wireLogout() {
  var ddBtn = document.getElementById("dd-logout-btn");
  if (!ddBtn) { setTimeout(wireLogout, 300); return; }
  if (ddBtn._wired) return;
  ddBtn._wired = true;
  ddBtn.addEventListener("click", function(e) {
    e.stopPropagation();
    var btn = document.querySelector("#hn-logout-wrap button");
    if (btn) btn.click();
  });
})();
</script>
""", unsafe_allow_html=True)

st.markdown('<div id="hn-logout-wrap">', unsafe_allow_html=True)
if st.button("🚪 Logout", key="_navbar_logout"):
    st.session_state.access_token = None
    st.session_state.user_name    = None
    st.session_state.mg_messages  = []
    st.session_state.theme_light  = False
    st.switch_page("app.py")
st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════
#  SVG Illustrations
# ════════════════════════════════════════════════════════════════════════
SVG_MEDIGENIUS = """
<svg viewBox="0 0 260 155" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="260" height="155" rx="0" fill="url(#gMG)"/>
  <defs>
    <linearGradient id="gMG" x1="0" y1="0" x2="260" y2="155" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#0d1f3c"/>
      <stop offset="100%" stop-color="#071630"/>
    </linearGradient>
  </defs>
  <ellipse cx="130" cy="75" rx="52" ry="44" fill="none" stroke="rgba(59,130,246,0.18)" stroke-width="1.5"/>
  <circle cx="130" cy="34" r="6" fill="rgba(59,130,246,0.25)" stroke="#3b82f6" stroke-width="1.2"/>
  <circle cx="100" cy="55" r="5" fill="rgba(6,182,212,0.25)" stroke="#06b6d4" stroke-width="1.2"/>
  <circle cx="160" cy="55" r="5" fill="rgba(6,182,212,0.25)" stroke="#06b6d4" stroke-width="1.2"/>
  <circle cx="90"  cy="82" r="5" fill="rgba(59,130,246,0.2)"  stroke="#3b82f6" stroke-width="1.2"/>
  <circle cx="170" cy="82" r="5" fill="rgba(59,130,246,0.2)"  stroke="#3b82f6" stroke-width="1.2"/>
  <circle cx="110" cy="108" r="4" fill="rgba(6,182,212,0.2)"  stroke="#06b6d4" stroke-width="1.2"/>
  <circle cx="150" cy="108" r="4" fill="rgba(6,182,212,0.2)"  stroke="#06b6d4" stroke-width="1.2"/>
  <line x1="130" y1="40" x2="100" y2="55" stroke="rgba(59,130,246,0.3)" stroke-width="0.8"/>
  <line x1="130" y1="40" x2="160" y2="55" stroke="rgba(59,130,246,0.3)" stroke-width="0.8"/>
  <line x1="100" y1="60" x2="90"  y2="82" stroke="rgba(59,130,246,0.3)" stroke-width="0.8"/>
  <line x1="160" y1="60" x2="170" y2="82" stroke="rgba(59,130,246,0.3)" stroke-width="0.8"/>
  <line x1="90"  y1="87" x2="110" y2="108" stroke="rgba(6,182,212,0.3)" stroke-width="0.8"/>
  <line x1="170" y1="87" x2="150" y2="108" stroke="rgba(6,182,212,0.3)" stroke-width="0.8"/>
  <circle cx="130" cy="75" r="16" fill="url(#gMGc)"/>
  <defs>
    <linearGradient id="gMGc" x1="114" y1="59" x2="146" y2="91" gradientUnits="userSpaceOnUse">
      <stop stop-color="#3b82f6"/>
      <stop offset="1" stop-color="#06b6d4"/>
    </linearGradient>
  </defs>
  <text x="130" y="79" text-anchor="middle" fill="white" font-size="12" font-family="sans-serif">🧠</text>
</svg>
"""

SVG_MEDISCAN = """
<svg viewBox="0 0 260 155" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="260" height="155" rx="0" fill="url(#gMS)"/>
  <defs>
    <linearGradient id="gMS" x1="0" y1="0" x2="260" y2="155" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#0a1f2e"/>
      <stop offset="100%" stop-color="#061828"/>
    </linearGradient>
  </defs>
  <rect x="70" y="35" width="120" height="85" rx="10" fill="none" stroke="rgba(6,182,212,0.25)" stroke-width="1.5"/>
  <rect x="82" y="47" width="96" height="61" rx="6" fill="rgba(6,182,212,0.05)" stroke="rgba(6,182,212,0.18)" stroke-width="1"/>
  <line x1="82" y1="77" x2="178" y2="77" stroke="rgba(6,182,212,0.6)" stroke-width="1.5" stroke-dasharray="4 3"/>
  <rect x="108" y="57" width="44" height="40" rx="4" fill="none" stroke="rgba(6,182,212,0.4)" stroke-width="1"/>
  <circle cx="130" cy="77" r="10" fill="rgba(6,182,212,0.15)" stroke="#06b6d4" stroke-width="1.2"/>
  <circle cx="130" cy="77" r="4"  fill="#06b6d4"/>
  <line x1="130" y1="35" x2="130" y2="47" stroke="rgba(6,182,212,0.5)" stroke-width="1.5"/>
  <line x1="130" y1="108" x2="130" y2="120" stroke="rgba(6,182,212,0.5)" stroke-width="1.5"/>
  <line x1="70"  y1="77" x2="82"  y2="77" stroke="rgba(6,182,212,0.5)" stroke-width="1.5"/>
  <line x1="178" y1="77" x2="190" y2="77" stroke="rgba(6,182,212,0.5)" stroke-width="1.5"/>
</svg>
"""

SVG_RECORDS = """
<svg viewBox="0 0 260 155" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="260" height="155" rx="0" fill="url(#gRec)"/>
  <defs>
    <linearGradient id="gRec" x1="0" y1="0" x2="260" y2="155" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#0a2010"/>
      <stop offset="100%" stop-color="#061808"/>
    </linearGradient>
  </defs>
  <rect x="65" y="30" width="90" height="110" rx="8" fill="rgba(34,197,94,0.06)" stroke="rgba(34,197,94,0.22)" stroke-width="1.5"/>
  <rect x="75" y="45" width="70" height="5" rx="2.5" fill="rgba(34,197,94,0.3)"/>
  <rect x="75" y="57" width="55" height="4" rx="2" fill="rgba(34,197,94,0.18)"/>
  <rect x="75" y="68" width="60" height="4" rx="2" fill="rgba(34,197,94,0.18)"/>
  <rect x="75" y="79" width="45" height="4" rx="2" fill="rgba(34,197,94,0.18)"/>
  <rect x="75" y="90" width="50" height="4" rx="2" fill="rgba(34,197,94,0.18)"/>
  <rect x="75" y="101" width="40" height="4" rx="2" fill="rgba(34,197,94,0.15)"/>
  <rect x="105" y="55" width="90" height="75" rx="8" fill="rgba(34,197,94,0.08)" stroke="rgba(34,197,94,0.28)" stroke-width="1.5"/>
  <rect x="113" y="68" width="70" height="5"  rx="2.5" fill="rgba(34,197,94,0.35)"/>
  <rect x="113" y="80" width="58" height="4" rx="2" fill="rgba(34,197,94,0.2)"/>
  <rect x="113" y="91" width="52" height="4" rx="2" fill="rgba(34,197,94,0.2)"/>
  <rect x="113" y="102" width="44" height="4" rx="2" fill="rgba(34,197,94,0.2)"/>
</svg>
"""

SVG_DATAINSIGHT = """
<svg viewBox="0 0 260 155" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="260" height="155" rx="0" fill="url(#gDI)"/>
  <defs>
    <linearGradient id="gDI" x1="0" y1="0" x2="260" y2="155" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#13082b"/>
      <stop offset="100%" stop-color="#0c0620"/>
    </linearGradient>
  </defs>
  <!-- Bar chart -->
  <rect x="55"  y="95" width="22" height="35" rx="4" fill="rgba(168,85,247,0.55)"/>
  <rect x="83"  y="75" width="22" height="55" rx="4" fill="rgba(168,85,247,0.7)"/>
  <rect x="111" y="55" width="22" height="75" rx="4" fill="rgba(139,92,246,0.85)"/>
  <rect x="139" y="68" width="22" height="62" rx="4" fill="rgba(99,102,241,0.75)"/>
  <rect x="167" y="42" width="22" height="88" rx="4" fill="rgba(168,85,247,0.9)"/>
  <!-- Trend line -->
  <polyline points="66,88 94,68 122,48 150,60 178,35"
            fill="none" stroke="#a855f7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="66"  cy="88" r="4" fill="#a855f7"/>
  <circle cx="94"  cy="68" r="4" fill="#a855f7"/>
  <circle cx="122" cy="48" r="4" fill="#a855f7"/>
  <circle cx="150" cy="60" r="4" fill="#a855f7"/>
  <circle cx="178" cy="35" r="4.5" fill="#c084fc" stroke="#a855f7" stroke-width="1.5"/>
  <!-- Grid lines -->
  <line x1="50" y1="130" x2="205" y2="130" stroke="rgba(168,85,247,0.15)" stroke-width="1"/>
  <line x1="50" y1="100" x2="205" y2="100" stroke="rgba(168,85,247,0.08)" stroke-width="1"/>
  <line x1="50" y1="70"  x2="205" y2="70"  stroke="rgba(168,85,247,0.08)" stroke-width="1"/>
</svg>
"""

# ════════════════════════════════════════════════════════════════════════
#  2 ▸ WELCOME HEADER  (second element, below navbar)
# ════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="db-header">
  <div class="db-header-left">
    <div class="db-greeting">Good day 👋</div>
    <h1 class="db-title">Welcome, <span class="db-name">{user_name}</span></h1>
    <div class="db-subtitle">Your health dashboard — all insights in one place.</div>
  </div>
  <div class="db-header-right">
    <div class="db-avatar">{initials}</div>
    <div class="db-ai-badge">
      <span class="db-ai-dot"></span>
      AI Active
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════
#  3 ▸ STATS CARDS   (fetch real data from API)
# ════════════════════════════════════════════════════════════════════════
STAT_META = [
    ("mg_count",       "💬", "AI Conversations", "#3b82f6", "rgba(59,130,246,0.15)",  "rgba(59,130,246,0.25)"),
    ("scan_count",     "💊", "Medicine Scans",   "#06b6d4", "rgba(6,182,212,0.15)",   "rgba(6,182,212,0.25)"),
    ("records_count",  "📋", "Health Records",   "#22c55e", "rgba(34,197,94,0.15)",   "rgba(34,197,94,0.25)"),
    ("family_count",   "👨‍👩‍👧", "Family Entries", "#f97316", "rgba(249,115,22,0.15)",  "rgba(249,115,22,0.25)"),
    ("total_insights", "📈", "Data Insights",    "#a855f7", "rgba(168,85,247,0.15)",  "rgba(168,85,247,0.25)"),
]

stats_resp = api_get("/dashboard/stats")
stats_data = {}
if stats_resp and stats_resp.status_code == 200:
    stats_data = stats_resp.json()

st.markdown(section_label_html("📊 Your Health Overview"), unsafe_allow_html=True)

stat_cols = st.columns(len(STAT_META))
for i, (key, icon, label, color, ic, ib) in enumerate(STAT_META):
    value = stats_data.get(key, "—")
    with stat_cols[i]:
        st.markdown(stat_card_html(icon, value, label, color, ic, ib, index=i), unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════
#  4 ▸ FEATURE CARDS  (navigate to modules)
# ════════════════════════════════════════════════════════════════════════
FEATURE_CARDS = [
    {
        "title":    "MediGenius",
        "subtitle": "AI health chat",
        "icon":     "💬",
        "color":    "#3b82f6",
        "page":     "pages/2_💬_MediGenius.py",
        "svg":      SVG_MEDIGENIUS,
        "tag":      "AI-Powered",
    },
    {
        "title":    "MediScan",
        "subtitle": "Medicine intelligence",
        "icon":     "💊",
        "color":    "#06b6d4",
        "page":     "pages/3_💊_MediScan.py",
        "svg":      SVG_MEDISCAN,
        "tag":      "Image + Text",
    },
    {
        "title":    "Health Records",
        "subtitle": "Manage your records",
        "icon":     "📋",
        "color":    "#22c55e",
        "page":     "pages/4_📋_Health_Records.py",
        "svg":      SVG_RECORDS,
        "tag":      "Secure Vault",
    },
    {
        "title":    "DataInsight",
        "subtitle": "Analyse health reports",
        "icon":     "📈",
        "color":    "#a855f7",
        "page":     "pages/8_📊_Data_Insights.py",
        "svg":      SVG_DATAINSIGHT,
        "tag":      "Lab Reports",
    },
]

st.markdown(section_label_html("🚀 Health Modules"), unsafe_allow_html=True)

cols = st.columns(len(FEATURE_CARDS))
for i, card in enumerate(FEATURE_CARDS):
    with cols[i]:
        st.markdown(f"""
<div class="feature-card" style="--fc:{card['color']}; --i:{i};">
  <div class="feature-card-img">{card['svg']}</div>
  <div class="feature-card-body">
    <div class="feature-card-tag">{card['tag']}</div>
    <div class="feature-card-title">{card['icon']} {card['title']}</div>
    <div class="feature-card-sub">{card['subtitle']}</div>
  </div>
</div>
""", unsafe_allow_html=True)
        if st.button(f"Open {card['title']}", key=f"fc_{i}", use_container_width=True):
            st.switch_page(card["page"])

# ════════════════════════════════════════════════════════════════════════
#  5 ▸ RECENT ACTIVITY
# ════════════════════════════════════════════════════════════════════════
st.markdown(section_label_html("📝 Recent Activity"), unsafe_allow_html=True)

act_col1, act_col2, act_col3 = st.columns(3)

# Recent conversations
with act_col1:
    st.markdown('<div class="activity-card">', unsafe_allow_html=True)
    st.markdown('<div class="activity-card-title">💬 Recent Chats</div>', unsafe_allow_html=True)
    mg_resp = api_get("/medigenius/history")
    if mg_resp and mg_resp.status_code == 200:
        msgs = mg_resp.json()
        user_msgs = [m for m in msgs if m.get("role") == "user"][-3:]
        if user_msgs:
            for m in reversed(user_msgs):
                preview = (m["content"][:55] + "…") if len(m["content"]) > 55 else m["content"]
                st.markdown(f'<div class="activity-item">💬 {preview}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="activity-empty">No conversations yet</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Recent scans
with act_col2:
    st.markdown('<div class="activity-card">', unsafe_allow_html=True)
    st.markdown('<div class="activity-card-title">💊 Recent Scans</div>', unsafe_allow_html=True)
    scan_resp = api_get("/mediscan/history")
    if scan_resp and scan_resp.status_code == 200:
        scans = scan_resp.json()[-3:]
        if scans:
            for s in reversed(scans):
                date_str = s.get("scanned_at", "")[:10]
                st.markdown(f'<div class="activity-item">💊 {s["medicine_name"]} <span class="act-date">{date_str}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="activity-empty">No scans yet</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# DataInsight activity
with act_col3:
    st.markdown('<div class="activity-card">', unsafe_allow_html=True)
    st.markdown('<div class="activity-card-title">📈 DataInsight Summary</div>', unsafe_allow_html=True)
    di_resp = api_get("/data-insights/reports")
    if di_resp and di_resp.status_code == 200:
        reports = di_resp.json()
        if reports:
            st.markdown(f'<div class="activity-item">📊 {len(reports)} report(s) uploaded</div>', unsafe_allow_html=True)
            latest = reports[-1]
            lbl    = latest.get("report_label") or latest.get("report_type", "Report")
            date   = latest.get("upload_date", "")[:10]
            st.markdown(f'<div class="activity-item">🔬 Latest: {lbl}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="activity-item act-date">📅 {date}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="activity-empty">No reports yet</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="activity-empty">Upload a health report to see insights</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════
#  6 ▸ QUICK NAV BUTTONS
# ════════════════════════════════════════════════════════════════════════
st.markdown("<br>", unsafe_allow_html=True)
qn_cols = st.columns(5)
quick_links = [
    ("💬 MediGenius",  "pages/2_💬_MediGenius.py"),
    ("💊 MediScan",    "pages/3_💊_MediScan.py"),
    ("📋 Records",     "pages/4_📋_Health_Records.py"),
    ("👨‍👩‍👧 Family",  "pages/5_👨‍👩‍👧_Family_History.py"),
    ("📈 DataInsight", "pages/8_📊_Data_Insights.py"),
]
for i, (label, page) in enumerate(quick_links):
    with qn_cols[i]:
        if st.button(label, key=f"qn_{i}", use_container_width=True):
            st.switch_page(page)
