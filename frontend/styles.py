# ═══════════════════════════════════════════════════════════════════════════════
#  Unified Design System v2 — Dark / Light theme with animated backgrounds
#  shadcn/ui inspired • Inter typography • CSS-only animations
# ═══════════════════════════════════════════════════════════════════════════════

GLOBAL_CSS = """
<style>
/* ── Google Font ─────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ═════════════════════════════════════════════════════════════════════════════
   THEME TOKENS — Dark Mode (default)
   ═════════════════════════════════════════════════════════════════════════════ */
:root {
  /* ── Core backgrounds ── */
  --bg:       #0B1220;
  --bg2:      #0f1729;
  --surface:  #111827;
  --surface2: #1a2236;
  --surface3: #253047;

  /* ── Accent ── */
  --accent:       #3b82f6;
  --accent-dim:   rgba(59,130,246,0.15);
  --accent-glow:  rgba(59,130,246,0.28);
  --accent-hover: #2563eb;

  /* ── Semantic colours ── */
  --green:  #22c55e;
  --orange: #f97316;
  --yellow: #eab308;
  --red:    #ef4444;
  --pink:   #ec4899;
  --cyan:   #06b6d4;
  --purple: #a855f7;
  --teal:   #14b8a6;

  /* ── Text ── */
  --text:   #f1f5f9;
  --text2:  #cbd5e1;
  --muted:  #64748b;
  --muted2: #475569;

  /* ── Borders ── */
  --border:    rgba(255,255,255,0.06);
  --border-md: rgba(255,255,255,0.10);
  --border-lg: rgba(255,255,255,0.16);

  /* ── Radii ── */
  --radius:    10px;
  --radius-lg: 16px;
  --radius-xl: 22px;

  /* ── Typography ── */
  --font: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

  /* ── Shadows ── */
  --shadow-sm:  0 1px 6px rgba(0,0,0,0.4);
  --shadow-md:  0 4px 20px rgba(0,0,0,0.5);
  --shadow-lg:  0 12px 40px rgba(0,0,0,0.6);
  --shadow-xl:  0 20px 60px rgba(0,0,0,0.7);

  /* ── Nav pill ── */
  --nav-bg:      rgba(17,24,39,0.92);
  --nav-pill:    rgba(59,130,246,0.18);
  --nav-active:  #3b82f6;

  /* ── Theme flag (dark=1, light=0) ── */
  --is-dark: 1;
}

/* ═════════════════════════════════════════════════════════════════════════════
   LIGHT MODE OVERRIDES — applied when body has class "light-mode"
   ═════════════════════════════════════════════════════════════════════════════ */
body.light-mode,
body.light-mode [data-testid="stAppViewContainer"],
body.light-mode [data-testid="stMain"],
body.light-mode .main {
  --bg:       #F9FAFB !important;
  --bg2:      #f3f4f6 !important;
  --surface:  #FFFFFF !important;
  --surface2: #f8fafc !important;
  --surface3: #e2e8f0 !important;
  --text:     #0f172a !important;
  --text2:    #1e293b !important;
  --muted:    #64748b !important;
  --muted2:   #94a3b8 !important;
  --border:   rgba(0,0,0,0.06) !important;
  --border-md:rgba(0,0,0,0.10) !important;
  --border-lg:rgba(0,0,0,0.16) !important;
  --nav-bg:   rgba(255,255,255,0.95) !important;
  --shadow-sm:0 1px 6px rgba(0,0,0,0.08) !important;
  --shadow-md:0 4px 20px rgba(0,0,0,0.10) !important;
  --shadow-lg:0 12px 40px rgba(0,0,0,0.15) !important;
  background-color: #F9FAFB !important;
  color: #0f172a !important;
}

/* ── Global Reset ─────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main {
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-family: var(--font) !important;
  transition: background-color 0.4s ease, color 0.4s ease !important;
}

/* ── Hide Streamlit chrome ───────────────────────────────────────────────── */
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
#MainMenu, footer { display: none !important; }

/* ── Hide sidebar entirely ───────────────────────────────────────────────── */
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
section[data-testid="stSidebarContent"] { display: none !important; }

/* ── Block container ─────────────────────────────────────────────────────── */
.block-container {
  padding: 1rem 2rem 4rem !important;
  max-width: 1280px !important;
}

/* ═════════════════════════════════════════════════════════════════════════════
   ANIMATED BACKGROUND GRADIENT
   ═════════════════════════════════════════════════════════════════════════════ */
.bg-animated {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  opacity: 0.45;
  background:
    radial-gradient(ellipse 80% 60% at 20% 10%, rgba(59,130,246,0.12) 0%, transparent 60%),
    radial-gradient(ellipse 60% 50% at 80% 90%, rgba(168,85,247,0.08) 0%, transparent 55%),
    radial-gradient(ellipse 50% 70% at 60% 30%, rgba(6,182,212,0.06) 0%, transparent 50%);
  animation: bgFloat 18s ease-in-out infinite alternate;
}
.bg-animated.light {
  opacity: 0.20;
  background:
    radial-gradient(ellipse 80% 60% at 20% 10%, rgba(59,130,246,0.15) 0%, transparent 60%),
    radial-gradient(ellipse 60% 50% at 80% 90%, rgba(168,85,247,0.10) 0%, transparent 55%);
}
@keyframes bgFloat {
  0%   { transform: translate(0, 0) scale(1); }
  33%  { transform: translate(1.5%, 0.8%) scale(1.03); }
  66%  { transform: translate(-1%, 1.5%) scale(0.98); }
  100% { transform: translate(0.5%, -1%) scale(1.02); }
}

/* ═════════════════════════════════════════════════════════════════════════════
   HORIZONTAL NAVBAR
   ═════════════════════════════════════════════════════════════════════════════ */
.hn-wrap {
  position: sticky;
  top: 0;
  z-index: 999;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  background: var(--nav-bg);
  border-bottom: 1px solid var(--border-md);
  padding: 0.6rem 2rem;
  margin: -1rem -2rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background 0.4s ease;
  box-shadow: 0 1px 24px rgba(0,0,0,0.30);
}
.hn-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1rem;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.02em;
  margin-right: 1rem;
  flex-shrink: 0;
  text-decoration: none;
}
.hn-logo-icon {
  width: 32px; height: 32px;
  background: linear-gradient(135deg, var(--accent), var(--cyan));
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1rem;
  box-shadow: 0 0 14px var(--accent-glow);
}
.hn-tabs {
  display: flex;
  align-items: center;
  gap: 0.2rem;
  flex: 1;
}
.hn-tab {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0.38rem 0.9rem;
  border-radius: 50px;
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--muted);
  cursor: pointer;
  border: none;
  background: transparent;
  font-family: var(--font);
  text-decoration: none;
  transition: all 0.22s ease;
  white-space: nowrap;
}
.hn-tab:hover {
  color: var(--text);
  background: var(--surface2);
}
.hn-tab.active {
  background: var(--nav-pill);
  color: var(--accent);
  font-weight: 600;
  box-shadow: 0 0 0 1px rgba(59,130,246,0.3);
}
.hn-right {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-left: auto;
  flex-shrink: 0;
}
/* Theme toggle pill */
.theme-toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0.35rem 0.8rem;
  border-radius: 50px;
  font-size: 0.8rem;
  font-weight: 500;
  border: 1px solid var(--border-md);
  background: var(--surface2);
  color: var(--text2);
  cursor: pointer;
  transition: all 0.25s ease;
  font-family: var(--font);
}
.theme-toggle:hover {
  border-color: var(--accent);
  color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-dim);
}
/* Avatar in nav */
.nav-avatar {
  width: 36px; height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), var(--cyan));
  display: flex; align-items: center; justify-content: center;
  font-size: 0.78rem; font-weight: 800; color: #fff;
  border: 2px solid var(--border-lg);
  box-shadow: 0 0 12px var(--accent-glow);
  flex-shrink: 0;
  cursor: pointer;
  transition: transform 0.22s ease, box-shadow 0.22s ease;
  user-select: none;
}
.nav-avatar:hover {
  transform: scale(1.1);
  box-shadow: 0 0 20px var(--accent-glow);
}

/* ── Profile dropdown wrapper ──────────────────────────────────── */
.nav-profile {
  position: relative;
  display: flex;
  align-items: center;
}
.nav-dropdown {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  min-width: 200px;
  background: var(--surface);
  border: 1px solid var(--border-md);
  border-radius: var(--radius-lg);
  box-shadow: 0 16px 48px rgba(0,0,0,0.55), 0 0 0 1px var(--border);
  padding: 0.5rem 0;
  z-index: 1200;
  animation: dropIn 0.22s cubic-bezier(0.22, 1, 0.36, 1) both;
  transform-origin: top right;
}
@keyframes dropIn {
  from { opacity: 0; transform: scale(0.90) translateY(-8px); }
  to   { opacity: 1; transform: scale(1)   translateY(0); }
}
.nav-dropdown-header {
  padding: 0.75rem 1rem 0.5rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 0.35rem;
}
.nav-dd-name {
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--text);
  line-height: 1.2;
}
.nav-dd-role {
  font-size: 0.72rem;
  color: var(--muted);
  margin-top: 0.1rem;
}
.nav-dd-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.55rem 1rem;
  font-size: 0.84rem;
  font-weight: 500;
  color: var(--text2);
  cursor: pointer;
  transition: all 0.18s ease;
  border: none;
  background: transparent;
  width: 100%;
  text-align: left;
  font-family: var(--font);
  border-radius: 0;
}
.nav-dd-item:hover {
  background: var(--surface2);
  color: var(--text);
  padding-left: 1.2rem;
}
.nav-dd-item.logout {
  color: var(--red);
  border-top: 1px solid var(--border);
  margin-top: 0.35rem;
  padding-top: 0.65rem;
}
.nav-dd-item.logout:hover {
  background: rgba(239,68,68,0.10);
  color: #ff6b6b;
}
/* Divider within dropdown */
.nav-dd-divider {
  height: 1px;
  background: var(--border);
  margin: 0.3rem 0;
}

/* ── Back button ─────────────────────────────────────────────────────────── */
.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--muted);
  cursor: pointer;
  padding: 0.3rem 0;
  text-decoration: none;
  transition: color 0.2s ease;
  margin-bottom: 1rem;
}
.back-btn:hover { color: var(--accent); }

/* ═════════════════════════════════════════════════════════════════════════════
   DASHBOARD HEADER
   ═════════════════════════════════════════════════════════════════════════════ */
.db-header {
  background: var(--surface);
  border: 1px solid var(--border-md);
  border-radius: var(--radius-xl);
  padding: 1.6rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  overflow: hidden;
  margin-bottom: 1.8rem;
  transition: background 0.4s ease;
  box-shadow: var(--shadow-md);
  animation: cardIn 0.55s ease both;
}
.db-header::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, var(--accent), var(--cyan), transparent);
}
.db-header-left h1 {
  font-size: 1.65rem; font-weight: 800;
  color: var(--text); letter-spacing: -0.02em; margin: 0;
}
.db-header-left p { color: var(--muted); font-size: 0.85rem; margin: 0.3rem 0 0; }
.db-header-right { display: flex; align-items: center; gap: 14px; }
.db-avatar {
  width: 52px; height: 52px; border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), var(--cyan));
  display: flex; align-items: center; justify-content: center;
  font-weight: 800; font-size: 1.15rem; color: #fff; flex-shrink: 0;
  box-shadow: 0 4px 18px var(--accent-glow);
  border: 2px solid var(--border-lg);
}
.db-badge {
  display: inline-flex; align-items: center; gap: 6px;
  background: rgba(34,197,94,0.10);
  border: 1px solid rgba(34,197,94,0.25);
  color: var(--green);
  padding: 0.3rem 0.85rem;
  border-radius: 50px;
  font-size: 0.75rem; font-weight: 600;
}
.db-badge-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--green);
  animation: pulse 2s infinite;
}

/* ═════════════════════════════════════════════════════════════════════════════
   SECTION LABEL
   ═════════════════════════════════════════════════════════════════════════════ */
.section-label {
  font-size: 0.70rem;
  font-weight: 700;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  margin: 0 0 1rem;
  display: flex;
  align-items: center;
  gap: 0.6rem;
}
.section-label::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}

/* ═════════════════════════════════════════════════════════════════════════════
   STAT CARDS  (stagger animation via --i custom prop)
   ═════════════════════════════════════════════════════════════════════════════ */
.stat-card {
  background: var(--surface);
  border: 1px solid var(--border-md);
  border-radius: var(--radius-lg);
  padding: 1.2rem 1.2rem 1.3rem;
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
  position: relative;
  overflow: hidden;
  transition: transform 0.22s ease, box-shadow 0.22s ease, background 0.4s ease, border-color 0.22s ease;
  animation: cardIn 0.5s ease calc(var(--i, 0) * 0.08s) both;
  box-shadow: var(--shadow-sm);
}
.stat-card:hover {
  transform: translateY(-4px) scale(1.015);
  box-shadow: 0 14px 36px rgba(0,0,0,0.45), 0 0 0 1px var(--border-lg);
}
.stat-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: var(--c, var(--accent));
  border-radius: 2px 2px 0 0;
}
.stat-card::after {
  content: '';
  position: absolute; bottom: 0; right: 0;
  width: 70px; height: 70px;
  background: radial-gradient(circle, var(--c-glow, rgba(59,130,246,0.10)), transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}
.stat-card-icon {
  width: 42px; height: 42px;
  border-radius: 12px;
  background: var(--ic, var(--accent-dim));
  border: 1px solid var(--ib, rgba(59,130,246,0.25));
  display: flex; align-items: center; justify-content: center;
  font-size: 1.15rem;
}
.stat-card-num {
  font-size: 2.1rem;
  font-weight: 900;
  color: var(--text);
  line-height: 1;
  letter-spacing: -0.04em;
}
.stat-card-label {
  font-size: 0.75rem;
  color: var(--muted);
  font-weight: 500;
  letter-spacing: 0.02em;
}

/* ═════════════════════════════════════════════════════════════════════════════
   FEATURE CARDS
   ═════════════════════════════════════════════════════════════════════════════ */
.feature-card {
  background: var(--surface);
  border: 1px solid var(--border-md);
  border-radius: var(--radius-xl);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
  transition: transform 0.25s ease, box-shadow 0.25s ease, background 0.4s ease;
  height: 100%;
  animation: cardIn 0.55s ease calc(var(--i, 0) * 0.10s) both;
  box-shadow: var(--shadow-sm);
}
.feature-card:hover {
  transform: translateY(-6px) scale(1.01);
  box-shadow: 0 20px 50px rgba(0,0,0,0.5);
}
.feature-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: var(--fc-grad, linear-gradient(90deg, var(--accent), transparent));
}
.feature-card-img {
  width: 100%; height: 155px;
  display: flex; align-items: center; justify-content: center;
  overflow: hidden;
  border-bottom: 1px solid var(--border);
  position: relative;
}
.feature-card-img img {
  width: 100%; height: 100%;
  object-fit: cover;
  opacity: 0.90;
  transition: opacity 0.3s ease, transform 0.4s ease;
}
.feature-card:hover .feature-card-img img {
  opacity: 1;
  transform: scale(1.04);
}
.feature-card-body { padding: 1.3rem 1.5rem 1.5rem; flex: 1; display: flex; flex-direction: column; }
.feature-card-title {
  font-size: 1.02rem;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 0.4rem;
  display: flex; align-items: center; gap: 8px;
}
.feature-card-desc {
  color: var(--muted);
  font-size: 0.83rem;
  line-height: 1.6;
  flex: 1;
  margin-bottom: 1.1rem;
}

/* ═════════════════════════════════════════════════════════════════════════════
   ACTIVITY CARDS
   ═════════════════════════════════════════════════════════════════════════════ */
.activity-card {
  background: var(--surface);
  border: 1px solid var(--border-md);
  border-radius: var(--radius-lg);
  padding: 1.3rem 1.5rem;
  position: relative;
  overflow: hidden;
  height: 100%;
  transition: background 0.4s ease;
  animation: cardIn 0.6s ease 0.3s both;
}
.activity-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: var(--ac-grad, linear-gradient(90deg, var(--accent), transparent));
}
.activity-card-title {
  font-size: 0.88rem; font-weight: 600; color: var(--text);
  margin-bottom: 0.9rem; display: flex; align-items: center; gap: 0.5rem;
}
.activity-msg {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-left: 2px solid var(--accent);
  border-radius: 8px;
  padding: 0.55rem 0.85rem;
  margin-bottom: 0.4rem;
  font-size: 0.82rem;
  color: var(--muted);
  line-height: 1.5;
}
.activity-msg span { color: var(--text); font-weight: 500; }
.activity-empty {
  text-align: center; padding: 1.5rem; color: var(--muted); font-size: 0.82rem;
}
.activity-empty-icon { font-size: 2rem; opacity: 0.30; margin-bottom: 0.5rem; }

/* DataInsight placeholder */
.di-placeholder {
  background: var(--surface);
  border: 1px solid rgba(59,130,246,0.2);
  border-radius: var(--radius-xl);
  padding: 2rem;
  text-align: center;
  animation: cardIn 0.6s ease 0.4s both;
}
.di-placeholder-icon { font-size: 3rem; margin-bottom: 1rem; opacity: 0.70; }
.di-placeholder h3 { font-size: 1.1rem; font-weight: 700; color: var(--text); margin: 0 0 0.4rem; }
.di-placeholder p { color: var(--muted); font-size: 0.85rem; margin: 0; }

/* ═════════════════════════════════════════════════════════════════════════════
   PAGE HEADER  (module pages)
   ═════════════════════════════════════════════════════════════════════════════ */
.page-header {
  background: var(--surface);
  border: 1px solid var(--border-md);
  border-radius: var(--radius-xl);
  padding: 1.5rem 2rem;
  margin-bottom: 2rem;
  display: flex;
  align-items: center;
  gap: 1.25rem;
  position: relative;
  overflow: hidden;
  transition: background 0.4s ease;
  animation: cardIn 0.50s ease both;
  box-shadow: var(--shadow-sm);
}
.page-header::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, var(--accent), transparent 70%);
}
.page-header-icon {
  width: 52px; height: 52px;
  background: var(--accent-dim);
  border: 1px solid rgba(59,130,246,0.3);
  border-radius: var(--radius-lg);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.55rem; flex-shrink: 0;
}
.page-header-text h1 { font-size: 1.5rem; font-weight: 700; color: var(--text); margin: 0; letter-spacing: -0.02em; }
.page-header-text p  { color: var(--muted); font-size: 0.85rem; margin: 0.2rem 0 0; }

/* ═════════════════════════════════════════════════════════════════════════════
   AUTH PAGE
   ═════════════════════════════════════════════════════════════════════════════ */
.auth-card {
  background: var(--surface);
  border: 1px solid var(--border-md);
  border-radius: var(--radius-xl);
  padding: 2.5rem 2.5rem 2rem;
  width: 100%; max-width: 460px;
  position: relative;
  box-shadow: var(--shadow-xl);
  animation: slideUp 0.42s ease;
}
@keyframes slideUp {
  from { opacity:0; transform:translateY(24px); }
  to   { opacity:1; transform:translateY(0); }
}
.auth-logo { text-align: center; margin-bottom: 1.75rem; }
.auth-logo-icon {
  width: 62px; height: 62px;
  background: var(--accent-dim);
  border: 1px solid rgba(59,130,246,0.4);
  border-radius: var(--radius-lg);
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 1.9rem; margin-bottom: 0.85rem;
  box-shadow: 0 8px 28px var(--accent-glow);
}
.auth-logo h1 { font-size: 1.55rem; font-weight: 800; color: var(--text); letter-spacing: -0.02em; margin: 0; }
.auth-logo p  { color: var(--muted); font-size: 0.86rem; margin-top: 0.25rem; }

/* ═════════════════════════════════════════════════════════════════════════════
   FORM INPUTS
   ═════════════════════════════════════════════════════════════════════════════ */
.stTextInput > div > div > input,
.stTextArea  > div > div > textarea,
.stNumberInput > div > div > input {
  background: var(--surface2) !important;
  border: 1px solid var(--border-md) !important;
  border-radius: var(--radius) !important;
  color: var(--text) !important;
  font-family: var(--font) !important;
  font-size: 0.9rem !important;
  padding: 0.65rem 1rem !important;
  transition: border-color 0.2s, box-shadow 0.2s, background 0.4s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea  > div > div > textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px var(--accent-dim) !important;
}
.stTextInput > div > div > input::placeholder,
.stTextArea  > div > div > textarea::placeholder { color: var(--muted2) !important; }

/* ── Selectbox ───────────────────────────────────────────────────────────── */
.stSelectbox > div > div {
  background: var(--surface2) !important;
  border: 1px solid var(--border-md) !important;
  border-radius: var(--radius) !important;
  color: var(--text) !important;
  font-family: var(--font) !important;
}

/* ── Labels ──────────────────────────────────────────────────────────────── */
label, .stTextInput label, .stSelectbox label,
.stTextArea label, .stDateInput label, .stTimeInput label {
  color: var(--muted) !important;
  font-family: var(--font) !important;
  font-size: 0.76rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.07em !important;
  text-transform: uppercase !important;
}

/* ── Buttons ─────────────────────────────────────────────────────────────── */
.stButton > button {
  background: var(--surface2) !important;
  border: 1px solid var(--border-md) !important;
  border-radius: var(--radius) !important;
  color: var(--text) !important;
  font-family: var(--font) !important;
  font-weight: 500 !important;
  font-size: 0.88rem !important;
  padding: 0.55rem 1.25rem !important;
  transition: all 0.22s ease !important;
}
.stButton > button:hover {
  background: var(--surface3) !important;
  border-color: var(--border-lg) !important;
  transform: translateY(-1px) !important;
  box-shadow: var(--shadow-sm) !important;
}
.stButton > button[kind="primary"] {
  background: var(--accent) !important;
  border-color: var(--accent) !important;
  color: #fff !important;
  box-shadow: 0 4px 16px var(--accent-glow) !important;
}
.stButton > button[kind="primary"]:hover {
  background: var(--accent-hover) !important;
  border-color: var(--accent-hover) !important;
  box-shadow: 0 6px 24px rgba(59,130,246,0.45) !important;
  transform: translateY(-2px) !important;
}

/* ── Tabs ────────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--surface2) !important;
  border-radius: var(--radius) !important;
  padding: 4px !important;
  gap: 4px !important;
  border: 1px solid var(--border-md) !important;
  margin-bottom: 1.5rem !important;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 8px !important;
  font-family: var(--font) !important;
  font-weight: 500 !important;
  font-size: 0.84rem !important;
  color: var(--muted) !important;
  background: transparent !important;
  padding: 0.5rem 1.2rem !important;
  transition: all 0.2s !important;
}
.stTabs [aria-selected="true"] {
  background: var(--surface) !important;
  color: var(--text) !important;
  box-shadow: 0 1px 4px rgba(0,0,0,0.3) !important;
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ── Expanders ───────────────────────────────────────────────────────────── */
.stExpander {
  background: var(--surface) !important;
  border: 1px solid var(--border-md) !important;
  border-radius: var(--radius-lg) !important;
  margin-bottom: 0.7rem !important;
  overflow: hidden !important;
}
.stExpander:hover { border-color: var(--surface3) !important; }
.stExpander summary {
  font-family: var(--font) !important;
  font-weight: 500 !important;
  font-size: 0.9rem !important;
  color: var(--text) !important;
  padding: 1rem 1.2rem !important;
}
details[open] > summary {
  border-bottom: 1px solid var(--border) !important;
  color: var(--accent) !important;
}

/* ── File Uploader ───────────────────────────────────────────────────────── */
[data-testid="stFileUploader"] {
  background: var(--surface2) !important;
  border: 2px dashed var(--border-md) !important;
  border-radius: var(--radius-lg) !important;
  padding: 8px !important;
  transition: border-color 0.2s !important;
}
[data-testid="stFileUploader"]:hover { border-color: var(--accent) !important; }

/* ── Alert boxes ─────────────────────────────────────────────────────────── */
.stSuccess { background: rgba(34,197,94,0.1) !important; border: 1px solid rgba(34,197,94,0.3) !important; border-radius: var(--radius) !important; }
.stError   { background: rgba(239,68,68,0.1)  !important; border: 1px solid rgba(239,68,68,0.3)  !important; border-radius: var(--radius) !important; }
.stWarning { background: rgba(234,179,8,0.1)  !important; border: 1px solid rgba(234,179,8,0.3)  !important; border-radius: var(--radius) !important; }
.stInfo, [data-testid="stInfo"] {
  background: rgba(59,130,246,0.08) !important;
  border: 1px solid rgba(59,130,246,0.25) !important;
  border-radius: var(--radius) !important;
  font-size: 0.85rem !important;
}

/* ── Spinner ─────────────────────────────────────────────────────────────── */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* ── Scrollbar ───────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--surface3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--muted2); }

/* ── Chat bubbles ────────────────────────────────────────────────────────── */
.stChatMessage { background: transparent !important; border: none !important; padding: 0 !important; }
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stChatMessageContent {
  background: var(--accent) !important;
  border-radius: 18px 18px 4px 18px !important;
  padding: 12px 16px !important;
  color: #fff !important;
  max-width: 75%;
  margin-left: auto;
  box-shadow: 0 4px 16px var(--accent-glow);
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stChatMessageContent {
  background: var(--surface) !important;
  border: 1px solid var(--border-md) !important;
  border-radius: 18px 18px 18px 4px !important;
  padding: 12px 16px !important;
  max-width: 80%;
}
[data-testid="chatAvatarIcon-user"],
[data-testid="chatAvatarIcon-assistant"] {
  background: var(--surface2) !important;
  border: 1px solid var(--border-md) !important;
  border-radius: 50% !important;
  width: 34px !important; height: 34px !important;
}
.stChatInputContainer {
  background: var(--surface) !important;
  border: 1px solid var(--border-md) !important;
  border-radius: var(--radius-lg) !important;
  padding: 4px 8px !important;
  transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stChatInputContainer:focus-within {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px var(--accent-dim) !important;
}
.stChatInputContainer textarea {
  background: transparent !important; color: var(--text) !important;
  font-family: var(--font) !important; font-size: 0.9rem !important; border: none !important;
}
.stChatInputContainer textarea::placeholder { color: var(--muted2) !important; }
.stChatInputContainer button {
  background: var(--accent) !important; border-radius: 10px !important;
  border: none !important; color: white !important;
}

/* ── MediGenius header ───────────────────────────────────────────────────── */
.mg-header { display: flex; align-items: center; gap: 14px; margin-bottom: 4px; }
.mg-logo {
  width: 50px; height: 50px;
  background: linear-gradient(135deg, var(--accent), var(--cyan));
  border-radius: var(--radius-lg);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.5rem; flex-shrink: 0;
  box-shadow: 0 0 24px var(--accent-glow);
}
.mg-title    { font-size: 1.75rem !important; font-weight: 800 !important; color: var(--text) !important; margin: 0 !important; }
.mg-subtitle { font-size: 0.8rem; color: var(--muted); margin: 0; letter-spacing: 0.02em; }
.mg-divider  { height: 1px; background: linear-gradient(90deg, transparent, var(--surface3), transparent); margin: 14px 0 22px; }

/* ── Search / Result cards ───────────────────────────────────────────────── */
.search-card {
  background: var(--surface);
  border: 1px solid var(--border-md);
  border-radius: var(--radius-xl);
  padding: 1.5rem 1.75rem 1.25rem;
  margin-bottom: 1.75rem;
  box-shadow: var(--shadow-md);
}
.search-label {
  font-size: 0.72rem; font-weight: 700;
  color: var(--muted); text-transform: uppercase;
  letter-spacing: 0.08em; margin-bottom: 0.65rem;
}
.result-card {
  background: var(--surface);
  border: 1px solid rgba(34,197,94,0.25);
  border-left: 3px solid var(--green);
  border-radius: var(--radius-lg);
  padding: 1rem 1.25rem;
  margin: 1rem 0 0.25rem;
}
.result-title { font-size: 0.95rem; font-weight: 600; color: var(--green); display: flex; align-items: center; gap: 8px; }

/* ═════════════════════════════════════════════════════════════════════════════
   KEYFRAME ANIMATIONS
   ═════════════════════════════════════════════════════════════════════════════ */
@keyframes cardIn {
  from { opacity: 0; transform: translateY(18px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0)    scale(1); }
}
@keyframes pulse {
  0%,100% { opacity:1; transform:scale(1); }
  50%     { opacity:0.4; transform:scale(1.3); }
}
@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}
@keyframes shimmer {
  0%   { background-position: -200% center; }
  100% { background-position: 200%  center; }
}
</style>
"""


