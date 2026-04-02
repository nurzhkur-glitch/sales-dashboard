import streamlit as st
import pandas as pd
import numpy as np
from utils.styles import render_insight, render_section_header
from utils.charts import comparison_chart, forecast_chart, bar_chart, line_chart
from utils.insights import generate_alerts

df = st.session_state.get("filtered_df", pd.DataFrame())
full_df = st.session_state.get("full_df", pd.DataFrame())

st.title("🔮 Сравнение периодов и прогноз")

if df.empty:
    st.warning("Нет данных для выбранных фильтров.")
    st.stop()

# ── Alerts ──
render_section_header("Алерты и уведомления")
alerts = generate_alerts(full_df)
if alerts:
    for alert in alerts:
        render_insight(alert["text"], alert["level"])
else:
    st.success("Аномалий не обнаружено. Все метрики в норме.")

st.divider()

# ── Period comparison ──
render_section_header("Сравнение периодов")
comp_type = st.radio("Тип сравнения", ["Месяц к месяцу (MoM)", "Год к году (YoY)"], horizontal=True)

if comp_type == "Месяц к месяцу (MoM)":
    months_available = sorted(df["дата"].dt.to_period("M").unique(), reverse=True)
    month_labels = [str(m) for m in months_available]

    if len(month_labels) >= 2:
        col1, col2 = st.columns(2)
        with col1:
            period1 = st.selectbox("Период 1", month_labels, index=1)
        with col2:
            period2 = st.selectbox("Период 2", month_labels, index=0)

        p1 = pd.Period(period1, freq="M")
        p2 = pd.Period(period2, freq="M")
        df_p1 = df[df["дата"].dt.to_period("M") == p1]
        df_p2 = df[df["дата"].dt.to_period("M") == p2]

        c1, c2, c3 = st.columns(3)
        rev1, rev2 = df_p1["продажа"].sum(), df_p2["продажа"].sum()
        c1.metric(f"Выручка {period1}", f"{rev1:,.0f}", delta=f"{rev2 - rev1:,.0f} ({period2})")
        prof1, prof2 = df_p1["наценка"].sum(), df_p2["наценка"].sum()
        c2.metric(f"Прибыль {period1}", f"{prof1:,.0f}", delta=f"{prof2 - prof1:,.0f} ({period2})")
        qty1, qty2 = len(df_p1), len(df_p2)
        c3.metric(f"Кол-во {period1}", f"{qty1:,}", delta=f"{qty2 - qty1:,} ({period2})")

        if "отделение" in df.columns:
            branch_p1 = df_p1.groupby("отделение").agg(выручка=("продажа", "sum")).reset_index()
            branch_p2 = df_p2.groupby("отделение").agg(выручка=("продажа", "sum")).reset_index()
            fig_comp = comparison_chart(
                branch_p1, branch_p2, "отделение", "выручка",
                str(period1), str(period2), "Сравнение по филиалам",
            )
            st.plotly_chart(fig_comp, use_container_width=True)

        if "подкатегория" in df.columns:
            cat_p1 = df_p1.groupby("подкатегория").agg(выручка=("продажа", "sum")).reset_index()
            cat_p2 = df_p2.groupby("подкатегория").agg(выручка=("продажа", "sum")).reset_index()
            fig_cat = comparison_chart(
                cat_p1, cat_p2, "подкатегория", "выручка",
                str(period1), str(period2), "Сравнение по категориям",
            )
            st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.info("Нужно минимум 2 месяца для сравнения.")

