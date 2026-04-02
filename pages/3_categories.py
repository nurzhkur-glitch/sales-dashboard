import streamlit as st
import pandas as pd
from utils.styles import render_insight, render_section_header
from utils.charts import donut_chart, bar_chart, line_chart
from utils.insights import generate_category_insights

df = st.session_state.get("filtered_df", pd.DataFrame())

st.title("📦 Аналитика по категориям")

if df.empty or "подкатегория" not in df.columns:
    st.warning("Нет данных для выбранных фильтров.")
    st.stop()

# ── Category stats ──
cat_stats = df.groupby("подкатегория").agg(
    выручка=("продажа", "sum"),
    наценка=("наценка", "sum"),
    кол_во=("продажа", "count"),
).reset_index()
cat_stats["доля_%"] = (cat_stats["выручка"] / cat_stats["выручка"].sum() * 100).round(2)
cat_stats["маржа_%"] = (cat_stats["наценка"] / cat_stats["выручка"].replace(0, float("nan")) * 100).fillna(0).round(1)
cat_stats["ср_чек"] = (cat_stats["выручка"] / cat_stats["кол_во"]).round(0)
cat_stats = cat_stats.sort_values("выручка", ascending=False)

# ── Insights ──
render_section_header("Инсайты по категориям")
insights = generate_category_insights(df)
for ins in insights:
    render_insight(ins["text"], ins["level"])

st.divider()

# ── Donut + Bar ──
col1, col2 = st.columns(2)
with col1:
    fig_donut = donut_chart(cat_stats, "выручка", "подкатегория", "Доля категорий", height=420)
    st.plotly_chart(fig_donut, use_container_width=True)
with col2:
    fig_bar = bar_chart(cat_stats, x="подкатегория", y="выручка", title="Выручка по категориям", height=420)
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# ── Margin by category ──
render_section_header("Маржинальность по категориям")
col_a, col_b = st.columns(2)
with col_a:
    fig_margin = bar_chart(cat_stats, x="подкатегория", y="маржа_%", title="Маржа (%) по категориям", height=380)
    st.plotly_chart(fig_margin, use_container_width=True)
with col_b:
    fig_qty = bar_chart(cat_stats, x="подкатегория", y="кол_во", title="Количество продаж", height=380)
    st.plotly_chart(fig_qty, use_container_width=True)

st.divider()

# ── Trend by category ──
render_section_header("Динамика по категориям")
trend = df.groupby([df["дата"].dt.to_period("M"), "подкатегория"]).agg(
    выручка=("продажа", "sum"),
).reset_index()
trend["дата"] = trend["дата"].dt.to_timestamp()
fig_trend = line_chart(trend, "дата", "выручка", "Выручка по категориям", color="подкатегория", height=420)
st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

# ── Top products per category ──
render_section_header("Топ товары по категориям")
selected_cat = st.selectbox("Выберите категорию", cat_stats["подкатегория"].tolist())
if selected_cat:
    name_col = "наименование" if "наименование" in df.columns else "Наименование"
    if name_col in df.columns:
        top_items = (
            df[df["подкатегория"] == selected_cat]
            .nlargest(15, "продажа")
            [[name_col, "продажа", "наценка", "себестоимость"]]
            .rename(columns={name_col: "Товар", "продажа": "Цена продажи", "наценка": "Наценка", "себестоимость": "Себестоимость"})
        )
        st.dataframe(
            top_items.style.format({
                "Цена продажи": "{:,.0f}",
                "Наценка": "{:,.0f}",
                "Себестоимость": "{:,.0f}",
            }),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Колонка 'наименование' не найдена в данных.")

st.divider()

# ── Summary table ──
render_section_header("Сводная таблица")
st.dataframe(
    cat_stats.rename(columns={
        "подкатегория": "Категория",
        "выручка": "Выручка",
        "наценка": "Валовая прибыль",
        "кол_во": "Кол-во",
        "доля_%": "Доля %",
        "маржа_%": "Маржа %",
        "ср_чек": "Ср. чек",
    }).style.format({
        "Выручка": "{:,.0f}",
        "Валовая прибыль": "{:,.0f}",
        "Доля %": "{:.1f}%",
        "Маржа %": "{:.1f}%",
        "Ср. чек": "{:,.0f}",
        "Кол-во": "{:,}",
    }),
    use_container_width=True,
    hide_index=True,
)