# ─── Helper: inject theme CSS into body ─────────────────────────────────────
def get_theme_inject_css(is_light: bool) -> str:
    """Returns JS that adds/removes 'light-mode' class on body."""
    cls = "light-mode" if is_light else ""
    return f"""
<script>
(function() {{
  document.body.className = document.body.className
    .replace(/\\blight-mode\\b/g, '').trim();
  if ("{cls}") document.body.classList.add("{cls}");
}})();
</script>
"""


# ─── Helper: animated background div ────────────────────────────────────────
def animated_bg_html(is_light: bool = False) -> str:
    cls = "bg-animated light" if is_light else "bg-animated"
    return f'<div class="{cls}"></div>'


# ─── Helper: horizontal navbar ───────────────────────────────────────────────
NAV_PAGES = [
    ("💬", "Chats",       "pages/2_💬_MediGenius.py"),
    ("💊", "Scans",       "pages/3_💊_MediScan.py"),
    ("📋", "Records",     "pages/4_📋_Health_Records.py"),
    ("👨‍👩‍👧", "Family",   "pages/5_👨‍👩‍👧_Family_History.py"),
    ("📈", "DataInsight", "pages/8_📊_Data_Insights.py"),
]

def navbar_html(active: str = "", initials: str = "U", is_light: bool = False,
                user_name: str = "User", show_dropdown: bool = False) -> str:
    tabs_html = ""
    for icon, label, _ in NAV_PAGES:
        cls = "hn-tab active" if label == active else "hn-tab"
        tabs_html += f'<span class="{cls}">{icon}&nbsp; {label}</span>'

    toggle_icon  = "☀️" if not is_light else "🌙"
    toggle_label = "Light" if not is_light else "Dark"

    # Profile dropdown HTML (pure CSS toggle via hidden checkbox trick is unreliable;
    # we render it always and JS onclick controls visibility)
    dropdown_html = f"""
<div class="nav-dropdown" id="nav-dd">
  <div class="nav-dropdown-header">
    <div class="nav-dd-name">{user_name}</div>
    <div class="nav-dd-role">Health Dashboard</div>
  </div>
  <div class="nav-dd-item">⚙️&nbsp; Settings</div>
  <div class="nav-dd-divider"></div>
  <div class="nav-dd-item logout" id="dd-logout-btn">🚪&nbsp; Logout</div>
</div>
""" if show_dropdown else ""

    return f"""
<div class="hn-wrap" id="main-navbar">
  <div class="hn-logo">
    <div class="hn-logo-icon">🏥</div>
    HealthAI
  </div>
  <div class="hn-tabs">
    {tabs_html}
  </div>
  <div class="hn-right">
    <div class="theme-toggle" id="theme-pill" title="Toggle theme">
      {toggle_icon}&nbsp;{toggle_label}
    </div>
    <div class="nav-profile" id="nav-profile-wrap">
      <div class="nav-avatar" id="nav-avatar-btn" title="Profile">{initials}</div>
      <div class="nav-dropdown" id="nav-dd" style="display:none;">
        <div class="nav-dropdown-header">
          <div class="nav-dd-name">{user_name}</div>
          <div class="nav-dd-role">Health Dashboard</div>
        </div>
        <div class="nav-dd-divider"></div>
        <div class="nav-dd-item logout" id="dd-logout-btn">🚪&nbsp; Logout</div>
      </div>
    </div>
  </div>
</div>
<script>
(function() {{
  // Profile dropdown toggle
  var avatar = document.getElementById('nav-avatar-btn');
  var dd     = document.getElementById('nav-dd');
  if (!avatar || !dd) return;
  avatar.addEventListener('click', function(e) {{
    e.stopPropagation();
    var open = dd.style.display === 'block';
    dd.style.display = open ? 'none' : 'block';
    if (!open) {{
      dd.style.animation = 'none';
      dd.offsetHeight;  // reflow
      dd.style.animation = '';
    }}
  }});
  document.addEventListener('click', function() {{
    dd.style.display = 'none';
  }});
  // Logout inside dropdown triggers the Streamlit logout button
  var ddLogout = document.getElementById('dd-logout-btn');
  if (ddLogout) {{
    ddLogout.addEventListener('click', function(e) {{
      e.stopPropagation();
      // Find any button whose text contains 'Logout' or '🚪'
      var btns = Array.from(document.querySelectorAll('button'));
      var logoutBtn = btns.find(function(b) {{
        return b.innerText.toLowerCase().includes('logout');
      }});
      if (logoutBtn) {{ logoutBtn.click(); }}
    }});
  }}
}})();
</script>
"""