else:  # YoY
    years = sorted(df["год"].unique(), reverse=True)
    if len(years) >= 2:
        col1, col2 = st.columns(2)
        with col1:
            year1 = st.selectbox("Год 1", years, index=1)
        with col2:
            year2 = st.selectbox("Год 2", years, index=0)

        df_y1 = df[df["год"] == year1]
        df_y2 = df[df["год"] == year2]

        monthly_y1 = df_y1.groupby("месяц").agg(выручка=("продажа", "sum")).reset_index()
        monthly_y2 = df_y2.groupby("месяц").agg(выручка=("продажа", "sum")).reset_index()

        MONTH_NAMES = {
            1: "Янв", 2: "Фев", 3: "Мар", 4: "Апр", 5: "Май", 6: "Июн",
            7: "Июл", 8: "Авг", 9: "Сен", 10: "Окт", 11: "Ноя", 12: "Дек",
        }
        monthly_y1["месяц_кр"] = monthly_y1["месяц"].map(MONTH_NAMES)
        monthly_y2["месяц_кр"] = monthly_y2["месяц"].map(MONTH_NAMES)

        fig_yoy = comparison_chart(
            monthly_y1, monthly_y2, "месяц_кр", "выручка",
            str(year1), str(year2), f"Выручка: {year1} vs {year2}",
        )
        st.plotly_chart(fig_yoy, use_container_width=True)

        yoy_merged = monthly_y1[["месяц", "выручка"]].merge(
            monthly_y2[["месяц", "выручка"]], on="месяц", suffixes=(f"_{year1}", f"_{year2}"),
            how="outer",
        ).fillna(0)
        yoy_merged["месяц_кр"] = yoy_merged["месяц"].map(MONTH_NAMES)
        col_y1 = f"выручка_{year1}"
        col_y2 = f"выручка_{year2}"
        yoy_merged["изменение_%"] = ((yoy_merged[col_y2] - yoy_merged[col_y1]) / yoy_merged[col_y1].replace(0, float("nan")) * 100).fillna(0).round(1)
        st.dataframe(
            yoy_merged[["месяц_кр", col_y1, col_y2, "изменение_%"]].rename(columns={
                "месяц_кр": "Месяц",
                col_y1: f"Выручка {year1}",
                col_y2: f"Выручка {year2}",
                "изменение_%": "Изменение %",
            }).style.format({
                f"Выручка {year1}": "{:,.0f}",
                f"Выручка {year2}": "{:,.0f}",
                "Изменение %": "{:+.1f}%",
            }),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Нужно минимум 2 года для сравнения.")

st.divider()

# ── Forecast ──
render_section_header("Прогноз на следующий период")

monthly_all = full_df.groupby(full_df["дата"].dt.to_period("M")).agg(
    выручка=("продажа", "sum"),
    наценка=("наценка", "sum"),
    кол_во=("продажа", "count"),
).reset_index()
monthly_all["дата"] = monthly_all["дата"].dt.to_timestamp()
monthly_all = monthly_all.sort_values("дата")

if len(monthly_all) >= 3:
    monthly_all["idx"] = range(len(monthly_all))

    from sklearn.linear_model import LinearRegression

    forecast_months = st.slider("Месяцев прогноза", 1, 6, 3)

    for metric, label in [("выручка", "Выручка"), ("наценка", "Валовая прибыль"), ("кол_во", "Кол-во продаж")]:
        X = monthly_all["idx"].values.reshape(-1, 1)
        y = monthly_all[metric].values

        model = LinearRegression()
        model.fit(X, y)

        future_idx = np.arange(len(monthly_all), len(monthly_all) + forecast_months).reshape(-1, 1)
        future_vals = model.predict(future_idx)
        future_vals = np.maximum(future_vals, 0)

        last_date = monthly_all["дата"].max()
        future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=forecast_months, freq="MS")

        df_forecast = pd.DataFrame({"дата": future_dates, metric: future_vals})

        fig = forecast_chart(
            monthly_all, df_forecast, "дата", metric,
            f"{label}: факт + прогноз", height=380,
        )
        st.plotly_chart(fig, use_container_width=True)

    r2 = model.score(X, y)
    st.caption(f"Модель: линейная регрессия (R² = {r2:.3f}). Прогноз является ориентировочным.")
else:
    st.info("Нужно минимум 3 месяца данных для прогноза.")
