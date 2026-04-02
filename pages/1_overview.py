import streamlit as st
import pandas as pd
from utils.styles import render_insight, render_section_header, format_number
from utils.charts import line_chart, bar_chart
from utils.insights import generate_overview_insights
from utils.export import generate_pdf_report

df = st.session_state.get("filtered_df", pd.DataFrame())
full_df = st.session_state.get("full_df", pd.DataFrame())

st.title("📊 Обзор продаж")

if df.empty:
    st.warning("Нет данных для выбранных фильтров.")
    st.stop()

# ── KPI cards ──
total_revenue = df["продажа"].sum()
total_cogs = df["себестоимость"].sum()
total_profit = df["наценка"].sum()
avg_check = total_revenue / len(df) if len(df) > 0 else 0
total_qty = len(df)
margin_pct = (total_profit / total_revenue * 100) if total_revenue > 0 else 0

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Выручка", format_number(total_revenue, suffix=" ₸"))
col2.metric("Себестоимость", format_number(total_cogs, suffix=" ₸"))
col3.metric("Валовая прибыль", format_number(total_profit, suffix=" ₸"))
col4.metric("Средний чек", format_number(avg_check, suffix=" ₸"))
col5.metric("Кол-во продаж", f"{total_qty:,}")
col6.metric("Маржа", f"{margin_pct:.1f}%")

st.divider()

# ── Auto-insights ──
render_section_header("Ключевые наблюдения")
insights = generate_overview_insights(full_df)
if insights:
    for ins in insights:
        render_insight(ins["text"], ins["level"])
else:
    st.info("Недостаточно данных для генерации инсайтов.")

st.divider()

# ── Revenue trend ──
render_section_header("Динамика выручки")
time_group = st.radio("Группировка", ["По месяцам", "По неделям", "По дням"], horizontal=True)

if time_group == "По месяцам":
    trend = df.groupby(df["дата"].dt.to_period("M")).agg(
        выручка=("продажа", "sum"),
        наценка=("наценка", "sum"),
        кол_во=("продажа", "count"),
    ).reset_index()
    trend["дата"] = trend["дата"].dt.to_timestamp()
elif time_group == "По неделям":
    trend = df.groupby(df["дата"].dt.to_period("W")).agg(
        выручка=("продажа", "sum"),
        наценка=("наценка", "sum"),
        кол_во=("продажа", "count"),
    ).reset_index()
    trend["дата"] = trend["дата"].dt.to_timestamp()
else:
    trend = df.groupby(df["дата"].dt.date).agg(
        выручка=("продажа", "sum"),
        наценка=("наценка", "sum"),
        кол_во=("продажа", "count"),
    ).reset_index()
    trend.rename(columns={trend.columns[0]: "дата"}, inplace=True)

fig_rev = line_chart(trend, "дата", "выручка", "Выручка", height=380)
st.plotly_chart(fig_rev, use_container_width=True)

col_a, col_b = st.columns(2)
with col_a:
    fig_profit = line_chart(trend, "дата", "наценка", "Валовая прибыль", height=320)
    st.plotly_chart(fig_profit, use_container_width=True)
with col_b:
    fig_qty = bar_chart(trend, "дата", "кол_во", "Количество продаж", height=320)
    st.plotly_chart(fig_qty, use_container_width=True)

st.divider()

# ── Summary table (like Power BI) ──
render_section_header("Сводная таблица по годам")
yearly = df.groupby("год").agg(
    Revenue=("продажа", "sum"),
    COGS=("себестоимость", "sum"),
    Gross_Profit=("наценка", "sum"),
    Quantity=("продажа", "count"),
).reset_index()
yearly["Gross_Profit_%"] = (yearly["Gross_Profit"] / yearly["Revenue"].replace(0, float("nan")) * 100).fillna(0).round(1)
yearly["Margin_%"] = (yearly["Gross_Profit"] / yearly["COGS"].replace(0, float("nan")) * 100).fillna(0).round(1)
yearly.columns = ["Год", "Выручка", "Себестоимость", "Валовая прибыль", "Кол-во", "GP %", "Маржа %"]

st.dataframe(
    yearly.style.format({
        "Выручка": "{:,.0f}",
        "Себестоимость": "{:,.0f}",
        "Валовая прибыль": "{:,.0f}",
        "GP %": "{:.1f}%",
        "Маржа %": "{:.1f}%",
        "Кол-во": "{:,}",
    }),
    use_container_width=True,
    hide_index=True,
)

with st.expander("Детализация по месяцам"):
    monthly = df.groupby(["год", "месяц"]).agg(
        Revenue=("продажа", "sum"),
        COGS=("себестоимость", "sum"),
        Gross_Profit=("наценка", "sum"),
        Quantity=("продажа", "count"),
    ).reset_index()
    monthly["GP_%"] = (monthly["Gross_Profit"] / monthly["Revenue"].replace(0, float("nan")) * 100).fillna(0).round(1)
    monthly.columns = ["Год", "Месяц", "Выручка", "Себестоимость", "Валовая прибыль", "Кол-во", "GP %"]
    st.dataframe(
        monthly.style.format({
            "Выручка": "{:,.0f}",
            "Себестоимость": "{:,.0f}",
            "Валовая прибыль": "{:,.0f}",
            "GP %": "{:.1f}%",
            "Кол-во": "{:,}",
        }),
        use_container_width=True,
        hide_index=True,
    )

# ── PDF export ──
st.divider()
if st.button("📄 Скачать отчёт в PDF"):
    pdf_bytes = generate_pdf_report(df, insights)
    st.download_button(
        label="⬇️ Скачать PDF",
        data=pdf_bytes,
        file_name="sales_report.pdf",
        mime="application/pdf",
    )
