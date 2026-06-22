# -*- coding: utf-8 -*-
"""Страница «Калькулятор» — расчёт выбросов, сокращений и отклонений от ПДД."""
import io
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from engine import (Constants, YearInput, calc_period, default_inputs,
                    DEFAULT_COMPOSITION, GAS_COMPONENTS, N_CARBON, PLAN,
                    DEFAULT_YEARS, emission_factor_ng)


def ru(x, d=0):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return "—"
    return f"{x:,.{d}f}".replace(",", " ").replace(".", ",")


# ---------------------------------------------------------------- HERO
st.markdown("""
<div class="hero">
  <span class="badge">● Климатический проект · стадия верификации</span>
  <h1>Калькулятор выбросов и сокращений выбросов парниковых газов</h1>
  <p>Полезная утилизация вторичных энергетических ресурсов доменного газа с выработкой электроэнергии.
  Расчёт по формулам (1)–(13) Плана мониторинга проектной документации и Приказа Минприроды России
  от 27.05.2022 № 371. Введите фактически измеренные значения — система рассчитает выбросы по проектному
  и базовому сценариям, сокращение выбросов и отклонения от проектной документации.</p>
  <div class="tags">
    <span>🏭 ТЭЦ-ПВС · котлоагрегат КА-11</span>
    <span>🏢 ПАО «Северсталь», г. Череповец</span>
    <span>📘 ГОСТ Р ИСО 14064-2</span>
    <span>📐 Приказ № 371</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------- состояние
INPUT_LABELS = {
    "fc_ng_proj": "П4 · Расход прир. газа КА №1-11 (проект), тыс. м³",
    "ns_hws_pr":  "П17 · Пар на ГВС (проект), Гкал",
    "ns_bf_pr":   "П18 · Пар на производство (проект), Гкал",
    "ns_bfp_pr":  "П19 · Пар на доменное произв. (проект), Гкал",
    "ns_elg_pr":  "П24 · Пар на электроэнергию (проект), Гкал",
    "elg_tg_pr":  "П25 · Выработка э/э (проект), тыс. кВт·ч",
    "nd_y":       "П30 · Дней в периоде",
    "ncv_ng":     "П15 · Коэф. перевода в у.т. (НТС), т у.т./тыс. м³",
    "ef_el":      "П28 · Коэф. косв. выбросов э/э, кг CO₂/МВт·ч",
}


def inputs_to_df(inputs):
    data = {"Период": [i.year for i in inputs]}
    for key in INPUT_LABELS:
        data[INPUT_LABELS[key]] = [getattr(i, key) for i in inputs]
    return pd.DataFrame(data)


if "df" not in st.session_state:
    st.session_state.df = inputs_to_df(default_inputs())

# ---------------------------------------------------------------- сайдбар
with st.sidebar:
    st.markdown("### ⚙️ Параметры модели")
    st.caption("Фиксированные параметры (графа «фиксирован», табл. 7.6.1 PDD)")
    c = Constants()
    c.gwp_co2 = st.number_input("П3 · ПГП CO₂", value=float(c.gwp_co2), format="%.4f")
    c.of_ng = st.number_input("П6 · Коэф. окисления топлива", value=float(c.of_ng), format="%.4f")
    c.rho_co2 = st.number_input("П9 · Плотность CO₂, кг/м³", value=float(c.rho_co2), format="%.4f")
    c.sfc_ng_bl = st.number_input("П14 · Уд. расход газа КА №1-10, кг у.т./Гкал",
                                  value=float(c.sfc_ng_bl), format="%.4f")
    c.elg_tg_bl = st.number_input("П22 · Выработка э/э (базовый), тыс. кВт·ч/год",
                                  value=float(c.elg_tg_bl), format="%.3f")
    c.p_ow_bsl = st.number_input("П26 · Доля тепла на собств. нужды (база)",
                                 value=float(c.p_ow_bsl), format="%.4f")
    c.nd_bl = st.number_input("П29 · Дней в году (базовый сценарий)", value=int(c.nd_bl), step=1)

    st.markdown("### 🧪 Состав природного газа")
    st.caption("Объёмные доли компонентов (П7), % об.")
    comp = {}
    for g in GAS_COMPONENTS:
        comp[g] = st.number_input(f"{g}  (n_C={N_CARBON[g]})",
                                  value=float(DEFAULT_COMPOSITION[g]), format="%.5f")
    ef_preview = emission_factor_ng(comp, c.rho_co2)
    st.success(f"EF (коэф. выбросов CO₂) = {ru(ef_preview,4)} т CO₂/тыс. м³")

    st.markdown("---")
    if st.button("↺ Сбросить к данным ПДД", width="stretch"):
        st.session_state.df = inputs_to_df(default_inputs())
        st.rerun()

# ---------------------------------------------------------------- ввод
st.markdown('<div class="sec"><span class="l"></span><h3>Исходные данные по периодам</h3>'
            '<span class="hint">режим плана — значения ПДД · при верификации замените на измеренные</span></div>',
            unsafe_allow_html=True)
edited = st.data_editor(st.session_state.df, num_rows="dynamic", width="stretch", key="editor",
                        height=388)


def df_to_inputs(df):
    inv = {v: k for k, v in INPUT_LABELS.items()}
    inputs = []
    for _, row in df.iterrows():
        kwargs = {"year": int(row["Период"]), "composition": dict(comp)}
        for label, key in inv.items():
            kwargs[key] = float(row[label])
        kwargs["nd_y"] = int(round(kwargs["nd_y"]))
        inputs.append(YearInput(**kwargs))
    return inputs


inputs = df_to_inputs(edited)
results = calc_period(inputs, c)
plan_map = {y: {"PE": PLAN["PE"][k], "BE": PLAN["BE"][k], "ER": PLAN["ER"][k]}
            for k, y in enumerate(DEFAULT_YEARS)}

sPE = sum(r.pe for r in results); sBE = sum(r.be for r in results); sER = sum(r.er for r in results)
plan_ER = sum(plan_map[r.year]["ER"] for r in results if r.year in plan_map)
dER = sER - plan_ER
chip = (f'<span class="chip up">▲ +{ru(dER)} т ({ru(dER/plan_ER*100,1) if plan_ER else "—"}%)</span>'
        if dER >= 0 else
        f'<span class="chip down">▼ {ru(dER)} т ({ru(dER/plan_ER*100,1) if plan_ER else "—"}%)</span>')

# ---------------------------------------------------------------- KPI
st.markdown(f"""
<div class="kpis">
  <div class="kpi b1"><div class="bar"></div>
    <div class="cap"><span class="ic">🏭</span> Выбросы по проекту · Σ PE</div>
    <div class="val">{ru(sPE)}</div><div class="sub">т CO₂-экв. за зачётный период</div></div>
  <div class="kpi b2"><div class="bar"></div>
    <div class="cap"><span class="ic">📊</span> Базовая линия · Σ BE</div>
    <div class="val">{ru(sBE)}</div><div class="sub">т CO₂-экв. за зачётный период</div></div>
  <div class="kpi b3"><div class="bar"></div>
    <div class="cap"><span class="ic">🌱</span> Сокращение · Σ ER</div>
    <div class="val">{ru(sER)}</div><div class="sub">т CO₂-экв. · углеродные единицы</div></div>
  <div class="kpi b4"><div class="bar"></div>
    <div class="cap"><span class="ic">🎯</span> Отклонение от плана ПДД</div>
    <div class="val">{ru(dER)}</div>{chip}</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------- таблица
rows = []
for r in results:
    p = plan_map.get(r.year, {})
    rows.append({
        "Период": r.year,
        "EF, т/тыс.м³": round(r.ef_co2_ng, 4),
        "PE, т CO₂-экв.": round(r.pe),
        "PE план": p.get("PE"),
        "Δ PE": (round(r.pe) - p["PE"]) if "PE" in p else None,
        "BE, т CO₂-экв.": round(r.be),
        "BE план": p.get("BE"),
        "Δ BE": (round(r.be) - p["BE"]) if "BE" in p else None,
        "ER, т CO₂-экв.": round(r.er),
        "ER план": p.get("ER"),
        "Δ ER": (round(r.er) - p["ER"]) if "ER" in p else None,
    })
out = pd.DataFrame(rows)

PLOT_BG = "rgba(0,0,0,0)"
years = [r.year for r in results]


def style_good(good_positive):
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
           .format("{:,.0f}", subset=[c2 for c2 in df.columns if c2 not in ("Период", "EF, т/тыс.м³")],
                   na_rep="—", thousands=" ")
           .format("{:.4f}", subset=["EF, т/тыс.м³"])
           .format("{:.0f}", subset=["Период"])
           .map(style_good(False), subset=["Δ PE"])
           .map(style_good(True), subset=["Δ BE"])
           .map(style_good(True), subset=["Δ ER"]))
    st.dataframe(sty, width="stretch", hide_index=True, height=420)


