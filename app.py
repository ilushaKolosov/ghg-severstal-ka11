# -*- coding: utf-8 -*-
"""
РљР°Р»СЊРєСѓР»СЏС‚РѕСЂ РІС‹Р±СЂРѕСЃРѕРІ Рё СЃРѕРєСЂР°С‰РµРЅРёР№ РІС‹Р±СЂРѕСЃРѕРІ РїР°СЂРЅРёРєРѕРІС‹С… РіР°Р·РѕРІ вЂ” РїСЂРµРјРёР°Р»СЊРЅС‹Р№
С‚С‘РјРЅС‹Р№ РґР°С€Р±РѕСЂРґ (Streamlit + Plotly).

РљР»РёРјР°С‚РёС‡РµСЃРєРёР№ РїСЂРѕРµРєС‚ В«РџРѕР»РµР·РЅР°СЏ СѓС‚РёР»РёР·Р°С†РёСЏ РІС‚РѕСЂРёС‡РЅС‹С… СЌРЅРµСЂРіРµС‚РёС‡РµСЃРєРёС… СЂРµСЃСѓСЂСЃРѕРІ
РґРѕРјРµРЅРЅРѕРіРѕ РіР°Р·Р° СЃ РІС‹СЂР°Р±РѕС‚РєРѕР№ СЌР»РµРєС‚СЂРѕСЌРЅРµСЂРіРёРёВ» вЂ” РўР­Р¦-РџР’РЎ, РљРђ-11, РџРђРћ В«РЎРµРІРµСЂСЃС‚Р°Р»СЊВ».
Р¤РѕСЂРјСѓР»С‹ (1)-(13) РџР»Р°РЅР° РјРѕРЅРёС‚РѕСЂРёРЅРіР° PDD Рё РџСЂРёРєР°Р·Р° РњРёРЅРїСЂРёСЂРѕРґС‹ Р РѕСЃСЃРёРё в„– 371.

Р—Р°РїСѓСЃРє:
    pip install -r requirements.txt
    streamlit run app.py
"""
import io
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from engine import (Constants, YearInput, calc_period, default_inputs,
                    DEFAULT_COMPOSITION, GAS_COMPONENTS, N_CARBON, PLAN,
                    DEFAULT_YEARS, emission_factor_ng)

st.set_page_config(
    page_title="GHG Calculator В· РўР­Р¦-РџР’РЎ РљРђ-11 В· РЎРµРІРµСЂСЃС‚Р°Р»СЊ",
    page_icon="рџЊЌ", layout="wide", initial_sidebar_state="expanded",
)

