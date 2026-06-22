# -*- coding: utf-8 -*-
"""
Streamlit-интерфейс программы расчёта выбросов и сокращений выбросов ПГ.

Запуск:
    pip install -r requirements.txt
    streamlit run app.py

Программа использует расчётное ядро engine.py (формулы 1-13 PDD и Приказа № 371).
"""
import io
import pandas as pd
import streamlit as st

from engine import (Constants, YearInput, calc_period, default_inputs,
                    DEFAULT_COMPOSITION, GAS_COMPONENTS, N_CARBON, PLAN, DEFAULT_YEARS)

st.set_page_config(page_title="Расчёт сокращений выбросов ПГ — КА-11", layout="wide")

st.title("Калькулятор выбросов и сокращений выбросов парниковых газов")
st.caption("Климатический проект «Полезная утилизация вторичных энергетических ресурсов доменного газа "
           "с выработкой электроэнергии» — ТЭЦ-ПВС, КА-11, ПАО «Северсталь». "
           "Формулы (1)–(13) Плана мониторинга PDD и Приказа Минприроды России № 371.")

# --------------------------------------------------------------------------
#  Состояние: таблица входных данных по периодам.
# --------------------------------------------------------------------------
INPUT_LABELS = {
    "fc_ng_proj": "П4 Расход прир. газа КА №1-11 (проект), тыс. м³",
    "ns_hws_pr":  "П17 Пар на ГВС (проект), Гкал",
    "ns_bf_pr":   "П18 Пар на производство (проект), Гкал",
    "ns_bfp_pr":  "П19 Пар на доменное произв. (проект), Гкал",
    "ns_elg_pr":  "П24 Пар на электроэнергию (проект), Гкал",
    "elg_tg_pr":  "П25 Выработка э/э (проект), тыс. кВт·ч",
    "nd_y":       "П30 Дней в периоде",
    "ncv_ng":     "П15 Коэф. перевода в у.т. (НТС), т у.т./тыс. м³",
    "ef_el":      "П28 Коэф. косв. выбросов э/э, кг CO₂/МВт·ч",
}

def inputs_to_df(inputs):
    data = {"Период": [i.year for i in inputs]}
    for key in INPUT_LABELS:
        data[INPUT_LABELS[key]] = [getattr(i, key) for i in inputs]
    return pd.DataFrame(data)

if "df" not in st.session_state:
    st.session_state.df = inputs_to_df(default_inputs())

# --------------------------------------------------------------------------
#  Сайдбар: фиксированные параметры и состав газа.
# --------------------------------------------------------------------------
with st.sidebar:
    st.header("Фиксированные параметры")
    c = Constants()
    c.gwp_co2 = st.number_input("П3 ПГП CO₂", value=float(c.gwp_co2), format="%.4f")
    c.of_ng = st.number_input("П6 Коэф. окисления топлива", value=float(c.of_ng), format="%.4f")
    c.rho_co2 = st.number_input("П9 Плотность CO₂, кг/м³", value=float(c.rho_co2), format="%.4f")
    c.sfc_ng_bl = st.number_input("П14 Уд. расход газа КА №1-10, кг у.т./Гкал",
                                  value=float(c.sfc_ng_bl), format="%.4f")
    c.elg_tg_bl = st.number_input("П22 Выработка э/э (базовый), тыс. кВт·ч/год",
                                  value=float(c.elg_tg_bl), format="%.3f")
    c.p_ow_bsl = st.number_input("П26 Доля тепла на собств. нужды (база)",
                                 value=float(c.p_ow_bsl), format="%.4f")
    c.nd_bl = st.number_input("П29 Дней в году (базовый сценарий)", value=int(c.nd_bl), step=1)

    st.header("Состав природного газа (П7), % об.")
    comp = {}
    for g in GAS_COMPONENTS:
        comp[g] = st.number_input(f"{g} (n_C={N_CARBON[g]})",
                                  value=float(DEFAULT_COMPOSITION[g]), format="%.5f")

    st.markdown("---")
    col_a, col_b = st.columns(2)
    if col_a.button("Сбросить к ПДД", width="stretch"):
        st.session_state.df = inputs_to_df(default_inputs())
        st.rerun()

