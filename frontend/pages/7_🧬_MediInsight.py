# ============================================================
#  pages/7_🧬_MediInsight.py  — MediInsight UI
# ============================================================
import re
import streamlit as st
import requests
import plotly.graph_objects as go

st.set_page_config(page_title="MediInsight", page_icon="🧬", layout="wide")

if "access_token" not in st.session_state: st.session_state.access_token = None
if "user_name"    not in st.session_state: st.session_state.user_name    = None

try:
    from utils import BASE_URL, require_login
    require_login()
except Exception:
    BASE_URL = "http://localhost:8000"
    if not st.session_state.access_token:
        st.warning("Please log in first.")
        st.stop()

for k, v in {
    "mi_report_id": None, "mi_result": None,
    "mi_comparison": None, "mi_history": []
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

def hdrs():
    return {"Authorization": f"Bearer {st.session_state.get('access_token', '')}"}

def api(method, path, **kw):
    try:
        return getattr(requests, method)(f"{BASE_URL}{path}", headers=hdrs(), timeout=120, **kw)
    except:
        return None

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@400;500;600&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif!important}

.hero{background:linear-gradient(135deg,#0c2340,#1a6db0);border-radius:18px;padding:28px 36px;margin-bottom:24px;color:#fff}
.hero h1{font-family:'Playfair Display',serif;font-size:2rem;margin:0}
.hero p{color:rgba(255,255,255,.65);margin:6px 0 0;font-size:.9rem}

.slabel{font-size:.7rem;font-weight:700;letter-spacing:1.8px;text-transform:uppercase;color:#164f87;margin-bottom:10px}

/* Status badges */
.bn{background:#e5f7ed;color:#0a6b35;border:1px solid #7fcca0;border-radius:6px;padding:3px 10px;font-size:.75rem;font-weight:700}
.bh{background:#fff1e5;color:#b84a00;border:1px solid #f0ae70;border-radius:6px;padding:3px 10px;font-size:.75rem;font-weight:700}
.bl{background:#fce8e8;color:#b80000;border:1px solid #f08080;border-radius:6px;padding:3px 10px;font-size:.75rem;font-weight:700}
.bb{background:#fffae5;color:#7a6000;border:1px solid #e0c840;border-radius:6px;padding:3px 10px;font-size:.75rem;font-weight:700}
.bu{background:#f0f0f0;color:#555;border:1px solid #ccc;border-radius:6px;padding:3px 10px;font-size:.75rem;font-weight:700}

/* Parameter table */
.ptable{width:100%;border-collapse:collapse;font-size:.86rem}
.ptable th{background:rgba(12,35,64,.06);color:#0c2340;padding:11px 14px;text-align:left;
           font-size:.7rem;letter-spacing:1px;text-transform:uppercase;
           border-bottom:2px solid rgba(26,109,176,.2)}
.ptable td{padding:11px 14px;border-bottom:1px solid rgba(26,109,176,.1);
           vertical-align:middle;line-height:1.5}
.ptable tr:hover td{background:rgba(26,109,176,.04)}
.ptable td.pname{font-weight:600;color:#0c2340}
.ptable td.pval{font-weight:600;font-size:.95rem}
.ptable td.pnote{font-size:.8rem;color:#5a7a9a;line-height:1.4}

/* Trend badges */
.t-up  {color:#0a6b35;font-weight:700;font-size:.9rem}
.t-dn  {color:#b80000;font-weight:700;font-size:.9rem}
.t-st  {color:#b86a00;font-weight:700;font-size:.9rem}

/* Status stat boxes */
.stat-box{text-align:center;padding:16px 10px;border-radius:12px;margin:4px}

/* Disclaimer */
.disc{background:#fffde7;border:1px solid #f9cc40;border-radius:10px;
      padding:12px 16px;color:#6b4f00;font-size:.83rem;margin-top:16px}

/* Buttons */
div.stButton>button{
    background:linear-gradient(135deg,#0c2340,#1a6db0)!important;
    color:#fff!important;border:none!important;
    border-radius:10px!important;font-weight:600!important}
div.stButton>button:hover{opacity:.88!important}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🧬 MediInsight</h1>
  <p>Hybrid AI lab report analysis · Tavily web intelligence + Gemini 2.5 Flash · Interactive charts</p>
</div>""", unsafe_allow_html=True)

left, right = st.columns([1, 2], gap="large")

# ════════════════════════════════════
#  LEFT PANEL — Upload + History
# ════════════════════════════════════
with left:
    st.markdown('<div class="slabel">👤 Patient Context</div>', unsafe_allow_html=True)
    whose    = st.selectbox("Whose report?", ["Myself", "Family Member"])
    relation = ""
    if whose == "Family Member":
        rel_opt  = st.selectbox("Relationship", ["Father","Mother","Brother","Sister","Grandfather","Grandmother","Other"])
        relation = st.text_input("Specify") if rel_opt == "Other" else rel_opt
    gender = st.selectbox("Gender (for reference ranges)", ["general", "male", "female"])

    st.markdown("---")
    st.markdown('<div class="slabel">📤 Upload Report</div>', unsafe_allow_html=True)
    uploaded    = st.file_uploader("PDF or TXT", type=["pdf", "txt"])
    report_type = st.selectbox("Report Type", ["— select —",
        "CBC (Complete Blood Count)", "Liver Function Test (LFT)",
        "Renal Function Test (RFT)", "Lipid Profile", "Thyroid Function Test",
        "Blood Glucose / HbA1c", "Electrolyte Panel", "ESR / CRP", "Iron Studies",
    ])

    if st.button("🔬 Upload & Analyse", use_container_width=True):
        if not uploaded:
            st.error("Please select a file.")
        elif report_type == "— select —":
            st.error("Please select a report type.")
        else:
            with st.spinner("📤 Uploading…"):
                up = api("post", "/mediinsight/upload",
                         files={"file": (uploaded.name, uploaded, uploaded.type)},
                         data={"report_type": report_type, "whose": whose,
                               "relation": relation, "gender": gender})
            if not up or not up.ok:
                st.error(up.json().get("detail", "Upload failed") if up else "Cannot reach server.")
            else:
                rid = up.json()["report_id"]
                st.session_state.mi_report_id = rid
                with st.spinner("🤖 Running 7-step AI analysis… (30–60s)"):
                    _tok = st.session_state.get("access_token", "")
                    ar   = requests.post(
                        f"{BASE_URL}/mediinsight/{rid}/analyze",
                        headers={"Authorization": f"Bearer {_tok}"},
                        data={"whose": whose, "relation": relation, "gender": gender},
                        timeout=180,
                    )
                if ar and ar.ok:
                    st.session_state.mi_result     = ar.json()
                    st.session_state.mi_comparison = None
                    h = api("get", "/mediinsight/history")
                    if h and h.ok: st.session_state.mi_history = h.json()
                    st.success("✅ Analysis complete!")
                    st.rerun()
                else:
                    st.error(ar.json().get("detail", "Analysis failed") if ar else "Server error.")

    # ── History ───────────────────────────────────────────────
    st.markdown("---")
    hc1, hc2 = st.columns([4, 1])
    with hc1: st.markdown('<div class="slabel">📁 Report History</div>', unsafe_allow_html=True)
    with hc2:
        if st.button("↻", key="ref_hist"):
            h = api("get", "/mediinsight/history")
            if h and h.ok: st.session_state.mi_history = h.json()

    if not st.session_state.mi_history:
        h = api("get", "/mediinsight/history")
        if h and h.ok: st.session_state.mi_history = h.json()

    if not st.session_state.mi_history:
        st.caption("No reports uploaded yet.")

    for item in st.session_state.mi_history:
        icon   = "✅" if item["status"] == "processed" else "⏳"
        hcol, dcol = st.columns([5, 1])
        with hcol:
            label = f"{icon} {item['report_type']} · {item['upload_date'][:10]}"
            if st.button(label, key=f"h_{item['id']}", use_container_width=True):
                with st.spinner("Loading…"):
                    r = api("get", f"/mediinsight/{item['id']}/results")
                if r and r.ok:
                    d = r.json()
                    st.session_state.mi_report_id  = item["id"]
                    st.session_state.mi_result     = {
                        "report_type":    d.get("report_type", ""),
                        "parameters":     d.get("parameters", []),
                        "chart_data":     d.get("chart_data", []),
                        "summary":        d.get("summary"),
                        "disclaimer":     d.get("disclaimer", ""),
                        "scraped_sources":d.get("rag_sources", []),
                        "tavily_used":    d.get("tavily_used", False),
                        "model_used":     "gemini-2.5-flash",
                        "subject":        "",
                        "patient_context":{},
                    }
                    st.session_state.mi_comparison = None
                    st.rerun()
        with dcol:
            if st.button("🗑️", key=f"del_{item['id']}", help="Delete"):
                dr = api("delete", f"/mediinsight/{item['id']}")
                if dr and dr.ok:
                    if st.session_state.mi_report_id == item["id"]:
                        st.session_state.mi_report_id  = None
                        st.session_state.mi_result     = None
                        st.session_state.mi_comparison = None
                    h = api("get", "/mediinsight/history")
                    if h and h.ok: st.session_state.mi_history = h.json()
                    st.rerun()
                else:
                    st.error("Delete failed.")

# ════════════════════════════════════
#  RIGHT PANEL — Results
# ════════════════════════════════════
with right:
    result = st.session_state.mi_result

    if not result:
        st.markdown("""
        <div style="text-align:center;padding:70px 20px;opacity:.5">
          <div style="font-size:4rem">🔬</div>
          <div style="font-size:1.1rem;font-weight:600;color:#164f87;margin-top:14px">
            Upload a report to get started
          </div>
          <div style="color:#5a7a9a;font-size:.87rem;margin-top:6px">
            AI-powered analysis · Parameter charts · Report comparison
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        tab1, tab2, tab3, tab4 = st.tabs([
            "📋 Summary", "🔬 Parameters", "📊 Charts", "📈 Comparison"
        ])

        # ════════════════════════════════════════
        #  TAB 1 — SUMMARY (clean, no causes/sources)
        # ════════════════════════════════════════
        with tab1:
            s    = result.get("summary") or {}
            ctx  = result.get("patient_context", {})
            who  = ctx.get("whose", "") or ""
            rel  = ctx.get("relation", "") or ""
            subj = result.get("subject", "") or (f"{rel} ({who})" if rel else who)

            # Metrics row
            c1, c2, c3 = st.columns(3)
            c1.metric("Report Type",  result.get("report_type", "—"))
            c2.metric("AI Model",     result.get("model_used", "gemini-2.5-flash"))
            c3.metric("Data Source",  "🌐 Tavily + Gemini" if result.get("tavily_used") else "🤖 Gemini AI")

            if subj:
                st.markdown(f"**👤 Patient:** {subj}")
            st.markdown("---")

            # Overall summary
            st.markdown("**📝 Overall Summary**")
            summary_text = s.get("overall_summary", "")
            if summary_text:
                st.info(summary_text)
            else:
                st.warning("Summary not available. Try re-analysing the report.")

            # Abnormal findings only
            findings = s.get("abnormal_findings", [])
            if findings:
                st.markdown("**⚠️ Abnormal Findings**")
                for f in findings:
                    st.markdown(
                        f'<div style="padding:6px 0 6px 14px;border-left:3px solid #f08080;'
                        f'color:#b80000;font-size:.9rem;margin:4px 0">🔴 {f}</div>',
                        unsafe_allow_html=True)

            # Recommendation
            rec = s.get("recommendation", "")
            if rec:
                st.success(f"💡 **Recommendation:** {rec}")

            st.markdown(
                f'<div class="disc">⚕️ {result.get("disclaimer", "MediInsight provides educational insights only. Always consult a qualified physician.")}</div>',
                unsafe_allow_html=True)

        # ════════════════════════════════════════
        #  TAB 2 — PARAMETERS (full rich table)
        # ════════════════════════════════════════
        with tab2:
            params = result.get("parameters", [])
            if not params:
                st.info("No parameters extracted. Try re-analysing the report.")
            else:
                def badge(status):
                    cls = {"Normal":"bn","High":"bh","Low":"bl","Borderline":"bb"}.get(status,"bu")
                    sym = {"Normal":"✔ Normal","High":"▲ High","Low":"▼ Low",
                           "Borderline":"~ Borderline"}.get(status, status)
                    return f'<span class="{cls}">{sym}</span>'

                # Summary stats row
                total    = len(params)
                abnormal = [p for p in params if p["status"] in ("High","Low","Borderline")]
                normal   = [p for p in params if p["status"] == "Normal"]
                unknown  = [p for p in params if p["status"] == "Unknown"]

                sc1,sc2,sc3,sc4 = st.columns(4)
                sc1.metric("Total",    total)
                sc2.metric("🔴 Abnormal", len(abnormal))
                sc3.metric("✅ Normal",   len(normal))
                sc4.metric("❓ Unknown",  len(unknown))

                st.markdown("")

                # Full parameter table
                rows_html = ""
                for i, p in enumerate(params):
                    bg   = "rgba(26,109,176,.03)" if i % 2 == 0 else "transparent"
                    stat = p.get("status", "Unknown")
                    # Highlight abnormal rows
                    if stat == "High":   bg = "rgba(184,74,0,.05)"
                    elif stat == "Low":  bg = "rgba(184,0,0,.05)"
                    note = p.get("significance", "")
                    rows_html += f"""<tr style="background:{bg}">
                      <td class="pname" style="padding:11px 14px">{p.get("name","")}</td>
                      <td class="pval"  style="padding:11px 14px">{p.get("raw_value","")}</td>
                      <td style="padding:11px 14px;color:#5a7a9a;font-size:.85rem">{p.get("normal_range","—")}</td>
                      <td style="padding:11px 14px">{badge(stat)}</td>
                      <td class="pnote" style="padding:11px 14px">{note}</td>
                    </tr>"""

                st.markdown(f"""
                <div style="overflow-x:auto;border-radius:12px;border:1px solid rgba(26,109,176,.15)">
                <table class="ptable">
                  <thead><tr>
                    <th>Parameter</th>
                    <th>Your Value</th>
                    <th>Normal Range</th>
                    <th>Status</th>
                    <th>Clinical Note</th>
                  </tr></thead>
                  <tbody>{rows_html}</tbody>
                </table></div>""", unsafe_allow_html=True)

                st.markdown(
                    f'<div class="disc">⚕️ {result.get("disclaimer","Educational only.")}</div>',
                    unsafe_allow_html=True)

        # ════════════════════════════════════════
        #  TAB 3 — CHARTS
        # ════════════════════════════════════════
        with tab3:
            params_all = result.get("parameters", [])
            chart_data = result.get("chart_data", [])

            # Build chart_data from parameters if empty
            if not chart_data and params_all:
                import re as _re
                for p in params_all:
                    nr   = p.get("normal_range", "")
                    nums = _re.findall(r"[\d.]+", nr)
                    lo = hi = None
                    if nr.startswith("<") and nums:    lo, hi = 0.0,           float(nums[0])
                    elif nr.startswith(">") and nums:  lo, hi = float(nums[0]), float(nums[0])*2
                    elif len(nums) >= 2:               lo, hi = float(nums[0]), float(nums[1])
                    if lo is not None and hi is not None:
                        try:
                            val = float(p.get("value", 0))
                            if val >= 0:
                                chart_data.append({
                                    "name":        p.get("name",""),
                                    "value":       val,
                                    "unit":        p.get("unit",""),
                                    "normal_low":  lo,
                                    "normal_high": hi,
                                    "status":      p.get("status","Unknown"),
                                })
                        except Exception:
                            pass

            SCOLORS = {
                "Normal":    "#22c55e",
                "High":      "#f97316",
                "Low":       "#ef4444",
                "Borderline":"#eab308",
                "Unknown":   "#94a3b8",
            }

            if not params_all:
                st.info("No parameters found. Re-analyse the report first.")
            else:
                # ── 1. STATUS DONUT ───────────────────────────────
                status_counts = {}
                for p in params_all:
                    s = p.get("status","Unknown")
                    status_counts[s] = status_counts.get(s,0) + 1

                col_d, col_s = st.columns([1, 1])

                with col_d:
                    labels = list(status_counts.keys())
                    vals_d = list(status_counts.values())
                    colors = [SCOLORS.get(l,"#94a3b8") for l in labels]
                    total_p = sum(vals_d)

                    donut = go.Figure(go.Pie(
                        labels=labels, values=vals_d,
                        hole=0.65,
                        marker=dict(colors=colors,
                                    line=dict(color="rgba(255,255,255,0.15)", width=2)),
                        textinfo="label+percent",
                        textfont=dict(size=12, color="white"),
                        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
                    ))
                    donut.add_annotation(
                        text=f"<b>{total_p}</b><br><span style='font-size:11px'>Parameters</span>",
                        x=0.5, y=0.5, font=dict(size=18, color="#0c2340"),
                        showarrow=False,
                    )
                    donut.update_layout(
                        title=dict(text="Status Overview",
                                   font=dict(size=14, color="#0c2340"), x=0.5),
                        showlegend=True,
                        legend=dict(orientation="h", y=-0.15, x=0.5,
                                    xanchor="center", font=dict(size=11)),
                        margin=dict(t=50, b=40, l=10, r=10),
                        height=300,
                        paper_bgcolor="rgba(0,0,0,0)",
                    )
                    st.plotly_chart(donut, use_container_width=True)

                # ── 2. STATUS BREAKDOWN CARDS ─────────────────────
                with col_s:
                    st.markdown("<br>", unsafe_allow_html=True)
                    for stat, count in sorted(status_counts.items(),
                                              key=lambda x: ["High","Low","Borderline","Normal","Unknown"].index(x[0]) if x[0] in ["High","Low","Borderline","Normal","Unknown"] else 99):
                        clr  = SCOLORS.get(stat,"#94a3b8")
                        icon = {"Normal":"✅","High":"🔺","Low":"🔻","Borderline":"⚠️","Unknown":"❓"}.get(stat,"•")
                        pct  = round(count/total_p*100)
                        st.markdown(
                            f'<div style="display:flex;align-items:center;gap:12px;'
                            f'padding:10px 16px;border-radius:10px;margin:6px 0;'
                            f'background:{clr}18;border-left:4px solid {clr}">'
                            f'<span style="font-size:1.2rem">{icon}</span>'
                            f'<div style="flex:1">'
                            f'<div style="font-weight:700;color:{clr};font-size:.9rem">{stat}</div>'
                            f'<div style="font-size:.75rem;color:#64748b">{count} parameter{"s" if count>1 else ""}</div>'
                            f'</div>'
                            f'<div style="font-size:1.1rem;font-weight:700;color:{clr}">{pct}%</div>'
                            f'</div>',
                            unsafe_allow_html=True)

                st.markdown("---")

                # ── 3. HORIZONTAL BAR CHART (cleaner than vertical) ──
                if chart_data:
                    st.markdown("**📊 Values vs Normal Range**")

                    # Sort: abnormal first, then normal
                    sorted_cd = sorted(
                        chart_data,
                        key=lambda x: {"High":0,"Low":1,"Borderline":2,"Normal":3,"Unknown":4}.get(x.get("status",""),5)
                    )

                    # Paginate if > 10
                    PAGE_SIZE = 10
                    total_cd  = len(sorted_cd)
                    if total_cd > PAGE_SIZE:
                        pages = [f"Page {i+1} ({sorted_cd[i*PAGE_SIZE]['name']} — {sorted_cd[min((i+1)*PAGE_SIZE-1, total_cd-1)]['name']})"
                                 for i in range(0, (total_cd+PAGE_SIZE-1)//PAGE_SIZE)]
                        page    = st.selectbox("Select page", pages, key="cpage")
                        pidx    = pages.index(page)
                        cd_show = sorted_cd[pidx*PAGE_SIZE:(pidx+1)*PAGE_SIZE]
                    else:
                        cd_show = sorted_cd

                    names  = [c["name"]       for c in cd_show]
                    vals   = [c["value"]      for c in cd_show]
                    lo     = [c["normal_low"] for c in cd_show]
                    hi     = [c["normal_high"]for c in cd_show]
                    units  = [c.get("unit","")for c in cd_show]
                    status = [c.get("status","Normal") for c in cd_show]
                    bcolors= [SCOLORS.get(s,"#94a3b8") for s in status]

                    fig = go.Figure()

                    # Green normal range band as background bars
                    fig.add_trace(go.Bar(
                        name="Normal Range",
                        y=names,
                        x=[h-l for l,h in zip(lo,hi)],
                        base=lo,
                        orientation="h",
                        marker=dict(color="rgba(34,197,94,0.15)",
                                    line=dict(color="rgba(34,197,94,0.4)",width=1)),
                        hovertemplate="Normal: %{base:.1f}–%{x:.1f}<extra>Normal Range</extra>",
                        showlegend=True,
                    ))

                    # Actual value dots
                    fig.add_trace(go.Scatter(
                        name="Your Value",
                        y=names,
                        x=vals,
                        mode="markers+text",
                        marker=dict(
                            color=bcolors,
                            size=14,
                            line=dict(color="white", width=2),
                            symbol="diamond",
                        ),
                        text=[f"  {v} {u}" for v,u in zip(vals,units)],
                        textposition="middle right",
                        textfont=dict(size=11, color="#0c2340"),
                        hovertemplate="<b>%{y}</b><br>Value: %{x}<extra></extra>",
                    ))

                    fig.update_layout(
                        barmode="overlay",
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="DM Sans", size=12, color="#1a2b3c"),
                        xaxis=dict(showgrid=True,
                                   gridcolor="rgba(100,116,139,0.15)",
                                   zeroline=False,
                                   title="Value"),
                        yaxis=dict(showgrid=False,
                                   autorange="reversed",
                                   tickfont=dict(size=11)),
                        legend=dict(orientation="h", y=1.05, x=0,
                                    font=dict(size=11)),
                        margin=dict(t=30, b=40, l=180, r=120),
                        height=max(300, len(cd_show)*38 + 80),
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    st.markdown("---")

                    # ── 4. GAUGE CHARTS for abnormal params ─────────
                    abnormal_cd = [c for c in chart_data
                                   if c.get("status") in ("High","Low","Borderline")]
                    if abnormal_cd:
                        st.markdown("**🎯 Abnormal Parameters at a Glance**")
                        n = min(6, len(abnormal_cd))
                        for row_i in range(0, n, 3):
                            row_items = abnormal_cd[row_i:row_i+3]
                            gcols     = st.columns(len(row_items))
                            for gi, ac in enumerate(row_items):
                                lo_v = ac["normal_low"]
                                hi_v = ac["normal_high"]
                                val  = ac["value"]
                                rng  = max(hi_v - lo_v, 0.1)
                                pad  = rng * 0.5
                                ax_min = max(0, lo_v - pad)
                                ax_max = hi_v + pad
                                sc   = SCOLORS.get(ac["status"],"#94a3b8")

                                gauge = go.Figure(go.Indicator(
                                    mode="gauge+number+delta",
                                    value=val,
                                    delta=dict(
                                        reference=(lo_v+hi_v)/2,
                                        valueformat=".2f",
                                        increasing=dict(color="#f97316"),
                                        decreasing=dict(color="#ef4444"),
                                    ),
                                    number=dict(
                                        suffix=f" {ac.get('unit','')}",
                                        font=dict(size=20, color=sc),
                                    ),
                                    title=dict(
                                        text=f"<b>{ac['name']}</b><br>"
                                             f"<span style='font-size:11px;color:#64748b'>"
                                             f"Normal: {lo_v:.1f}–{hi_v:.1f}</span>",
                                        font=dict(size=12),
                                    ),
                                    gauge=dict(
                                        axis=dict(range=[ax_min, ax_max],
                                                  tickfont=dict(size=9),
                                                  nticks=5),
                                        bar=dict(color=sc, thickness=0.7),
                                        bgcolor="rgba(0,0,0,0)",
                                        borderwidth=0,
                                        steps=[
                                            dict(range=[ax_min, lo_v],  color="rgba(239,68,68,0.1)"),
                                            dict(range=[lo_v,   hi_v],  color="rgba(34,197,94,0.15)"),
                                            dict(range=[hi_v,   ax_max],color="rgba(249,115,22,0.1)"),
                                        ],
                                        threshold=dict(
                                            line=dict(color=sc, width=3),
                                            thickness=0.85, value=val,
                                        ),
                                    ),
                                ))
                                gauge.update_layout(
                                    height=240,
                                    margin=dict(t=60, b=20, l=20, r=20),
                                    paper_bgcolor="rgba(0,0,0,0)",
                                )
                                with gcols[gi]:
                                    st.plotly_chart(gauge, use_container_width=True)

                else:
                    # No numeric ranges — show a simple bar chart of raw values by status color
                    if params_all:
                        st.markdown("**📊 Parameter Values**")
                        pnames = [p["name"][:20]  for p in params_all if p.get("value")]
                        pvals  = [p["value"]       for p in params_all if p.get("value")]
                        pclrs  = [SCOLORS.get(p.get("status","Unknown"),"#94a3b8")
                                  for p in params_all if p.get("value")]
                        if pnames:
                            fig_s = go.Figure(go.Bar(
                                x=pnames, y=pvals,
                                marker_color=pclrs,
                                text=pvals, textposition="outside",
                            ))
                            fig_s.update_layout(
                                plot_bgcolor="rgba(0,0,0,0)",
                                paper_bgcolor="rgba(0,0,0,0)",
                                height=350,
                                xaxis_tickangle=-35,
                                margin=dict(t=20,b=80,l=40,r=20),
                                font=dict(family="DM Sans"),
                            )
                            st.plotly_chart(fig_s, use_container_width=True)

                st.markdown(
                    f'<div class="disc">⚕️ {result.get("disclaimer","Educational only.")}</div>',
                    unsafe_allow_html=True)

        # ════════════════════════════════════════
        #  TAB 4 — COMPARISON
        # ════════════════════════════════════════
        with tab4:
            cur_id   = st.session_state.mi_report_id
            cur_type = result.get("report_type", "")
            history  = st.session_state.mi_history
            same     = [h for h in history
                        if h["id"] != cur_id and h.get("report_type","") == cur_type]

            if not same:
                st.info("📂 Upload another report of the same type to enable comparison.")
            else:
                opts    = {f"{h['report_type']} · {h['upload_date'][:10]}": h["id"] for h in same}
                chosen  = st.selectbox("Select previous report to compare with current", list(opts.keys()))
                prev_id = opts[chosen]

                if st.button("📊 Run Comparison", use_container_width=True):
                    with st.spinner("Comparing reports…"):
                        _tok = st.session_state.get("access_token", "")
                        cr   = requests.post(
                            f"{BASE_URL}/mediinsight/compare",
                            headers={"Authorization": f"Bearer {_tok}"},
                            data={"current_report_id": cur_id,
                                  "previous_report_id": prev_id},
                            timeout=60,
                        )
                    if cr and cr.ok:
                        st.session_state.mi_comparison = cr.json()
                        st.rerun()
                    else:
                        st.error(cr.json().get("detail","Comparison failed") if cr else "Error")

            comp = st.session_state.mi_comparison
            if comp and comp.get("comparisons"):
                rows = comp["comparisons"]

                # ── Overall trend ─────────────────────────────────
                ot = comp.get("overall_trend","")
                if ot:
                    st.info(f"📈 **Overall Trend:** {ot}")

                st.markdown("---")

                # ── Comparison table ──────────────────────────────
                def trend_html(t):
                    tl = (t or "").lower()
                    if "increas" in tl: return f'<span class="t-up">↑ Increasing</span>'
                    if "decreas" in tl: return f'<span class="t-dn">↓ Decreasing</span>'
                    return f'<span class="t-st">→ Stable</span>'

                rows_html = ""
                for i, r in enumerate(rows):
                    bg = "rgba(26,109,176,.03)" if i%2==0 else "transparent"
                    rows_html += f"""<tr style="background:{bg}">
                      <td class="pname" style="padding:11px 14px">{r.get("parameter","")}</td>
                      <td style="padding:11px 14px;color:#5a7a9a;font-weight:600">{r.get("previous","")}</td>
                      <td style="padding:11px 14px;font-weight:700;color:#0c2340">{r.get("current","")}</td>
                      <td style="padding:11px 14px">{trend_html(r.get("trend",""))}</td>
                      <td class="pnote" style="padding:11px 14px">{r.get("interpretation","")}</td>
                    </tr>"""

                st.markdown(f"""
                <div style="overflow-x:auto;border-radius:12px;border:1px solid rgba(26,109,176,.15)">
                <table class="ptable">
                  <thead><tr>
                    <th>Parameter</th>
                    <th>Previous</th>
                    <th>Current</th>
                    <th>Trend</th>
                    <th>Interpretation</th>
                  </tr></thead>
                  <tbody>{rows_html}</tbody>
                </table></div>""", unsafe_allow_html=True)

                st.markdown("")

                # ── Comparison bar chart ──────────────────────────
                prev_vals, curr_vals, param_names = [], [], []
                for r in rows:
                    try:
                        pv = float(re.findall(r"[\d.]+", r.get("previous",""))[0])
                        cv = float(re.findall(r"[\d.]+", r.get("current",""))[0])
                        prev_vals.append(pv)
                        curr_vals.append(cv)
                        param_names.append(r["parameter"])
                    except:
                        pass

                if param_names:
                    fig_comp = go.Figure(data=[
                        go.Bar(name="Previous", x=param_names, y=prev_vals,
                               marker_color="rgba(91,163,217,0.8)",
                               marker_line=dict(color="#5ba3d9",width=1)),
                        go.Bar(name="Current",  x=param_names, y=curr_vals,
                               marker_color="rgba(12,35,64,0.85)",
                               marker_line=dict(color="#0c2340",width=1)),
                    ])
                    fig_comp.update_layout(
                        barmode="group",
                        plot_bgcolor="rgba(240,248,255,0.3)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="DM Sans", color="#1a2b3c"),
                        xaxis=dict(tickangle=-30,
                                   gridcolor="rgba(180,210,255,0.2)"),
                        yaxis=dict(gridcolor="rgba(180,210,255,0.2)"),
                        legend=dict(orientation="h", y=1.08),
                        margin=dict(t=40, b=70, l=50, r=30),
                        height=380,
                        title=dict(text="Previous vs Current Values",
                                   font=dict(size=14, color="#0c2340")),
                    )
                    st.plotly_chart(fig_comp, use_container_width=True)

                    # ── Trend indicator dots ──────────────────────
                    st.markdown("**Trend Summary**")
                    trend_cols = st.columns(min(5, len(rows)))
                    for ti, r in enumerate(rows[:5]):
                        t   = r.get("trend","")
                        tl  = t.lower()
                        sym = "↑" if "increas" in tl else ("↓" if "decreas" in tl else "→")
                        clr = "#0a6b35" if "increas" in tl else ("#b80000" if "decreas" in tl else "#b86a00")
                        trend_cols[ti].markdown(
                            f'<div style="text-align:center;padding:12px 6px;border-radius:10px;'
                            f'background:{clr}18;border:1px solid {clr}44">'
                            f'<div style="font-size:1.4rem;color:{clr}">{sym}</div>'
                            f'<div style="font-size:.72rem;font-weight:700;color:{clr};margin-top:4px">'
                            f'{r["parameter"][:12]}</div></div>',
                            unsafe_allow_html=True)

                st.markdown(
                    f'<div class="disc">⚕️ {comp.get("disclaimer","Educational only.")}</div>',
                    unsafe_allow_html=True)