# ---------------------------------------------------------------- графики
def fig_layout(fig, h=360):
    fig.update_layout(
        template="plotly_dark", height=h,
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
        margin=dict(l=10, r=10, t=14, b=10),
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
    fig.add_bar(x=years, y=er, name="ER (факт/расчёт)",
                marker=dict(color=er, colorscale=[[0, "#1d4ed8"], [1, "#22d3ee"]], line=dict(width=0)),
                hovertemplate="%{x}: %{y:,.0f} т<extra></extra>")
    if any(p is not None for p in plan):
        fig.add_scatter(x=years, y=plan, name="План ПДД", mode="lines+markers",
                        line=dict(color="#fbbf24", width=2, dash="dot"),
                        marker=dict(size=7, color="#fbbf24"),
                        hovertemplate="%{x}: план %{y:,.0f} т<extra></extra>")
    return fig_layout(fig)


def chart_pe_be():
    fig = go.Figure()
    fig.add_bar(x=years, y=[r.be for r in results], name="BE — базовый сценарий",
                marker_color="#64748b", hovertemplate="%{x}: %{y:,.0f} т<extra></extra>")
    fig.add_bar(x=years, y=[r.pe for r in results], name="PE — проектный сценарий",
                marker_color="#3b82f6", hovertemplate="%{x}: %{y:,.0f} т<extra></extra>")
    fig.update_layout(barmode="group")
    return fig_layout(fig)


def chart_cumulative():
    cum, s = [], 0
    for v in [r.er for r in results]:
        s += v; cum.append(s)
    fig = go.Figure()
    fig.add_scatter(x=years, y=cum, mode="lines+markers", name="Накопленное ER",
                    line=dict(color="#34d399", width=3, shape="spline"),
                    fill="tozeroy", fillcolor="rgba(52,211,153,.12)",
                    marker=dict(size=7, color="#34d399"),
                    hovertemplate="к %{x}: %{y:,.0f} т<extra></extra>")
    return fig_layout(fig)


def chart_composition():
    labels = [g for g in GAS_COMPONENTS if comp.get(g, 0) > 0]
    vals = [comp[g] for g in labels]
    ch4 = comp.get("CH4", 0)
    fig = go.Figure(go.Pie(labels=labels, values=vals, hole=.64, sort=False,
                           marker=dict(colors=["#3b82f6", "#22d3ee", "#a78bfa", "#34d399",
                                               "#fbbf24", "#fb7185", "#94a3b8", "#f0abfc"],
                                       line=dict(color="#0a0f1c", width=2)),
                           textposition="inside", textinfo="percent", insidetextorientation="horizontal",
                           textfont=dict(size=12, color="#0a0f1c"),
                           hovertemplate="%{label}: %{value:.3f}% об.<extra></extra>"))
    fig.update_layout(uniformtext=dict(minsize=11, mode="hide"),
                      annotations=[dict(text=f"CH₄<br><b>{ch4:.1f}%</b>", x=0.5, y=0.5,
                                        font=dict(size=15, color="#eaf1fc"), showarrow=False)])
    return fig_layout(fig)


# ---------------------------------------------------------------- вкладки
tab_res, tab_chart = st.tabs(["📋  Результаты", "📈  Графики"])

with tab_res:
    st.markdown('<div class="sec"><span class="l"></span><h3>Выбросы, сокращения и отклонения от ПДД</h3></div>',
                unsafe_allow_html=True)
    render_results_table(out)

    pe_plan = sum(p for p in [plan_map.get(y, {}).get("PE") for y in years] if p)
    be_plan = sum(p for p in [plan_map.get(y, {}).get("BE") for y in years] if p)
    tot = pd.DataFrame([{
        "Период": "ИТОГО", "EF, т/тыс.м³": None,
        "PE, т CO₂-экв.": round(sPE), "PE план": pe_plan, "Δ PE": round(sPE) - pe_plan,
        "BE, т CO₂-экв.": round(sBE), "BE план": be_plan, "Δ BE": round(sBE) - be_plan,
        "ER, т CO₂-экв.": round(sER), "ER план": plan_ER, "Δ ER": round(dER),
    }])
    st.caption("Итог за зачётный период")
    st.dataframe(tot.style.format(lambda v: ru(v) if isinstance(v, (int, float)) else v),
                 width="stretch", hide_index=True)

    def to_excel(df_in, df_out):
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            df_in.to_excel(w, sheet_name="Входные данные", index=False)
            df_out.to_excel(w, sheet_name="Результаты", index=False)
        return buf.getvalue()

    st.download_button("⬇  Скачать результаты в Excel", data=to_excel(edited, out),
                       file_name="Результаты_расчёта_ПГ.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

with tab_chart:
    a, b = st.columns(2)
    with a:
        st.markdown('<div class="sec"><span class="l"></span><h3>Сокращение выбросов ER</h3></div>',
                    unsafe_allow_html=True)
        st.plotly_chart(chart_er(), width="stretch", config={"displayModeBar": False})
    with b:
        st.markdown('<div class="sec"><span class="l"></span><h3>Проектный и базовый сценарии</h3></div>',
                    unsafe_allow_html=True)
        st.plotly_chart(chart_pe_be(), width="stretch", config={"displayModeBar": False})
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="sec"><span class="l"></span><h3>Накопленное сокращение</h3></div>',
                    unsafe_allow_html=True)
        st.plotly_chart(chart_cumulative(), width="stretch", config={"displayModeBar": False})
    with c2:
        st.markdown('<div class="sec"><span class="l"></span><h3>Состав природного газа</h3></div>',
                    unsafe_allow_html=True)
        st.plotly_chart(chart_composition(), width="stretch", config={"displayModeBar": False})

st.markdown('<p class="note" style="text-align:center;margin-top:26px;opacity:.7">'
            'Климатический проект ПАО «Северсталь» · ТЭЦ-ПВС · КА-11 &nbsp;·&nbsp; '
            'расчёт по Приказу Минприроды России № 371 &nbsp;·&nbsp; '
            'подробности — на странице «Инструкция и методика»</p>', unsafe_allow_html=True)
