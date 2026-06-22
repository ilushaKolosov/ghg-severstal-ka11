# -*- coding: utf-8 -*-
"""
Точка входа многостраничного приложения (Streamlit).

Страницы:
  • Калькулятор          — views/calculator.py
  • Инструкция и методика — views/guide.py

Глобальные стили (тёмная AAA-тема) инъектируются здесь, поэтому действуют
на всех страницах.

Запуск:
    pip install -r requirements.txt
    streamlit run app.py
"""
import streamlit as st

st.set_page_config(
    page_title="GHG Calculator · ТЭЦ-ПВС КА-11 · Северсталь",
    page_icon="🌍", layout="wide", initial_sidebar_state="expanded",
)

# ===========================================================================
#  ГЛОБАЛЬНЫЙ ТЁМНЫЙ AAA-СТИЛЬ
# ===========================================================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500&display=swap');

:root{
  --bg:#0a0f1c; --bg2:#0d1426; --panel:rgba(255,255,255,.035);
  --panel-strong:rgba(255,255,255,.06); --line:rgba(255,255,255,.10);
  --ink:#e8eef9; --muted:#8a99b5; --brand:#3b82f6; --brand2:#22d3ee;
  --green:#34d399; --red:#fb7185; --amber:#fbbf24; --violet:#a78bfa;
}
html,body,[class*="css"]{font-family:'Manrope',-apple-system,Segoe UI,Roboto,sans-serif}
.stApp{
  background:
    radial-gradient(1200px 600px at 12% -8%, rgba(59,130,246,.16), transparent 55%),
    radial-gradient(1000px 520px at 92% 0%, rgba(34,211,238,.12), transparent 50%),
    radial-gradient(900px 700px at 60% 120%, rgba(167,139,250,.10), transparent 55%),
    linear-gradient(180deg,#0a0f1c 0%, #0a0f1c 100%);
  background-attachment:fixed;
}
.block-container{padding-top:1.4rem;padding-bottom:3rem;max-width:1340px}
#MainMenu,footer,header[data-testid="stHeader"]{visibility:hidden;height:0}

/* ---------- HERO ---------- */
.hero{position:relative;border-radius:22px;padding:30px 34px;margin-bottom:22px;overflow:hidden;
  background:linear-gradient(135deg, rgba(59,130,246,.22), rgba(34,211,238,.10) 45%, rgba(167,139,250,.16));
  border:1px solid var(--line);
  box-shadow:0 24px 60px rgba(3,8,22,.55), inset 0 1px 0 rgba(255,255,255,.08);}
.hero::after{content:"";position:absolute;inset:0;background:
  radial-gradient(600px 200px at 85% 10%, rgba(34,211,238,.18), transparent 60%);pointer-events:none}
.hero .badge{display:inline-flex;align-items:center;gap:8px;font-size:11.5px;font-weight:700;
  letter-spacing:1.6px;text-transform:uppercase;color:#bfe0ff;background:rgba(59,130,246,.18);
  border:1px solid rgba(59,130,246,.45);padding:6px 13px;border-radius:30px}
.hero h1{font-size:30px;font-weight:800;margin:14px 0 8px;line-height:1.12;letter-spacing:-.4px;
  background:linear-gradient(90deg,#ffffff,#bfe0ff 60%,#7fe7f5);-webkit-background-clip:text;background-clip:text;color:transparent}
.hero p{color:#cdd9ef;max-width:880px;font-size:14px;line-height:1.55;margin:0}
.hero .tags{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}
.hero .tags span{font-size:12px;font-weight:600;color:#dbe6fb;background:rgba(255,255,255,.06);
  border:1px solid var(--line);padding:6px 12px;border-radius:10px;backdrop-filter:blur(6px)}

/* ---------- KPI ---------- */
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:6px 0 10px}
.kpi{position:relative;border-radius:18px;padding:18px 18px 16px;overflow:hidden;
  background:linear-gradient(180deg, rgba(255,255,255,.07), rgba(255,255,255,.02));
  border:1px solid var(--line);box-shadow:0 14px 40px rgba(3,8,22,.45), inset 0 1px 0 rgba(255,255,255,.06);
  transition:transform .18s ease, box-shadow .18s ease}
.kpi:hover{transform:translateY(-3px);box-shadow:0 22px 54px rgba(3,8,22,.6)}
.kpi .cap{font-size:12px;color:var(--muted);font-weight:600;display:flex;align-items:center;gap:8px}
.kpi .ic{width:30px;height:30px;border-radius:9px;display:grid;place-items:center;font-size:15px}
.kpi .val{font-size:27px;font-weight:800;margin-top:12px;letter-spacing:-.5px;font-variant-numeric:tabular-nums}
.kpi .sub{font-size:12px;color:var(--muted);margin-top:6px}
.kpi .bar{position:absolute;left:0;top:0;height:3px;width:100%;}
.kpi.b1 .bar{background:linear-gradient(90deg,#3b82f6,#22d3ee)} .kpi.b1 .ic{background:rgba(59,130,246,.2);color:#7fb4ff}
.kpi.b2 .bar{background:linear-gradient(90deg,#8a99b5,#cbd5e1)} .kpi.b2 .ic{background:rgba(148,163,184,.18);color:#cbd5e1}
.kpi.b3 .bar{background:linear-gradient(90deg,#10b981,#34d399)} .kpi.b3 .ic{background:rgba(52,211,153,.18);color:#34d399}
.kpi.b4 .bar{background:linear-gradient(90deg,#a78bfa,#f0abfc)} .kpi.b4 .ic{background:rgba(167,139,250,.2);color:#c4b5fd}
.chip{display:inline-block;font-size:12px;font-weight:700;padding:2px 9px;border-radius:20px;margin-top:8px}
.chip.up{background:rgba(52,211,153,.16);color:#34d399} .chip.down{background:rgba(251,113,133,.16);color:#fb7185}

/* ---------- section titles ---------- */
.sec{display:flex;align-items:center;gap:11px;margin:26px 0 12px}
.sec .l{width:5px;height:22px;border-radius:6px;background:linear-gradient(180deg,#3b82f6,#22d3ee)}
.sec h3{margin:0;font-size:17px;font-weight:800;color:#eaf1fc;letter-spacing:-.2px}
.sec .hint{margin-left:auto;font-size:12px;color:var(--muted)}

/* ---------- panels / sidebar ---------- */
div[data-testid="stDataFrame"], div[data-testid="stDataEditor"]{
  border:1px solid var(--line);border-radius:14px;overflow:hidden;
  box-shadow:0 12px 34px rgba(3,8,22,.4)}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#0c1322,#0a0f1c);border-right:1px solid var(--line)}
section[data-testid="stSidebar"] .stNumberInput label{font-size:12px;color:var(--muted);font-weight:600}
.stTabs [data-baseweb="tab-list"]{gap:6px}
.stTabs [data-baseweb="tab"]{background:rgba(255,255,255,.04);border:1px solid var(--line);
  border-radius:11px 11px 0 0;padding:9px 16px;font-weight:700;font-size:13px}
.stTabs [aria-selected="true"]{background:linear-gradient(180deg,rgba(59,130,246,.28),rgba(59,130,246,.08));
  color:#fff;border-color:rgba(59,130,246,.5)}
.stDownloadButton button, .stButton button{border-radius:11px;font-weight:700;border:1px solid var(--line);
  background:linear-gradient(180deg,rgba(59,130,246,.9),rgba(37,99,235,.95));color:#fff;box-shadow:0 8px 22px rgba(37,99,235,.35)}
.stButton button:hover,.stDownloadButton button:hover{filter:brightness(1.08)}
.note{color:var(--muted);font-size:13px;line-height:1.6}
.formula{font-family:'JetBrains Mono',monospace;background:rgba(255,255,255,.04);border:1px solid var(--line);
  border-radius:10px;padding:12px 14px;color:#cfe0ff;font-size:12.5px;line-height:1.9;overflow-x:auto}

/* ---------- guide page ---------- */
.gcards{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:10px 0}
.gcard{background:linear-gradient(180deg,rgba(255,255,255,.06),rgba(255,255,255,.02));
  border:1px solid var(--line);border-radius:16px;padding:18px;box-shadow:0 12px 32px rgba(3,8,22,.4)}
.gcard .ic{font-size:22px} .gcard h4{margin:10px 0 6px;font-size:15px;color:#eaf1fc;font-weight:800}
.gcard p{margin:0;color:var(--muted);font-size:13px;line-height:1.55}
.steps{counter-reset:s;display:flex;flex-direction:column;gap:12px;margin:6px 0}
.step{position:relative;padding:14px 16px 14px 60px;border:1px solid var(--line);border-radius:14px;
  background:rgba(255,255,255,.03);font-size:13.5px}
.step::before{counter-increment:s;content:counter(s);position:absolute;left:15px;top:50%;
  transform:translateY(-50%);width:32px;height:32px;border-radius:10px;display:grid;place-items:center;
  font-weight:800;color:#fff;background:linear-gradient(135deg,#3b82f6,#22d3ee)}
.step b{color:#eaf1fc} .step span{color:var(--muted)}
.gtable{width:100%;border-collapse:collapse;font-size:13px;margin-top:6px}
.gtable th,.gtable td{border:1px solid var(--line);padding:9px 11px;text-align:left;vertical-align:top}
.gtable th{background:rgba(255,255,255,.05);color:#cdd9ef;font-weight:700}
.gtable td{color:#c7d2e6}
.gtable code{font-family:'JetBrains Mono',monospace;color:#bfe0ff}
.kbd{font-family:'JetBrains Mono',monospace;background:rgba(59,130,246,.15);
  border:1px solid rgba(59,130,246,.4);border-radius:6px;padding:1px 7px;color:#bfe0ff;font-size:12px}
.callout{border-left:3px solid var(--brand);background:rgba(59,130,246,.08);border-radius:0 12px 12px 0;
  padding:14px 16px;color:#cdd9ef;font-size:13.5px;line-height:1.6;margin:8px 0}
@media(max-width:1000px){.gcards{grid-template-columns:1fr}.kpis{grid-template-columns:repeat(2,1fr)}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ===========================================================================
#  Навигация
# ===========================================================================
calc = st.Page("views/calculator.py", title="Калькулятор", icon="📊", default=True)
guide = st.Page("views/guide.py", title="Инструкция и методика", icon="📖")

st.navigation([calc, guide]).run()