# ===========================================================================
#  РџР Р•РњРРђР›Р¬РќР«Р™ РўРЃРњРќР«Р™ РЎРўРР›Р¬ (РёРЅСЉРµРєС†РёСЏ CSS)
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
@media (max-width:1000px){.kpis{grid-template-columns:repeat(2,1fr)}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ===========================================================================
#  РЈС‚РёР»РёС‚С‹ С„РѕСЂРјР°С‚РёСЂРѕРІР°РЅРёСЏ
# ===========================================================================
def ru(x, d=0):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return "вЂ”"
    s = f"{x:,.{d}f}".replace(",", " ").replace(".", ",")
    return s

# ===========================================================================
#  HERO
# ===========================================================================
st.markdown("""
<div class="hero">
  <span class="badge">в—Џ РљР»РёРјР°С‚РёС‡РµСЃРєРёР№ РїСЂРѕРµРєС‚ В· СЃС‚Р°РґРёСЏ РІРµСЂРёС„РёРєР°С†РёРё</span>
  <h1>РљР°Р»СЊРєСѓР»СЏС‚РѕСЂ РІС‹Р±СЂРѕСЃРѕРІ Рё СЃРѕРєСЂР°С‰РµРЅРёР№ РІС‹Р±СЂРѕСЃРѕРІ РїР°СЂРЅРёРєРѕРІС‹С… РіР°Р·РѕРІ</h1>
  <p>РџРѕР»РµР·РЅР°СЏ СѓС‚РёР»РёР·Р°С†РёСЏ РІС‚РѕСЂРёС‡РЅС‹С… СЌРЅРµСЂРіРµС‚РёС‡РµСЃРєРёС… СЂРµСЃСѓСЂСЃРѕРІ РґРѕРјРµРЅРЅРѕРіРѕ РіР°Р·Р° СЃ РІС‹СЂР°Р±РѕС‚РєРѕР№ СЌР»РµРєС‚СЂРѕСЌРЅРµСЂРіРёРё.
  Р Р°СЃС‡С‘С‚ РїРѕ С„РѕСЂРјСѓР»Р°Рј (1)вЂ“(13) РџР»Р°РЅР° РјРѕРЅРёС‚РѕСЂРёРЅРіР° РїСЂРѕРµРєС‚РЅРѕР№ РґРѕРєСѓРјРµРЅС‚Р°С†РёРё Рё РџСЂРёРєР°Р·Р° РњРёРЅРїСЂРёСЂРѕРґС‹ Р РѕСЃСЃРёРё
  РѕС‚ 27.05.2022 в„– 371. Р’РІРµРґРёС‚Рµ С„Р°РєС‚РёС‡РµСЃРєРё РёР·РјРµСЂРµРЅРЅС‹Рµ Р·РЅР°С‡РµРЅРёСЏ вЂ” СЃРёСЃС‚РµРјР° СЂР°СЃСЃС‡РёС‚Р°РµС‚ РІС‹Р±СЂРѕСЃС‹ РїРѕ РїСЂРѕРµРєС‚РЅРѕРјСѓ
  Рё Р±Р°Р·РѕРІРѕРјСѓ СЃС†РµРЅР°СЂРёСЏРј, СЃРѕРєСЂР°С‰РµРЅРёРµ РІС‹Р±СЂРѕСЃРѕРІ Рё РѕС‚РєР»РѕРЅРµРЅРёСЏ РѕС‚ РїСЂРѕРµРєС‚РЅРѕР№ РґРѕРєСѓРјРµРЅС‚Р°С†РёРё.</p>
  <div class="tags">
    <span>рџЏ­ РўР­Р¦-РџР’РЎ В· РєРѕС‚Р»РѕР°РіСЂРµРіР°С‚ РљРђ-11</span>
    <span>рџЏў РџРђРћ В«РЎРµРІРµСЂСЃС‚Р°Р»СЊВ», Рі. Р§РµСЂРµРїРѕРІРµС†</span>
    <span>рџ“ Р“РћРЎРў Р  РРЎРћ 14064-2</span>
    <span>рџ“ђ РџСЂРёРєР°Р· в„– 371</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ===========================================================================
#  РЎРѕСЃС‚РѕСЏРЅРёРµ
# ===========================================================================
INPUT_LABELS = {
    "fc_ng_proj": "Рџ4 В· Р Р°СЃС…РѕРґ РїСЂРёСЂ. РіР°Р·Р° РљРђ в„–1-11 (РїСЂРѕРµРєС‚), С‚С‹СЃ. РјВі",
    "ns_hws_pr":  "Рџ17 В· РџР°СЂ РЅР° Р“Р’РЎ (РїСЂРѕРµРєС‚), Р“РєР°Р»",
    "ns_bf_pr":   "Рџ18 В· РџР°СЂ РЅР° РїСЂРѕРёР·РІРѕРґСЃС‚РІРѕ (РїСЂРѕРµРєС‚), Р“РєР°Р»",
    "ns_bfp_pr":  "Рџ19 В· РџР°СЂ РЅР° РґРѕРјРµРЅРЅРѕРµ РїСЂРѕРёР·РІ. (РїСЂРѕРµРєС‚), Р“РєР°Р»",
    "ns_elg_pr":  "Рџ24 В· РџР°СЂ РЅР° СЌР»РµРєС‚СЂРѕСЌРЅРµСЂРіРёСЋ (РїСЂРѕРµРєС‚), Р“РєР°Р»",
    "elg_tg_pr":  "Рџ25 В· Р’С‹СЂР°Р±РѕС‚РєР° СЌ/СЌ (РїСЂРѕРµРєС‚), С‚С‹СЃ. РєР’С‚В·С‡",
    "nd_y":       "Рџ30 В· Р”РЅРµР№ РІ РїРµСЂРёРѕРґРµ",
    "ncv_ng":     "Рџ15 В· РљРѕСЌС„. РїРµСЂРµРІРѕРґР° РІ Сѓ.С‚. (РќРўРЎ), С‚ Сѓ.С‚./С‚С‹СЃ. РјВі",
    "ef_el":      "Рџ28 В· РљРѕСЌС„. РєРѕСЃРІ. РІС‹Р±СЂРѕСЃРѕРІ СЌ/СЌ, РєРі COв‚‚/РњР’С‚В·С‡",
}

def inputs_to_df(inputs):
    data = {"РџРµСЂРёРѕРґ": [i.year for i in inputs]}
    for key in INPUT_LABELS:
        data[INPUT_LABELS[key]] = [getattr(i, key) for i in inputs]
    return pd.DataFrame(data)

if "df" not in st.session_state:
    st.session_state.df = inputs_to_df(default_inputs())

# ===========================================================================
#  РЎР°Р№РґР±Р°СЂ вЂ” С„РёРєСЃРёСЂРѕРІР°РЅРЅС‹Рµ РїР°СЂР°РјРµС‚СЂС‹ Рё СЃРѕСЃС‚Р°РІ РіР°Р·Р°
# ===========================================================================
with st.sidebar:
    st.markdown("### вљ™пёЏ РџР°СЂР°РјРµС‚СЂС‹ РјРѕРґРµР»Рё")
    st.caption("Р¤РёРєСЃРёСЂРѕРІР°РЅРЅС‹Рµ РїР°СЂР°РјРµС‚СЂС‹ (РіСЂР°С„Р° В«С„РёРєСЃРёСЂРѕРІР°РЅВ», С‚Р°Р±Р». 7.6.1 PDD)")
    c = Constants()
    c.gwp_co2 = st.number_input("Рџ3 В· РџР“Рџ COв‚‚", value=float(c.gwp_co2), format="%.4f")
    c.of_ng = st.number_input("Рџ6 В· РљРѕСЌС„. РѕРєРёСЃР»РµРЅРёСЏ С‚РѕРїР»РёРІР°", value=float(c.of_ng), format="%.4f")
    c.rho_co2 = st.number_input("Рџ9 В· РџР»РѕС‚РЅРѕСЃС‚СЊ COв‚‚, РєРі/РјВі", value=float(c.rho_co2), format="%.4f")
    c.sfc_ng_bl = st.number_input("Рџ14 В· РЈРґ. СЂР°СЃС…РѕРґ РіР°Р·Р° РљРђ в„–1-10, РєРі Сѓ.С‚./Р“РєР°Р»",
                                  value=float(c.sfc_ng_bl), format="%.4f")
    c.elg_tg_bl = st.number_input("Рџ22 В· Р’С‹СЂР°Р±РѕС‚РєР° СЌ/СЌ (Р±Р°Р·РѕРІС‹Р№), С‚С‹СЃ. РєР’С‚В·С‡/РіРѕРґ",
                                  value=float(c.elg_tg_bl), format="%.3f")
    c.p_ow_bsl = st.number_input("Рџ26 В· Р”РѕР»СЏ С‚РµРїР»Р° РЅР° СЃРѕР±СЃС‚РІ. РЅСѓР¶РґС‹ (Р±Р°Р·Р°)",
                                 value=float(c.p_ow_bsl), format="%.4f")
    c.nd_bl = st.number_input("Рџ29 В· Р”РЅРµР№ РІ РіРѕРґСѓ (Р±Р°Р·РѕРІС‹Р№ СЃС†РµРЅР°СЂРёР№)", value=int(c.nd_bl), step=1)

    st.markdown("### рџ§Є РЎРѕСЃС‚Р°РІ РїСЂРёСЂРѕРґРЅРѕРіРѕ РіР°Р·Р°")
    st.caption("РћР±СЉС‘РјРЅС‹Рµ РґРѕР»Рё РєРѕРјРїРѕРЅРµРЅС‚РѕРІ (Рџ7), % РѕР±.")
    comp = {}
    for g in GAS_COMPONENTS:
        comp[g] = st.number_input(f"{g}  (n_C={N_CARBON[g]})",
                                  value=float(DEFAULT_COMPOSITION[g]), format="%.5f")
    ef_preview = emission_factor_ng(comp, c.rho_co2)
    st.success(f"EF (РєРѕСЌС„. РІС‹Р±СЂРѕСЃРѕРІ COв‚‚) = {ru(ef_preview,4)} С‚ COв‚‚/С‚С‹СЃ. РјВі")

    st.markdown("---")
    if st.button("в†є РЎР±СЂРѕСЃРёС‚СЊ Рє РґР°РЅРЅС‹Рј РџР”Р”", width="stretch"):
        st.session_state.df = inputs_to_df(default_inputs())
        st.rerun()

# ===========================================================================
#  Р’РІРѕРґ РґР°РЅРЅС‹С…
# ===========================================================================
st.markdown('<div class="sec"><span class="l"></span><h3>РСЃС…РѕРґРЅС‹Рµ РґР°РЅРЅС‹Рµ РїРѕ РїРµСЂРёРѕРґР°Рј</h3>'
            '<span class="hint">СЂРµР¶РёРј РїР»Р°РЅР° вЂ” Р·РЅР°С‡РµРЅРёСЏ РџР”Р” В· РїСЂРё РІРµСЂРёС„РёРєР°С†РёРё Р·Р°РјРµРЅРёС‚Рµ РЅР° РёР·РјРµСЂРµРЅРЅС‹Рµ</span></div>',
            unsafe_allow_html=True)
edited = st.data_editor(st.session_state.df, num_rows="dynamic", width="stretch", key="editor",
                        height=388)

def df_to_inputs(df):
    inv = {v: k for k, v in INPUT_LABELS.items()}
    inputs = []
    for _, row in df.iterrows():
        kwargs = {"year": int(row["РџРµСЂРёРѕРґ"]), "composition": dict(comp)}
        for label, key in inv.items():
            kwargs[key] = float(row[label])
        kwargs["nd_y"] = int(round(kwargs["nd_y"]))
        inputs.append(YearInput(**kwargs))
    return inputs

inputs = df_to_inputs(edited)
results = calc_period(inputs, c)
plan_map = {y: {"PE": PLAN["PE"][k], "BE": PLAN["BE"][k], "ER": PLAN["ER"][k]}
            for k, y in enumerate(DEFAULT_YEARS)}

# СЃСѓРјРјС‹
sPE = sum(r.pe for r in results); sBE = sum(r.be for r in results); sER = sum(r.er for r in results)
plan_ER = sum(plan_map[r.year]["ER"] for r in results if r.year in plan_map)
dER = sER - plan_ER
chip = (f'<span class="chip up">в–І +{ru(dER)} С‚ ({ru(dER/plan_ER*100,1) if plan_ER else "вЂ”"}%)</span>'
        if dER >= 0 else
        f'<span class="chip down">в–ј {ru(dER)} С‚ ({ru(dER/plan_ER*100,1) if plan_ER else "вЂ”"}%)</span>')

# ===========================================================================
#  KPI
# ===========================================================================
st.markdown(f"""
<div class="kpis">
  <div class="kpi b1"><div class="bar"></div>
    <div class="cap"><span class="ic">рџЏ­</span> Р’С‹Р±СЂРѕСЃС‹ РїРѕ РїСЂРѕРµРєС‚Сѓ В· ОЈ PE</div>
    <div class="val">{ru(sPE)}</div><div class="sub">С‚ COв‚‚-СЌРєРІ. Р·Р° Р·Р°С‡С‘С‚РЅС‹Р№ РїРµСЂРёРѕРґ</div></div>
  <div class="kpi b2"><div class="bar"></div>
    <div class="cap"><span class="ic">рџ“Љ</span> Р‘Р°Р·РѕРІР°СЏ Р»РёРЅРёСЏ В· ОЈ BE</div>
    <div class="val">{ru(sBE)}</div><div class="sub">С‚ COв‚‚-СЌРєРІ. Р·Р° Р·Р°С‡С‘С‚РЅС‹Р№ РїРµСЂРёРѕРґ</div></div>
  <div class="kpi b3"><div class="bar"></div>
    <div class="cap"><span class="ic">рџЊ±</span> РЎРѕРєСЂР°С‰РµРЅРёРµ В· ОЈ ER</div>
    <div class="val">{ru(sER)}</div><div class="sub">С‚ COв‚‚-СЌРєРІ. В· СѓРіР»РµСЂРѕРґРЅС‹Рµ РµРґРёРЅРёС†С‹</div></div>
  <div class="kpi b4"><div class="bar"></div>
    <div class="cap"><span class="ic">рџЋЇ</span> РћС‚РєР»РѕРЅРµРЅРёРµ РѕС‚ РїР»Р°РЅР° РџР”Р”</div>
    <div class="val">{ru(dER)}</div>{chip}</div>
</div>
""", unsafe_allow_html=True)

# ===========================================================================
#  РўР°Р±Р»РёС†Р° СЂРµР·СѓР»СЊС‚Р°С‚РѕРІ (Styler)
# ===========================================================================
rows = []
for r in results:
    p = plan_map.get(r.year, {})
    rows.append({
        "РџРµСЂРёРѕРґ": r.year,
        "EF, С‚/С‚С‹СЃ.РјВі": round(r.ef_co2_ng, 4),
        "PE, С‚ COв‚‚-СЌРєРІ.": round(r.pe),
        "PE РїР»Р°РЅ": p.get("PE"),
        "О” PE": (round(r.pe) - p["PE"]) if "PE" in p else None,
        "BE, С‚ COв‚‚-СЌРєРІ.": round(r.be),
        "BE РїР»Р°РЅ": p.get("BE"),
        "О” BE": (round(r.be) - p["BE"]) if "BE" in p else None,
        "ER, С‚ COв‚‚-СЌРєРІ.": round(r.er),
        "ER РїР»Р°РЅ": p.get("ER"),
        "О” ER": (round(r.er) - p["ER"]) if "ER" in p else None,
    })
out = pd.DataFrame(rows)

PLOT_BG = "rgba(0,0,0,0)"
years = [r.year for r in results]

def style_good(col, good_positive):
    def f(v):
        if pd.isna(v):
            return "color:#64748b"
        if abs(v) < 0.5:
            return "color:#8a99b5"
        good = v >= 0 if good_positive else v <= 0
        return f"color:{'#34d399' if good else '#fb7185'};font-weight:700"
    return f

def render_results_table(df):
    sty = (df.style
           .format("{:,.0f}", subset=[c for c in df.columns if c not in ("РџРµСЂРёРѕРґ", "EF, С‚/С‚С‹СЃ.РјВі")],
                   na_rep="вЂ”", thousands=" ")
           .format("{:.4f}", subset=["EF, С‚/С‚С‹СЃ.РјВі"])
           .format("{:.0f}", subset=["РџРµСЂРёРѕРґ"])
           .map(style_good("О” PE", False), subset=["О” PE"])
           .map(style_good("О” BE", True), subset=["О” BE"])
           .map(style_good("О” ER", True), subset=["О” ER"]))
    st.dataframe(sty, width="stretch", hide_index=True, height=420)

# ===========================================================================
#  Р“СЂР°С„РёРєРё Plotly (С‚С‘РјРЅС‹Рµ)
# ===========================================================================
def fig_layout(fig, h=360, title=None):
    fig.update_layout(
        template="plotly_dark", height=h, title=title,
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
        margin=dict(l=10, r=10, t=40 if title else 14, b=10),
        font=dict(family="Manrope, sans-serif", color="#cdd9ef", size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        hoverlabel=dict(bgcolor="#111a2e", bordercolor="#3b82f6"),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,.06)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(255,255,255,.06)", zeroline=False)
    return fig

def chart_er():
    er = [r.er for r in results]
    plan = [plan_map.get(y, {}).get("ER") for y in years]
    fig = go.Figure()
    fig.add_bar(x=years, y=er, name="ER (С„Р°РєС‚/СЂР°СЃС‡С‘С‚)",
                marker=dict(color=er, colorscale=[[0, "#1d4ed8"], [1, "#22d3ee"]],
                            line=dict(width=0)),
                hovertemplate="%{x}: %{y:,.0f} С‚<extra></extra>")
    if any(p is not None for p in plan):
        fig.add_scatter(x=years, y=plan, name="РџР»Р°РЅ РџР”Р”", mode="lines+markers",
                        line=dict(color="#fbbf24", width=2, dash="dot"),
                        marker=dict(size=7, color="#fbbf24"),
                        hovertemplate="%{x}: РїР»Р°РЅ %{y:,.0f} С‚<extra></extra>")
    return fig_layout(fig)

def chart_pe_be():
    fig = go.Figure()
    fig.add_bar(x=years, y=[r.be for r in results], name="BE вЂ” Р±Р°Р·РѕРІС‹Р№ СЃС†РµРЅР°СЂРёР№",
                marker_color="#64748b", hovertemplate="%{x}: %{y:,.0f} С‚<extra></extra>")
    fig.add_bar(x=years, y=[r.pe for r in results], name="PE вЂ” РїСЂРѕРµРєС‚РЅС‹Р№ СЃС†РµРЅР°СЂРёР№",
                marker_color="#3b82f6", hovertemplate="%{x}: %{y:,.0f} С‚<extra></extra>")
    fig.update_layout(barmode="group")
    return fig_layout(fig)

def chart_cumulative():
    er = [r.er for r in results]
    cum, s = [], 0
    for v in er:
        s += v; cum.append(s)
    fig = go.Figure()
    fig.add_scatter(x=years, y=cum, mode="lines+markers", name="РќР°РєРѕРїР»РµРЅРЅРѕРµ ER",
                    line=dict(color="#34d399", width=3, shape="spline"),
                    fill="tozeroy", fillcolor="rgba(52,211,153,.12)",
                    marker=dict(size=7, color="#34d399"),
                    hovertemplate="Рє %{x}: %{y:,.0f} С‚<extra></extra>")
    return fig_layout(fig)

def chart_composition():
    labels = [g for g in GAS_COMPONENTS if comp.get(g, 0) > 0]
    vals = [comp[g] for g in labels]
    fig = go.Figure(go.Pie(labels=labels, values=vals, hole=.62,
                           marker=dict(colors=["#3b82f6", "#22d3ee", "#a78bfa", "#34d399",
                                               "#fbbf24", "#fb7185", "#94a3b8", "#f0abfc"],
                                       line=dict(color="#0a0f1c", width=2)),
                           textinfo="label+percent", textfont=dict(size=11),
                           hovertemplate="%{label}: %{value:.3f}% РѕР±.<extra></extra>"))
    return fig_layout(fig, h=360)

# ===========================================================================
#  Р’РєР»Р°РґРєРё
# ===========================================================================
tab_res, tab_chart, tab_method = st.tabs(["рџ“‹  Р РµР·СѓР»СЊС‚Р°С‚С‹", "рџ“€  Р“СЂР°С„РёРєРё", "рџ“ђ  РњРµС‚РѕРґРёРєР°"])

with tab_res:
    st.markdown('<div class="sec"><span class="l"></span><h3>Р’С‹Р±СЂРѕСЃС‹, СЃРѕРєСЂР°С‰РµРЅРёСЏ Рё РѕС‚РєР»РѕРЅРµРЅРёСЏ РѕС‚ РџР”Р”</h3></div>',
                unsafe_allow_html=True)
    render_results_table(out)

    # СЃС‚СЂРѕРєР° РРўРћР“Рћ
    tot = pd.DataFrame([{
        "РџРµСЂРёРѕРґ": "РРўРћР“Рћ", "EF, С‚/С‚С‹СЃ.РјВі": None,
        "PE, С‚ COв‚‚-СЌРєРІ.": round(sPE), "PE РїР»Р°РЅ": sum(p for p in [plan_map.get(y, {}).get("PE") for y in years] if p),
        "О” PE": round(sPE) - sum(p for p in [plan_map.get(y, {}).get("PE") for y in years] if p),
        "BE, С‚ COв‚‚-СЌРєРІ.": round(sBE), "BE РїР»Р°РЅ": sum(p for p in [plan_map.get(y, {}).get("BE") for y in years] if p),
        "О” BE": round(sBE) - sum(p for p in [plan_map.get(y, {}).get("BE") for y in years] if p),
        "ER, С‚ COв‚‚-СЌРєРІ.": round(sER), "ER РїР»Р°РЅ": plan_ER, "О” ER": round(dER),
    }])
    st.caption("РС‚РѕРі Р·Р° Р·Р°С‡С‘С‚РЅС‹Р№ РїРµСЂРёРѕРґ")
    st.dataframe(tot.style.format(lambda v: ru(v) if isinstance(v, (int, float)) else v),
                 width="stretch", hide_index=True)

    def to_excel(df_in, df_out):
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            df_in.to_excel(w, sheet_name="Р’С…РѕРґРЅС‹Рµ РґР°РЅРЅС‹Рµ", index=False)
            df_out.to_excel(w, sheet_name="Р РµР·СѓР»СЊС‚Р°С‚С‹", index=False)
        return buf.getvalue()

    st.download_button("в¬‡  РЎРєР°С‡Р°С‚СЊ СЂРµР·СѓР»СЊС‚Р°С‚С‹ РІ Excel", data=to_excel(edited, out),
                       file_name="Р РµР·СѓР»СЊС‚Р°С‚С‹_СЂР°СЃС‡С‘С‚Р°_РџР“.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

with tab_chart:
    a, b = st.columns(2)
    with a:
        st.markdown('<div class="sec"><span class="l"></span><h3>РЎРѕРєСЂР°С‰РµРЅРёРµ РІС‹Р±СЂРѕСЃРѕРІ ER</h3></div>',
                    unsafe_allow_html=True)
        st.plotly_chart(chart_er(), width="stretch", config={"displayModeBar": False})
    with b:
        st.markdown('<div class="sec"><span class="l"></span><h3>РџСЂРѕРµРєС‚РЅС‹Р№ Рё Р±Р°Р·РѕРІС‹Р№ СЃС†РµРЅР°СЂРёРё</h3></div>',
                    unsafe_allow_html=True)
        st.plotly_chart(chart_pe_be(), width="stretch", config={"displayModeBar": False})
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="sec"><span class="l"></span><h3>РќР°РєРѕРїР»РµРЅРЅРѕРµ СЃРѕРєСЂР°С‰РµРЅРёРµ</h3></div>',
                    unsafe_allow_html=True)
        st.plotly_chart(chart_cumulative(), width="stretch", config={"displayModeBar": False})
    with c2:
        st.markdown('<div class="sec"><span class="l"></span><h3>РЎРѕСЃС‚Р°РІ РїСЂРёСЂРѕРґРЅРѕРіРѕ РіР°Р·Р°</h3></div>',
                    unsafe_allow_html=True)
        st.plotly_chart(chart_composition(), width="stretch", config={"displayModeBar": False})

with tab_method:
    st.markdown('<div class="sec"><span class="l"></span><h3>Р¤РѕСЂРјСѓР»С‹ РџР»Р°РЅР° РјРѕРЅРёС‚РѕСЂРёРЅРіР° (1)вЂ“(13)</h3></div>',
                unsafe_allow_html=True)
    st.markdown("""
<div class="formula">
РџСЂРѕРµРєС‚РЅС‹Р№ СЃС†РµРЅР°СЂРёР№:<br>
(3)  EF = (ОЈ Wбµў В· n_C,i) В· ПЃ_COв‚‚ В· 10вЃ»ВІ        вЂ” С‚ COв‚‚/С‚С‹СЃ. РјВі<br>
(2)  PE_FC = FC_РџР“,1-11 В· EF В· OF<br>
(1)  PE = PE_FC В· GWP<br><br>
Р‘Р°Р·РѕРІС‹Р№ СЃС†РµРЅР°СЂРёР№:<br>
(9)  sfc = РїР°СЂ_СЌР»,РїСЂ / ELG_РїСЂ &nbsp;&nbsp; (8) РїР°СЂ_СЌР»,Р±Р°Р· = ELG_Р±Р°Р· В· sfc<br>
(10) РїР°СЂ_СЃРЅ,Р±Р°Р· = (РїР°СЂ_РїСЂ + РїР°СЂ_РіРІСЃ + РїР°СЂ_РґРї + РїР°СЂ_СЌР»,Р±Р°Р·) В· p/(1в€’p)<br>
(7)  SG_1-10 = РїР°СЂ_РіРІСЃ + РїР°СЂ_РїСЂ + РїР°СЂ_РґРї + РїР°СЂ_СЌР»,Р±Р°Р· + РїР°СЂ_СЃРЅ,Р±Р°Р·<br>
(6)  FC_РџР“,1-10 = SG_1-10 В· SFC / Рљ_РџР“ / 1000 &nbsp;&nbsp; (5) BE_FC = FC_РџР“,1-10 В· EF В· OF<br>
(12) EC_Р±Р°Р· = ELG_РїСЂ в€’ ELG_Р±Р°Р· В· N_y/N_Р±Р°Р· &nbsp;&nbsp; (11) BE_СЌР» = EC_Р±Р°Р· В· EF_СЌР» / 1000<br>
(4)  BE = (BE_FC + BE_СЌР») В· GWP<br><br>
РЎРѕРєСЂР°С‰РµРЅРёРµ РІС‹Р±СЂРѕСЃРѕРІ:<br>
(13) ER = BE в€’ PE
</div>
""", unsafe_allow_html=True)
    st.markdown("""
<p class="note" style="margin-top:14px">
<b>РљРѕРЅС‚СЂРѕР»СЊРЅР°СЏ РїСЂРѕРІРµСЂРєР°.</b> РџСЂРё РёСЃС…РѕРґРЅС‹С… РґР°РЅРЅС‹С… РїСЂРѕРµРєС‚РЅРѕР№ РґРѕРєСѓРјРµРЅС‚Р°С†РёРё СЃРёСЃС‚РµРјР° РІРѕСЃРїСЂРѕРёР·РІРѕРґРёС‚
РїР»Р°РЅРѕРІС‹Рµ РёС‚РѕРіРё PDD Р·Р° 2025вЂ“2034 РіРі.: ОЈPE в‰€ 1 018 377; ОЈBE в‰€ 3 509 570;
<b>ОЈER в‰€ 2 491 193 С‚ COв‚‚-СЌРєРІ.</b> (С‚Р°Р±Р»РёС†Р° 8.4.1 РїСЂРѕРµРєС‚РЅРѕР№ РґРѕРєСѓРјРµРЅС‚Р°С†РёРё).<br><br>
<b>РСЃС‚РѕС‡РЅРёРєРё:</b> РїСЂРѕРµРєС‚РЅР°СЏ РґРѕРєСѓРјРµРЅС‚Р°С†РёСЏ РєР»РёРјР°С‚РёС‡РµСЃРєРѕРіРѕ РїСЂРѕРµРєС‚Р° (PDD, СЂР°Р·РґРµР»С‹ 5, 7, 8);
РџСЂРёРєР°Р· РњРёРЅРїСЂРёСЂРѕРґС‹ Р РѕСЃСЃРёРё РѕС‚ 27.05.2022 в„– 371; Р Р°СЃРїРѕСЂСЏР¶РµРЅРёРµ РџСЂР°РІРёС‚РµР»СЊСЃС‚РІР° Р Р¤ РѕС‚ 22.10.2021 в„– 2979-СЂ.
</p>
""", unsafe_allow_html=True)

st.markdown('<p class="note" style="text-align:center;margin-top:26px;opacity:.7">'
            'РљР»РёРјР°С‚РёС‡РµСЃРєРёР№ РїСЂРѕРµРєС‚ РџРђРћ В«РЎРµРІРµСЂСЃС‚Р°Р»СЊВ» В· РўР­Р¦-РџР’РЎ В· РљРђ-11 &nbsp;В·&nbsp; '
            'СЂР°СЃС‡С‘С‚ РїРѕ РџСЂРёРєР°Р·Сѓ РњРёРЅРїСЂРёСЂРѕРґС‹ Р РѕСЃСЃРёРё в„– 371</p>', unsafe_allow_html=True)
