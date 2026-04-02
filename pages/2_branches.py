import streamlit as st
import pandas as pd
from utils.styles import render_insight, render_section_header
from utils.charts import bar_chart, heatmap_chart, line_chart
from utils.insights import generate_branch_insights

df = st.session_state.get("filtered_df", pd.DataFrame())

st.title("🏢 Аналитика по филиалам")

if df.empty or "отделение" not in df.columns:
    st.warning("Нет данных для выбранных фильтров.")
    st.stop()

# ── Branch KPIs ──
branch_stats = df.groupby("отделение").agg(
    выручка=("продажа", "sum"),
    себестоимость=("себестоимость", "sum"),
    наценка=("наценка", "sum"),
    кол_во=("продажа", "count"),
).reset_index()
branch_stats["маржа_%"] = (branch_stats["наценка"] / branch_stats["выручка"].replace(0, float("nan")) * 100).fillna(0).round(1)
branch_stats["ср_чек"] = (branch_stats["выручка"] / branch_stats["кол_во"]).round(0)
branch_stats = branch_stats.sort_values("выручка", ascending=False)

# ── Insights ──
render_section_header("Инсайты по филиалам")
insights = generate_branch_insights(df)
for ins in insights:
    render_insight(ins["text"], ins["level"])

st.divider()

# ── Revenue bar chart ──
render_section_header("Выручка по филиалам")
fig_rev = bar_chart(
    branch_stats, x="отделение", y="выручка",
    title="Выручка по отделениям", height=420,
)
st.plotly_chart(fig_rev, use_container_width=True)

# ── Margin bar chart ──
col1, col2 = st.columns(2)
with col1:
    fig_margin = bar_chart(
        branch_stats, x="отделение", y="маржа_%",
        title="Маржа (%) по отделениям", height=380,
    )
    st.plotly_chart(fig_margin, use_container_width=True)
with col2:
    fig_qty = bar_chart(
        branch_stats, x="отделение", y="кол_во",
        title="Кол-во продаж по отделениям", height=380,
    )
    st.plotly_chart(fig_qty, use_container_width=True)

st.divider()

# ── Heatmap: branch × month ──
render_section_header("Тепловая карта: Филиал × Месяц")
MONTH_NAMES = {
    1: "Янв", 2: "Фев", 3: "Мар", 4: "Апр", 5: "Май", 6: "Июн",
    7: "Июл", 8: "Авг", 9: "Сен", 10: "Окт", 11: "Ноя", 12: "Дек",
}
df_hm = df.copy()
df_hm["месяц_кр"] = df_hm["месяц"].map(MONTH_NAMES)
pivot = df_hm.pivot_table(
    values="продажа", index="отделение", columns="месяц",
    aggfunc="sum", fill_value=0,
)
pivot.columns = [MONTH_NAMES.get(c, c) for c in pivot.columns]
fig_hm = heatmap_chart(pivot, "Выручка: Филиал × Месяц", height=max(350, len(pivot) * 35))
st.plotly_chart(fig_hm, use_container_width=True)

st.divider()

# ── Trend per branch ──
render_section_header("Динамика по филиалам")
selected = st.multiselect(
    "Выберите филиалы для сравнения",
    branch_stats["отделение"].tolist(),
    default=branch_stats["отделение"].head(3).tolist(),
)
if selected:
    trend_df = df[df["отделение"].isin(selected)].copy()
    trend_agg = trend_df.groupby([trend_df["дата"].dt.to_period("M"), "отделение"]).agg(
        выручка=("продажа", "sum"),
    ).reset_index()
    trend_agg["дата"] = trend_agg["дата"].dt.to_timestamp()
    fig_trend = line_chart(trend_agg, "дата", "выручка", "Выручка по филиалам", color="отделение", height=400)
    st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

# ── Detail table ──
render_section_header("Детальная таблица")
st.dataframe(
    branch_stats.rename(columns={
        "отделение": "Филиал",
        "выручка": "Выручка",
        "себестоимость": "Себестоимость",
        "наценка": "Валовая прибыль",
        "кол_во": "Кол-во",
        "маржа_%": "Маржа %",
        "ср_чек": "Ср. чек",
    }).style.format({
        "Выручка": "{:,.0f}",
        "Себестоимость": "{:,.0f}",
        "Валовая прибыль": "{:,.0f}",
        "Маржа %": "{:.1f}%",
        "Ср. чек": "{:,.0f}",
        "Кол-во": "{:,}",
    }),
    use_container_width=True,
    hide_index=True,
)
