# ============================================================
#  pages/8_📊_Data_Insights.py  (v2 — Plotly charts + re-analyze)
# ============================================================
#  UPDATED: Added horizontal navbar + theme support

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import requests
import streamlit as st

try:
    import plotly.graph_objects as go
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

from utils import BASE_URL, get_auth_header, require_login, api_get, api_delete
from styles import navbar_html, animated_bg_html

st.set_page_config(
    page_title="DataInsight — HealthAI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

try:
    from styles import GLOBAL_CSS
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
except ImportError:
    pass

# ── Theme + Navbar ────────────────────────────────────────────────
_is_light = st.session_state.get("theme_light", False)
if _is_light:
    st.markdown("""<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
  background-color: #F9FAFB !important; color: #0f172a !important; }
.hn-wrap { background: rgba(255,255,255,0.95) !important; }
</style>""", unsafe_allow_html=True)
st.markdown(animated_bg_html(_is_light), unsafe_allow_html=True)

# ─── Scoped CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');

.di-hdr{background:#0a1628;border:1px solid rgba(0,212,255,.15);border-radius:20px;padding:1.8rem 2.2rem;margin-bottom:1.5rem;position:relative;overflow:hidden;}
.di-hdr::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,#00d4ff,#7b5ea7,transparent);}
.di-hdr h1{font-family:'Syne',sans-serif;font-size:1.7rem;font-weight:800;color:#e8f4f8;letter-spacing:-0.02em;margin:0;}
.di-hdr p{color:#7a9ab5;font-size:.9rem;margin:.25rem 0 0;}

.di-sec{font-family:'Syne',sans-serif;font-size:1.05rem;font-weight:700;color:#00d4ff;text-transform:uppercase;letter-spacing:.08em;margin:1.8rem 0 .9rem;display:flex;align-items:center;gap:.5rem;}
.di-sec::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,rgba(0,212,255,.3),transparent);}

.di-card{background:#0a1628;border:1px solid rgba(255,255,255,.07);border-radius:16px;padding:1rem 1.1rem;margin-bottom:.5rem;animation:diIn .35s ease both;}
@keyframes diIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}

.di-param{display:flex;align-items:center;gap:.8rem;padding:.75rem 1rem;background:#0a1628;border:1px solid rgba(255,255,255,.06);border-radius:12px;margin-bottom:.45rem;}
.di-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0;}
.di-pname{font-size:.88rem;font-weight:600;color:#e8f4f8;flex:1;}
.di-pval{font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;color:#e8f4f8;}
.di-punit{font-size:.72rem;color:#7a9ab5;margin-left:2px;}
.di-prange{font-size:.7rem;color:#7a9ab5;margin-top:.1rem;}
.di-pstatus{font-size:.68rem;font-weight:700;padding:.15rem .5rem;border-radius:50px;font-family:'Syne',sans-serif;letter-spacing:.04em;}

.di-badge-high{background:rgba(0,255,136,.1);border:1px solid rgba(0,255,136,.4);color:#00ff88;}
.di-badge-medium{background:rgba(255,165,2,.1);border:1px solid rgba(255,165,2,.4);color:#ffa502;}
.di-badge-low-conf{background:rgba(255,71,87,.1);border:1px solid rgba(255,71,87,.4);color:#ff4757;}

.di-ai{background:linear-gradient(135deg,rgba(0,212,255,.04),rgba(123,94,167,.06));border:1px solid rgba(0,212,255,.2);border-radius:16px;padding:1.4rem 1.6rem;margin-top:1rem;position:relative;}
.di-ai::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,#00d4ff,#7b5ea7,transparent);border-radius:16px 16px 0 0;}
.di-ai-hdr{display:flex;align-items:center;gap:.7rem;margin-bottom:.9rem;}
.di-ai-av{width:36px;height:36px;background:linear-gradient(135deg,#00d4ff,#7b5ea7);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.1rem;box-shadow:0 4px 14px rgba(0,212,255,.3);}
.di-ai-text{color:#e8f4f8;font-size:.91rem;line-height:1.78;white-space:pre-wrap;}
.di-disc{font-size:.7rem;color:#7a9ab5;margin-top:.9rem;padding:.45rem .8rem;background:rgba(255,165,2,.05);border:1px solid rgba(255,165,2,.18);border-radius:8px;}

.di-empty{text-align:center;padding:3rem 1rem;color:#7a9ab5;}
.di-empty-icon{font-size:4rem;margin-bottom:.8rem;opacity:.35;}
.di-empty h3{font-family:'Syne',sans-serif;font-size:1.05rem;color:#e8f4f8;margin-bottom:.4rem;}

.di-rcard{background:#0a1628;border:1px solid rgba(255,255,255,.06);border-left:3px solid #00d4ff;border-radius:14px;padding:1rem 1.2rem;margin-bottom:.55rem;display:flex;align-items:center;gap:1rem;}
.di-rcard-info{flex:1}
.di-rcard-name{font-family:'Syne',sans-serif;font-weight:700;color:#e8f4f8;font-size:.9rem;}
.di-rcard-sub{color:#7a9ab5;font-size:.74rem;margin-top:.1rem;}
.di-upload-wrap{background:#0a1628;border:2px dashed rgba(0,212,255,.3);border-radius:18px;padding:1.8rem;text-align:center;transition:border-color .3s;}
.di-upload-wrap:hover{border-color:rgba(0,212,255,.65);}

.di-delta{background:#0a1628;border:1px solid rgba(255,255,255,.06);border-radius:12px;padding:.75rem 1rem;margin-bottom:.45rem;}
.di-delta-name{font-size:.82rem;font-weight:600;color:#e8f4f8;margin-bottom:.25rem;}
.di-delta-row{display:flex;gap:.5rem;align-items:center;font-size:.85rem;}

</style>
""", unsafe_allow_html=True)

# ─── Auth ───────────────────────────────────────────────────────
require_login()

# ─── Navbar + back button ────────────────────────────────────────
_un = st.session_state.get("user_name", "User")
_init = (_un[0] + (_un.split()[1][0] if len(_un.split()) > 1 else "")).upper()
st.markdown(navbar_html(active="DataInsight", initials=_init, is_light=_is_light), unsafe_allow_html=True)
_cb, _cs = st.columns([2, 10])
with _cb:
    if st.button("← Back to Dashboard", key="back_di"):
        st.switch_page("pages/1_🏠_Dashboard.py")

# ─── Session state ──────────────────────────────────────────────
def _ss(key, val):
    if key not in st.session_state: st.session_state[key] = val

_ss("di_upload_result",   None)
_ss("di_selected_report", None)
_ss("di_ai_text",         "")
_ss("di_compare_deltas",  [])
_ss("di_compare_text",    "")
_ss("di_expanded_card",   None)
_ss("di_delete_confirm",  None)

def _hdrs(): return get_auth_header()

CONF_CLS  = {"high": "di-badge-high", "medium": "di-badge-medium", "low": "di-badge-low-conf"}
ST_COLOR  = {"normal": "#00ff88", "borderline": "#ffa502", "high": "#ff4757", "low": "#ff4757"}
ST_EMOJI  = {"normal": "🟢", "borderline": "🟡", "high": "🔴", "low": "🔴"}
ST_LABEL  = {"normal": "Normal", "borderline": "Borderline", "high": "High ↑", "low": "Low ↓"}

# ─── SSE consumer ───────────────────────────────────────────────
def _consume_sse(url): 
    parts = []
    try:
        with requests.get(url, headers=_hdrs(), stream=True, timeout=90) as r:
            for line in r.iter_lines():
                if line:
                    d = line.decode("utf-8") if isinstance(line, bytes) else line
                    if d.startswith("data: "):
                        tok = d[6:]
                        if tok in ("[START]","[DONE]") or tok.startswith("[DELTA]"):
                            continue
                        parts.append(tok + " ")
    except Exception as e:
        parts.append(f"⚠️ {e}")
    return "".join(parts)

def _consume_sse_compare(url):
    parts, deltas = [], []
    try:
        with requests.get(url, headers=_hdrs(), stream=True, timeout=90) as r:
            for line in r.iter_lines():
                if line:
                    d = line.decode("utf-8") if isinstance(line, bytes) else line
                    if d.startswith("data: "):
                        tok = d[6:]
                        if tok in ("[START]","[DONE]"): continue
                        if tok.startswith("[DELTA]"):
                            try: deltas = json.loads(tok[7:])
                            except: pass
                            continue
                        parts.append(tok + " ")
    except Exception as e:
        parts.append(f"⚠️ {e}")
    return deltas, "".join(parts)

# ══════════════════════════════════════════════════════════════════
#  PAGE HEADER
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div class="di-hdr">
  <div style="display:flex;align-items:center;gap:1.2rem;">
    <div style="font-size:2.4rem;background:rgba(0,212,255,.1);border:1px solid rgba(0,212,255,.2);
                border-radius:14px;width:62px;height:62px;display:flex;align-items:center;justify-content:center;">📊</div>
    <div>
      <h1>Data Insights</h1>
      <p>Upload health reports · AI detection · Charts & trends · Streamed AI analysis</p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
#  SECTION 1 — REPORT INFO CARDS
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="di-sec">📚 Health Report Reference</div>', unsafe_allow_html=True)

@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_info():
    try:
        r = requests.get(f"{BASE_URL}/data-insights/report-info", headers=get_auth_header(), timeout=8)
        return r.json() if r.status_code == 200 else []
    except: return []

info_cards = _fetch_info()
if info_cards:
    cols = st.columns(len(info_cards) if len(info_cards) <= 5 else 5)
    for i, card in enumerate(info_cards):
        with cols[i % 5]:
            active = st.session_state.di_expanded_card == card["key"]
            btn_label = f"{card['icon']}\n{card['label'].split('(')[0].strip()}"
            if st.button(btn_label, key=f"ic_{card['key']}", use_container_width=True,
                         help=card["short_desc"]):
                st.session_state.di_expanded_card = None if active else card["key"]
    if st.session_state.di_expanded_card:
        det = next((c for c in info_cards if c["key"] == st.session_state.di_expanded_card), None)
        if det:
            with st.container(border=True):
                st.markdown(f"### {det['icon']}  {det['label']}")
                ca, cb = st.columns(2)
                with ca:
                    st.markdown(f"**🔬 What it measures**\n\n{det['what_it_measures']}")
                    st.markdown(f"**❗ Why important**\n\n{det['why_important']}")
                with cb:
                    st.markdown("**📏 Reference Ranges (WHO / ICMR)**")
                    tbl = "".join(f"<tr><td><b>{r['parameter']}</b></td><td style='color:#00d4ff'>{r['range']}</td></tr>" for r in det["normal_ranges"])
                    st.markdown(f'<table style="width:100%;border-collapse:collapse;font-size:.82rem;color:#e8f4f8">{tbl}</table>', unsafe_allow_html=True)
                    st.markdown("**🏥 Conditions this detects**")
                    st.markdown("  ·  ".join(f"`{c}`" for c in det["conditions_detected"]))

st.markdown("---")

# ══════════════════════════════════════════════════════════════════
#  SECTION 1.5 — UPLOAD MEDICAL REPORT (MedReport Analyzer)
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="di-sec">🏥 Upload Medical Report</div>', unsafe_allow_html=True)

# Session state for medreport upload
_ss("mr_owner_type", "Myself")
_ss("mr_owner_name", None)
_ss("mr_upload_result", None)

st.markdown("""
<div class="di-upload-wrap">
  <div style="font-size:2.4rem;margin-bottom:.5rem;">🏥</div>
  <div style="font-family:'Syne',sans-serif;font-size:.98rem;font-weight:700;color:#e8f4f8;margin-bottom:.25rem;">
    Upload your medical report for AI-powered analysis</div>
  <div style="color:#7a9ab5;font-size:.82rem;">PDF only · Gemini AI will classify, extract parameters & generate summary</div>
</div>""", unsafe_allow_html=True)

# Owner selection
st.markdown("**Whose report is this?**")
mr_col_owner, mr_col_name = st.columns([1, 1])
with mr_col_owner:
    mr_owner_sel = st.radio(
        "Report belongs to:",
        ["Myself", "Family Member", "Others"],
        horizontal=True,
        key="mr_owner_radio",
        label_visibility="collapsed",
    )
    st.session_state.mr_owner_type = mr_owner_sel

with mr_col_name:
    if mr_owner_sel == "Family Member":
        st.session_state.mr_owner_name = st.selectbox(
            "Select Relation",
            ["Father", "Mother", "Brother", "Sister", "Spouse", "Son", "Daughter"],
            key="mr_relation_select",
        )
    elif mr_owner_sel == "Others":
        st.session_state.mr_owner_name = st.text_input(
            "Enter Name", placeholder="e.g. John Doe", key="mr_other_name"
        )
    else:
        st.session_state.mr_owner_name = None

mr_file = st.file_uploader("Upload medical report PDF", type=["pdf"], key="mr_uploader")
if mr_file:
    if st.button("🔬 Analyse Medical Report", type="primary", use_container_width=True, key="mr_analyse_btn"):
        owner_type_val = "myself" if mr_owner_sel == "Myself" else ("family" if mr_owner_sel == "Family Member" else "others")
        with st.spinner("🏥 Uploading → Classifying → Extracting parameters → Generating summary... This may take a minute."):
            try:
                resp = requests.post(
                    f"{BASE_URL}/medreport/upload",
                    headers=_hdrs(),
                    files={"file": (mr_file.name, mr_file.getvalue(), "application/pdf")},
                    data={
                        "owner_type": owner_type_val,
                        "owner_name": st.session_state.mr_owner_name or "",
                    },
                    timeout=180,
                )
                if resp.status_code == 200:
                    result = resp.json()
                    st.session_state.mr_upload_result = result
                    st.cache_data.clear()

                    # Show success with routing info
                    if owner_type_val == "myself":
                        st.success(f"✅ Report analysed! {result.get('message', '')} — Auto-saved to your **Health Records**.")
                    elif owner_type_val == "family":
                        st.success(f"✅ Report analysed! {result.get('message', '')} — Saved under **Family Reports → {st.session_state.mr_owner_name}**.")
                    else:
                        st.success(f"✅ Report analysed! {result.get('message', '')}")
                else:
                    st.error(f"❌ {resp.json().get('detail', 'Upload failed')}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Backend not reachable. Is the server running?")
            except requests.exceptions.ReadTimeout:
                st.error("❌ Analysis timed out. The AI may still be processing — try refreshing.")

# Display medreport result
if st.session_state.mr_upload_result:
    res = st.session_state.mr_upload_result
    conf = res.get("confidence", "low")
    cc = CONF_CLS.get(conf, "di-badge-low-conf")

    st.markdown(f"""
    <div style="margin:.8rem 0;display:flex;align-items:center;flex-wrap:wrap;gap:.6rem;">
      <span style="color:#7a9ab5;font-size:.82rem;">Report Type:</span>
      <span style="font-family:'Syne',sans-serif;font-size:1.05rem;font-weight:700;color:#e8f4f8;">
        📋 &nbsp;{res.get('report_label','Unknown')}</span>
      <span class="di-pstatus {cc}">✓ {conf.upper()} CONFIDENCE</span>
      <span style="color:#7a9ab5;font-size:.78rem;margin-left:.6rem;">
        👤 {res.get('owner_type','myself').title()}{(' — ' + res.get('owner_name','')) if res.get('owner_name') else ''}</span>
    </div>""", unsafe_allow_html=True)

    # Show parameters
    mr_params = res.get("parameters", [])
    if mr_params:
        st.markdown("**📋 Extracted Parameters**")
        for p in mr_params:
            color = ST_COLOR.get(p.get("status", "normal"), "#00ff88")
            emoji = ST_EMOJI.get(p.get("status", "normal"), "🟢")
            slbl = ST_LABEL.get(p.get("status", "normal"), "Normal")
            nr = p.get("normal_range", "")
            insight = p.get("insight", "")
            st.markdown(f"""
            <div class="di-param">
              <div class="di-dot" style="background:{color};box-shadow:0 0 7px {color}55;"></div>
              <div class="di-pname">{p['name']}</div>
              <div style="text-align:right">
                <span class="di-pval">{p['value']}</span>
                <span class="di-punit">{p.get('unit','')}</span>
                <div class="di-prange">{emoji} {slbl}{'  ·  Ref: ' + nr if nr else ''}</div>
                {f'<div style="font-size:.7rem;color:#ffa502;margin-top:.1rem;">💡 {insight}</div>' if insight else ''}
              </div>
            </div>""", unsafe_allow_html=True)

    # Show summary
    mr_summary = res.get("summary", "")
    if mr_summary:
        st.markdown("**📝 AI Summary**")
        st.markdown(f"""
        <div class="di-ai">
          <div class="di-ai-hdr">
            <div class="di-ai-av">🤖</div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;color:#e8f4f8;font-size:.9rem;">
              MedReport AI Analysis</div>
          </div>
          <div class="di-ai-text">{mr_summary}</div>
          <div class="di-disc">⚠️ AI-generated for educational purposes only.
            Always consult a qualified healthcare professional for medical advice.</div>
        </div>""", unsafe_allow_html=True)

    if st.button("🔄 Upload Another Report", key="mr_reset"):
        st.session_state.mr_upload_result = None
        st.rerun()

st.markdown("---")

# ══════════════════════════════════════════════════════════════════
#  SECTION 2 — UPLOAD
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="di-sec">📤 Upload Your Health Report</div>', unsafe_allow_html=True)
st.markdown("""
<div class="di-upload-wrap">
  <div style="font-size:2.4rem;margin-bottom:.5rem;">📄</div>
  <div style="font-family:'Syne',sans-serif;font-size:.98rem;font-weight:700;color:#e8f4f8;margin-bottom:.25rem;">
    Drop your health report here</div>
  <div style="color:#7a9ab5;font-size:.82rem;">PDF or TXT · AI will auto-detect the report type</div>
</div>""", unsafe_allow_html=True)

up_file = st.file_uploader("Upload", type=["pdf","txt"], key="di_uploader", label_visibility="collapsed")
if up_file:
    if st.button("🔍 Detect & Analyse", type="primary", use_container_width=True, key="di_up_btn"):
        with st.spinner("🔬 Extracting and detecting..."):
            try:
                resp = requests.post(
                    f"{BASE_URL}/data-insights/upload",
                    headers=_hdrs(),
                    files={"file": (up_file.name, up_file.getvalue(), "application/pdf")},
                    timeout=60,
                )
                if resp.status_code == 200:
                    r = resp.json()
                    st.session_state.di_upload_result = r
                    st.session_state.di_selected_report = r
                    st.session_state.di_ai_text = ""
                    st.cache_data.clear()
                    st.success("✅ Uploaded and analysed!")
                else:
                    st.error(f"❌ {resp.json().get('detail','Upload failed')}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Backend not reachable.")

if st.session_state.di_upload_result:
    res = st.session_state.di_upload_result
    cc = CONF_CLS.get(res.get("confidence","low"), "di-badge-low-conf")
    st.markdown(f"""
    <div style="margin:.8rem 0;display:flex;align-items:center;flex-wrap:wrap;gap:.6rem;">
      <span style="color:#7a9ab5;font-size:.82rem;">Detected:</span>
      <span style="font-family:'Syne',sans-serif;font-size:1.05rem;font-weight:700;color:#e8f4f8;">
        {res.get('report_icon','📄')} &nbsp;{res.get('report_label','Unknown')}</span>
      <span class="di-pstatus {cc}">✓ {(res.get('confidence') or 'low').upper()} CONFIDENCE</span>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════
#  LOAD EXISTING REPORTS
# ══════════════════════════════════════════════════════════════════
all_resp = api_get("/data-insights/reports")
all_reports = all_resp.json() if all_resp and all_resp.status_code == 200 else []

# ══════════════════════════════════════════════════════════════════
#  SECTION 3 — PARAMETERS + CHARTS + AI
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="di-sec">📈 Parameters &amp; AI Health Insight</div>', unsafe_allow_html=True)

if all_reports:
    opts = {f"#{r['id']} · {r.get('report_label') or r['report_type']} · {r.get('upload_date','')[:10]}": r for r in all_reports}
    sel_lbl = st.selectbox("📂 Select a report to view:", ["— Select —"] + list(opts.keys()), key="di_sel")
    if sel_lbl != "— Select —":
        st.session_state.di_selected_report = opts[sel_lbl]
        st.session_state.di_ai_text = ""

report = st.session_state.di_selected_report
if report:
    params  = report.get("parameters") or []
    rep_id  = report.get("id") or report.get("report_id")
    lbl     = report.get("report_label") or report.get("report_type", "Health Report")

    # Re-analyze button (fixes old reports with junk params)
    ra_col, _ = st.columns([1,3])
    with ra_col:
        if st.button("🔄 Re-analyze parameters", key="di_reanalyze", use_container_width=True):
            with st.spinner("Re-running extraction..."):
                rr = requests.post(f"{BASE_URL}/data-insights/reports/{rep_id}/reanalyze",
                                   headers=_hdrs(), timeout=60)
                if rr.status_code == 200:
                    rd = rr.json()
                    st.session_state.di_selected_report = rd
                    st.session_state.di_ai_text = ""
                    params = rd.get("parameters") or []
                    st.cache_data.clear()
                    st.success(f"✅ {rd.get('message','Done')}")
                    st.rerun()
                else:
                    st.error(f"❌ {rr.json().get('detail','Failed')}")

    if params:
        # ── Summary metrics ─────────────────────────────────────
        n_normal = sum(1 for p in params if p.get("status") == "normal")
        n_border = sum(1 for p in params if p.get("status") == "borderline")
        n_abnorm = sum(1 for p in params if p.get("status") in ("high","low"))
        mc1,mc2,mc3,mc4 = st.columns(4)
        mc1.metric("🔬 Parameters", len(params))
        mc2.metric("🟢 Normal", n_normal)
        mc3.metric("🟡 Borderline", n_border)
        mc4.metric("🔴 Abnormal", n_abnorm)
        st.markdown("<br>", unsafe_allow_html=True)

        # ── Two columns: params left, charts right ───────────────
        col_p, col_c = st.columns([1, 1.4], gap="large")

        with col_p:
            st.markdown("**Key Parameters**")
            for p in params:
                color = ST_COLOR.get(p.get("status","normal"), "#00ff88")
                emoji = ST_EMOJI.get(p.get("status","normal"), "🟢")
                slbl  = ST_LABEL.get(p.get("status","normal"), "Normal")
                nr    = p.get("normal_range","")
                st.markdown(f"""
                <div class="di-param">
                  <div class="di-dot" style="background:{color};box-shadow:0 0 7px {color}55;"></div>
                  <div class="di-pname">{p['name']}</div>
                  <div style="text-align:right">
                    <span class="di-pval">{p['value']}</span>
                    <span class="di-punit">{p.get('unit','')}</span>
                    <div class="di-prange">{emoji} {slbl}{'  ·  Ref: ' + nr if nr else ''}</div>
                  </div>
                </div>""", unsafe_allow_html=True)

        with col_c:
            st.markdown("**Visual Comparison — Value vs. Reference Range**")
            if HAS_PLOTLY:
                # Parse normal ranges to draw reference lines
                def _parse_range(nr_str):
                    m = __import__("re").findall(r"[\d.]+", nr_str)
                    if len(m) >= 2:
                        return float(m[0]), float(m[1])
                    return None, None

                # Gauge chart per parameter
                for p in params:
                    try:
                        val = float(p["value"])
                    except (ValueError, TypeError):
                        continue
                    lo, hi = _parse_range(p.get("normal_range",""))
                    clr = ST_COLOR.get(p.get("status","normal"), "#00ff88")

                    if lo is not None and hi is not None:
                        # Gauge chart showing value vs range
                        gauge_max = max(hi * 1.6, val * 1.2)
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=val,
                            title={"text": p["name"], "font": {"size": 12, "color": "#e8f4f8"}},
                            number={"suffix": f" {p.get('unit','')}", "font": {"size": 14, "color": clr}},
                            gauge={
                                "axis": {
                                    "range": [0, gauge_max],
                                    "tickfont": {"size": 9, "color": "#7a9ab5"},
                                    "tickcolor": "#7a9ab5",
                                },
                                "bar": {"color": clr, "thickness": 0.28},
                                "bgcolor": "#0f1f38",
                                "borderwidth": 0,
                                "steps": [
                                    {"range": [0, lo],  "color": "rgba(255,71,87,0.15)"},
                                    {"range": [lo, hi], "color": "rgba(0,255,136,0.12)"},
                                    {"range": [hi, gauge_max], "color": "rgba(255,71,87,0.15)"},
                                ],
                                "threshold": {
                                    "line": {"color": "#00d4ff", "width": 2},
                                    "thickness": 0.75,
                                    "value": val,
                                },
                            },
                        ))
                        fig.update_layout(
                            height=180, margin=dict(l=20, r=20, t=40, b=10),
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            font_color="#e8f4f8",
                        )
                        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                    else:
                        # Simple horizontal bar if no range available
                        fig = go.Figure(go.Bar(
                            x=[val], y=[p["name"]],
                            orientation="h",
                            marker_color=clr,
                            marker_line_width=0,
                            text=[f"{val} {p.get('unit','')}"],
                            textposition="inside",
                            insidetextanchor="middle",
                        ))
                        fig.update_layout(
                            height=60, margin=dict(l=0,r=0,t=0,b=0),
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            xaxis={"showgrid":False,"visible":False},
                            yaxis={"showgrid":False,"tickfont":{"color":"#e8f4f8","size":11}},
                            showlegend=False,
                        )
                        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            else:
                # Fallback basic chart
                import pandas as pd
                chartable = [{"Parameter": p["name"], "Value": float(p["value"])} for p in params if _safe_float(p["value"])]
                if chartable:
                    df = pd.DataFrame(chartable).set_index("Parameter")
                    st.bar_chart(df, color="#00d4ff")

        # ── AI Analysis ─────────────────────────────────────────
        st.markdown("**🤖 AI Health Insight (powered by Gemini)**")
        if st.button("✨ Generate AI Analysis", type="primary", key="di_ai_btn"):
            st.session_state.di_ai_text = ""
            with st.spinner("🧠 Gemini is analysing your report..."):
                t = _consume_sse(f"{BASE_URL}/data-insights/reports/{rep_id}/analysis")
                st.session_state.di_ai_text = t

        if st.session_state.di_ai_text:
            st.markdown(f"""
            <div class="di-ai">
              <div class="di-ai-hdr">
                <div class="di-ai-av">🤖</div>
                <div style="font-family:'Syne',sans-serif;font-weight:700;color:#e8f4f8;font-size:.9rem;">
                  Gemini AI Health Insight</div>
              </div>
              <div class="di-ai-text">{st.session_state.di_ai_text}</div>
              <div class="di-disc">⚠️ AI-generated for educational purposes only.
                Always consult a qualified healthcare professional for medical advice.</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="di-empty">
          <div class="di-empty-icon">🔬</div>
          <h3>No parameters extracted</h3>
          <p>Click <b>🔄 Re-analyze parameters</b> above to fix this report,<br>
          or delete it and re-upload for best results.</p>
        </div>""", unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="di-empty">
      <div class="di-empty-icon">📂</div>
      <h3>No report loaded</h3>
      <p>Upload a report above or select one from the dropdown.</p>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════
#  SECTION 4 — COMPARE + MANAGE
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="di-sec">🔄 Compare &amp; Manage Reports</div>', unsafe_allow_html=True)

tab_cmp, tab_mgmt = st.tabs(["📊 Compare Reports", "🗂 My Reports"])

# ── COMPARE ────────────────────────────────────────────────────
with tab_cmp:
    from collections import defaultdict
    by_type = defaultdict(list)
    for r in all_reports:
        by_type[r["report_type"]].append(r)
    comparable = {t: rs for t, rs in by_type.items() if len(rs) >= 2}

    if comparable:
        t_choice = st.selectbox(
            "Select report type:", list(comparable.keys()),
            format_func=lambda k: next((r["report_label"] for r in all_reports if r["report_type"]==k), k),
            key="di_cmp_type",
        )
        same = comparable[t_choice]
        lmap = {f"#{r['id']} · {r.get('upload_date','')[:10]}": r["id"] for r in same}
        lkeys = list(lmap.keys())
        ca, cb = st.columns(2)
        with ca: r1_l = st.selectbox("Report A:", lkeys, key="di_r1")
        with cb: r2_l = st.selectbox("Report B:", lkeys[::-1], key="di_r2")
        r1_id, r2_id = lmap[r1_l], lmap[r2_l]

        if r1_id == r2_id:
            st.warning("Choose two different reports.")
        else:
            if st.button("🔄 Compare Now", type="primary", key="di_cmp_btn"):
                st.session_state.di_compare_deltas = []
                st.session_state.di_compare_text = ""
                with st.spinner("Comparing..."):
                    d, t = _consume_sse_compare(
                        f"{BASE_URL}/data-insights/reports/compare?report_id_1={r1_id}&report_id_2={r2_id}"
                    )
                    st.session_state.di_compare_deltas = d
                    st.session_state.di_compare_text = t

            if st.session_state.di_compare_deltas:
                st.markdown("#### Parameter Δ Changes")
                # Plotly grouped bar chart
                if HAS_PLOTLY and st.session_state.di_compare_deltas:
                    ds = st.session_state.di_compare_deltas
                    names   = [d["name"] for d in ds]
                    older_v = []
                    newer_v = []
                    for d in ds:
                        try: older_v.append(float(d["older_value"]))
                        except: older_v.append(0)
                        try: newer_v.append(float(d["newer_value"]))
                        except: newer_v.append(0)

                    fig = go.Figure()
                    fig.add_trace(go.Bar(name="Previous", x=names, y=older_v,
                                         marker_color="rgba(123,94,167,0.7)", marker_line_width=0))
                    fig.add_trace(go.Bar(name="Current",  x=names, y=newer_v,
                                         marker_color="rgba(0,212,255,0.8)", marker_line_width=0))
                    fig.update_layout(
                        barmode="group", height=340,
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font_color="#e8f4f8", font_size=11,
                        legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#e8f4f8"),
                        xaxis=dict(tickfont=dict(color="#7a9ab5")),
                        yaxis=dict(tickfont=dict(color="#7a9ab5"), gridcolor="rgba(255,255,255,0.05)"),
                        margin=dict(l=0,r=0,t=10,b=0),
                    )
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

                for d in st.session_state.di_compare_deltas:
                    arrow = {"up":"↑","down":"↓","stable":"→"}.get(d["trend"],"→")
                    color = d.get("color","#7a9ab5")
                    pct = d.get("pct_change",0)
                    st.markdown(f"""
                    <div class="di-delta">
                      <div class="di-delta-name">{d['name']} <span style="color:#7a9ab5;font-size:.72rem;">{d.get('unit','')}</span></div>
                      <div class="di-delta-row">
                        <span style="color:#7a9ab5">{d['older_value']}</span>
                        <span style="color:{color};font-weight:700;font-size:1rem;">{arrow}</span>
                        <span style="color:#e8f4f8;font-weight:700;">{d['newer_value']}</span>
                        <span style="background:{color}22;color:{color};padding:.1rem .45rem;border-radius:50px;
                              font-size:.68rem;font-family:'Syne',sans-serif;font-weight:700;">
                          {'+' if pct>0 else ''}{pct}% {arrow}</span>
                      </div>
                    </div>""", unsafe_allow_html=True)

            if st.session_state.di_compare_text:
                st.markdown(f"""
                <div class="di-ai" style="margin-top:.8rem;">
                  <div class="di-ai-hdr">
                    <div class="di-ai-av">🤖</div>
                    <div style="font-family:'Syne',sans-serif;font-weight:700;color:#e8f4f8;font-size:.9rem;">AI Comparison Summary</div>
                  </div>
                  <div class="di-ai-text">{st.session_state.di_compare_text}</div>
                  <div class="di-disc">⚠️ AI-generated. Consult a doctor for clinical interpretation.</div>
                </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="di-empty">
          <div class="di-empty-icon">📊</div>
          <h3>Need 2+ same-type reports</h3>
          <p>Upload at least 2 reports of the same type to compare.</p>
        </div>""", unsafe_allow_html=True)

# ── MANAGE ────────────────────────────────────────────────────
with tab_mgmt:
    if all_reports:
        st.markdown(f"📋 **{len(all_reports)} report(s)**")
        for rep in all_reports:
            cc = CONF_CLS.get(rep.get("confidence","low"), "di-badge-low-conf")
            pc = len(rep.get("parameters") or [])
            color_by_type = {"lipid_profile":"#7b5ea7","cbc":"#00d4ff","glucose":"#ff6b9d",
                             "thyroid":"#ffa502","liver_function":"#00ff88","kidney_function":"#ff4757",
                             "vitamins":"#00d4ff","blood_pressure":"#ff6b9d","hydration":"#00d4ff"
                             }.get(rep.get("report_type",""), "#00d4ff")
            st.markdown(f"""
            <div class="di-rcard" style="border-left-color:{color_by_type};">
              <div style="font-size:1.5rem;">📄</div>
              <div class="di-rcard-info">
                <div class="di-rcard-name">{rep.get('report_label') or rep.get('report_type','Unknown')}</div>
                <div class="di-rcard-sub">
                  {rep.get('file_name','')}  ·  {rep.get('upload_date','')[:16]}
                  ·  <b>{pc}</b> parameters
                </div>
              </div>
              <span class="di-pstatus {cc}">{(rep.get('confidence') or 'low').upper()}</span>
            </div>""", unsafe_allow_html=True)

            c1,c2,c3 = st.columns([3,1,1])
            with c2:
                if st.button("👁 View", key=f"v_{rep['id']}", use_container_width=True):
                    st.session_state.di_selected_report = rep
                    st.session_state.di_ai_text = ""
                    st.rerun()
            with c3:
                if st.button("🗑 Delete", key=f"d_{rep['id']}", use_container_width=True):
                    st.session_state.di_delete_confirm = rep["id"]

            if st.session_state.di_delete_confirm == rep["id"]:
                st.warning(f"⚠️ Delete **{rep.get('report_label','this report')}**?")
                cc1,cc2 = st.columns(2)
                with cc1:
                    if st.button("✅ Confirm", key=f"conf_{rep['id']}", type="primary"):
                        dr = api_delete(f"/data-insights/reports/{rep['id']}")
                        if dr and dr.status_code == 200:
                            st.success("Deleted.")
                            if st.session_state.di_selected_report and \
                               st.session_state.di_selected_report.get("id") == rep["id"]:
                                st.session_state.di_selected_report = None
                            st.session_state.di_delete_confirm = None
                            st.cache_data.clear()
                            st.rerun()
                        else: st.error("Delete failed.")
                with cc2:
                    if st.button("❌ Cancel", key=f"canc_{rep['id']}"):
                        st.session_state.di_delete_confirm = None
                        st.rerun()
    else:
        st.markdown("""
        <div class="di-empty">
          <div class="di-empty-icon">📂</div>
          <h3>No reports yet</h3>
          <p>Upload your first health report above.</p>
        </div>""", unsafe_allow_html=True)


# helper used in fallback chart section above
def _safe_float(v):
    try: float(v); return True
    except: return False