# --------------------------------------------------------------------------
#  Ввод данных по периодам (редактируемая таблица).
# --------------------------------------------------------------------------
st.subheader("Измеряемые параметры по периодам")
st.caption("В «режиме плана» показаны прогнозные значения PDD; при верификации замените их на фактически "
           "измеренные. Можно добавлять/удалять строки.")
edited = st.data_editor(st.session_state.df, num_rows="dynamic", width="stretch",
                        key="editor")

# --------------------------------------------------------------------------
#  Расчёт.
# --------------------------------------------------------------------------
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

# Сопоставление с планом PDD по году.
plan_map = {y: {"PE": PLAN["PE"][k], "BE": PLAN["BE"][k], "ER": PLAN["ER"][k]}
            for k, y in enumerate(DEFAULT_YEARS)}

rows = []
for r in results:
    p = plan_map.get(r.year, {})
    rows.append({
        "Период": r.year,
        "EF, т/тыс.м³": round(r.ef_co2_ng, 4),
        "PE (проект), т CO₂-экв.": round(r.pe),
        "PE план": p.get("PE", None),
        "Δ PE": (round(r.pe) - p["PE"]) if "PE" in p else None,
        "BE (базовый), т CO₂-экв.": round(r.be),
        "BE план": p.get("BE", None),
        "Δ BE": (round(r.be) - p["BE"]) if "BE" in p else None,
        "ER (сокращение), т CO₂-экв.": round(r.er),
        "ER план": p.get("ER", None),
        "Δ ER": (round(r.er) - p["ER"]) if "ER" in p else None,
    })
out = pd.DataFrame(rows)

# --------------------------------------------------------------------------
#  KPI.
# --------------------------------------------------------------------------
sPE = sum(r.pe for r in results)
sBE = sum(r.be for r in results)
sER = sum(r.er for r in results)
plan_ER = sum(plan_map[r.year]["ER"] for r in results if r.year in plan_map)
k1, k2, k3, k4 = st.columns(4)
k1.metric("Σ PE (проект), т CO₂-экв.", f"{sPE:,.0f}".replace(",", " "))
k2.metric("Σ BE (базовый), т CO₂-экв.", f"{sBE:,.0f}".replace(",", " "))
k3.metric("Σ ER (сокращение), т CO₂-экв.", f"{sER:,.0f}".replace(",", " "))
if plan_ER:
    d = sER - plan_ER
    k4.metric("Отклонение Σ ER от плана", f"{d:,.0f}".replace(",", " "),
              delta=f"{d/plan_ER*100:.1f}%")

st.subheader("Результаты: выбросы, сокращения и отклонения от ПДД")
st.dataframe(out, width="stretch", hide_index=True)

# --------------------------------------------------------------------------
#  Графики.
# --------------------------------------------------------------------------
g1, g2 = st.columns(2)
with g1:
    st.caption("Сокращение выбросов ER по периодам")
    st.bar_chart(out.set_index("Период")["ER (сокращение), т CO₂-экв."])
with g2:
    st.caption("Выбросы PE и BE по периодам")
    st.bar_chart(out.set_index("Период")[["PE (проект), т CO₂-экв.", "BE (базовый), т CO₂-экв."]])

# --------------------------------------------------------------------------
#  Экспорт в Excel.
# --------------------------------------------------------------------------
def to_excel(df_in, df_out):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df_in.to_excel(w, sheet_name="Входные данные", index=False)
        df_out.to_excel(w, sheet_name="Результаты", index=False)
    return buf.getvalue()

st.download_button("Скачать результаты в Excel", data=to_excel(edited, out),
                   file_name="Результаты_расчёта_ПГ.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.markdown("---")
st.caption("Проверка: при данных проектной документации суммарное сокращение выбросов за 2025–2034 гг. "
           "составляет ≈ 2 491 193 т CO₂-экв. (совпадает с таблицей 8.4.1 PDD).")
