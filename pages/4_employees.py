import streamlit as st
import pandas as pd
from utils.styles import render_insight, render_section_header
from utils.charts import bar_chart, line_chart, donut_chart
from utils.insights import generate_employee_insights

df = st.session_state.get("filtered_df", pd.DataFrame())

st.title("👤 Аналитика по сотрудникам")

if df.empty or "сотрудник" not in df.columns:
    st.warning("Нет данных для выбранных фильтров.")
    st.stop()

df_emp = df[df["сотрудник"] != "Неизвестно"].copy()

if df_emp.empty:
    st.warning("Нет данных с привязкой к сотрудникам.")
    st.stop()

# ── Employee stats ──
emp_stats = df_emp.groupby("сотрудник").agg(
    выручка=("продажа", "sum"),
    наценка=("наценка", "sum"),
    кол_во=("продажа", "count"),
).reset_index()
emp_stats["маржа_%"] = (emp_stats["наценка"] / emp_stats["выручка"].replace(0, float("nan")) * 100).fillna(0).round(1)
emp_stats["ср_чек"] = (emp_stats["выручка"] / emp_stats["кол_во"]).round(0)
emp_stats = emp_stats.sort_values("выручка", ascending=False)

# ── Insights ──
render_section_header("Инсайты по сотрудникам")
insights = generate_employee_insights(df)
for ins in insights:
    render_insight(ins["text"], ins["level"])

st.divider()

# ── Rating charts ──
render_section_header("Рейтинг сотрудников")

tab1, tab2, tab3 = st.tabs(["По выручке", "По количеству", "По марже"])

with tab1:
    top_rev = emp_stats.nlargest(15, "выручка")
    fig = bar_chart(top_rev, x="выручка", y="сотрудник", title="Топ-15 по выручке",
                    orientation="h", height=max(350, len(top_rev) * 30))
    fig.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    top_qty = emp_stats.nlargest(15, "кол_во")
    fig = bar_chart(top_qty, x="кол_во", y="сотрудник", title="Топ-15 по количеству",
                    orientation="h", height=max(350, len(top_qty) * 30))
    fig.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    top_margin = emp_stats[emp_stats["кол_во"] >= 5].nlargest(15, "маржа_%")
    fig = bar_chart(top_margin, x="маржа_%", y="сотрудник", title="Топ-15 по марже (мин. 5 продаж)",
                    orientation="h", height=max(350, len(top_margin) * 30))
    fig.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Employee profile ──
render_section_header("Профиль сотрудника")
selected_emp = st.selectbox("Выберите сотрудника", emp_stats["сотрудник"].tolist())

if selected_emp:
    emp_data = df_emp[df_emp["сотрудник"] == selected_emp]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Выручка", f"{emp_data['продажа'].sum():,.0f} ₸")
    c2.metric("Наценка", f"{emp_data['наценка'].sum():,.0f} ₸")
    c3.metric("Кол-во", f"{len(emp_data):,}")
    c4.metric("Ср. чек", f"{emp_data['продажа'].mean():,.0f} ₸")
    emp_margin = (emp_data["наценка"].sum() / emp_data["продажа"].sum() * 100) if emp_data["продажа"].sum() > 0 else 0
    c5.metric("Маржа", f"{emp_margin:.1f}%")

    col_a, col_b = st.columns(2)
    with col_a:
        trend = emp_data.groupby(emp_data["дата"].dt.to_period("M")).agg(
            выручка=("продажа", "sum"),
        ).reset_index()
        trend["дата"] = trend["дата"].dt.to_timestamp()
        fig_trend = line_chart(trend, "дата", "выручка", f"Выручка: {selected_emp}", height=350)
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_b:
        if "подкатегория" in emp_data.columns:
            cat_data = emp_data.groupby("подкатегория").agg(выручка=("продажа", "sum")).reset_index()
            fig_cat = donut_chart(cat_data, "выручка", "подкатегория", f"Категории: {selected_emp}", height=350)
            st.plotly_chart(fig_cat, use_container_width=True)

st.divider()

# ── Full table ──
render_section_header("Сводная таблица")
st.dataframe(
    emp_stats.rename(columns={
        "сотрудник": "Сотрудник",
        "выручка": "Выручка",
        "наценка": "Валовая прибыль",
        "кол_во": "Кол-во",
        "маржа_%": "Маржа %",
        "ср_чек": "Ср. чек",
    }).style.format({
        "Выручка": "{:,.0f}",
        "Валовая прибыль": "{:,.0f}",
        "Маржа %": "{:.1f}%",
        "Ср. чек": "{:,.0f}",
        "Кол-во": "{:,}",
    }),
    use_container_width=True,
    hide_index=True,
)