# ─── Helper: section label ───────────────────────────────────────────────────
def section_label_html(text: str) -> str:
    return f'<div class="section-label">{text}</div>'


# ─── Helper: stat card ───────────────────────────────────────────────────────
def stat_card_html(icon: str, value, label: str,
                   color: str = "#3b82f6",
                   icon_bg: str = "rgba(59,130,246,0.15)",
                   icon_border: str = "rgba(59,130,246,0.25)",
                   index: int = 0) -> str:
    glow = icon_bg.replace("0.15", "0.08").replace("0.12", "0.06")
    return f"""
<div class="stat-card" style="--c:{color};--ic:{icon_bg};--ib:{icon_border};--c-glow:{glow};--i:{index};">
    <div class="stat-card-icon">{icon}</div>
    <div class="stat-card-num">{value}</div>
    <div class="stat-card-label">{label}</div>
</div>
"""


# ─── Helper: page header ─────────────────────────────────────────────────────
def page_header_html(title: str, subtitle: str, icon: str, color: str = "#3b82f6") -> str:
    return f"""
<div class="page-header">
    <div class="page-header-icon">{icon}</div>
    <div class="page-header-text">
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
</div>
"""


# ─── Helper: sidebar user (kept for backward compat, hidden) ─────────────────
def sidebar_user_html(user_name: str) -> str:
    return ""
