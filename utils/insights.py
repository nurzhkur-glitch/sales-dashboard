import pandas as pd


def _pct_change(current: float, previous: float) -> float:
    if previous == 0:
        return 0.0
    return round((current - previous) / abs(previous) * 100, 1)


def _direction(pct: float) -> str:
    if pct > 0:
        return "выросла"
    if pct < 0:
        return "упала"
    return "не изменилась"


def _arrow(pct: float) -> str:
    if pct > 0:
        return "📈"
    if pct < 0:
        return "📉"
    return "➡️"


def generate_overview_insights(df: pd.DataFrame) -> list[dict]:
    insights = []
    if df.empty:
        return insights

    dates = df["дата"].sort_values()
    max_date = dates.max()
    current_month = max_date.month
    current_year = max_date.year

    df_current = df[(df["дата"].dt.month == current_month) & (df["дата"].dt.year == current_year)]

    if current_month == 1:
        prev_month, prev_year = 12, current_year - 1
    else:
        prev_month, prev_year = current_month - 1, current_year

    df_prev = df[(df["дата"].dt.month == prev_month) & (df["дата"].dt.year == prev_year)]

    if not df_current.empty and not df_prev.empty:
        rev_curr = df_current["продажа"].sum()
        rev_prev = df_prev["продажа"].sum()
        pct = _pct_change(rev_curr, rev_prev)
        insights.append({
            "text": f"{_arrow(pct)} Выручка за текущий месяц {_direction(pct)} на <b>{abs(pct)}%</b> по сравнению с прошлым ({rev_curr:,.0f} vs {rev_prev:,.0f})",
            "level": "success" if pct > 0 else "danger" if pct < -5 else "warning",
        })

        margin_curr = (df_current["наценка"].sum() / df_current["продажа"].sum() * 100) if df_current["продажа"].sum() > 0 else 0
        margin_prev = (df_prev["наценка"].sum() / df_prev["продажа"].sum() * 100) if df_prev["продажа"].sum() > 0 else 0
        margin_diff = round(margin_curr - margin_prev, 1)
        insights.append({
            "text": f"Маржинальность: <b>{margin_curr:.1f}%</b> (было {margin_prev:.1f}%, изменение {'+' if margin_diff > 0 else ''}{margin_diff} п.п.)",
            "level": "success" if margin_diff > 0 else "danger" if margin_diff < -2 else "info",
        })

        qty_curr = len(df_current)
        qty_prev = len(df_prev)
        qty_pct = _pct_change(qty_curr, qty_prev)
        insights.append({
            "text": f"Количество продаж: <b>{qty_curr}</b> (было {qty_prev}, {_direction(qty_pct)} на {abs(qty_pct)}%)",
            "level": "success" if qty_pct > 0 else "warning",
        })

    avg_margin = df["маржа_%"].mean()
    if avg_margin < 20:
        insights.append({
            "text": f"⚠️ Средняя маржа <b>{avg_margin:.1f}%</b> — ниже 20%. Рекомендуется проверить ценообразование.",
            "level": "danger",
        })

    return insights


def generate_branch_insights(df: pd.DataFrame) -> list[dict]:
    insights = []
    if df.empty or "отделение" not in df.columns:
        return insights

    branch_stats = df.groupby("отделение").agg(
        выручка=("продажа", "sum"),
        наценка=("наценка", "sum"),
        кол_во=("продажа", "count"),
    ).reset_index()
    branch_stats["маржа"] = (branch_stats["наценка"] / branch_stats["выручка"].replace(0, float("nan")) * 100).fillna(0)

    best_rev = branch_stats.loc[branch_stats["выручка"].idxmax()]
    insights.append({
        "text": f"🏆 Лидер по выручке: <b>{best_rev['отделение']}</b> — {best_rev['выручка']:,.0f} тг ({best_rev['кол_во']:.0f} продаж)",
        "level": "success",
    })

    best_margin = branch_stats.loc[branch_stats["маржа"].idxmax()]
    insights.append({
        "text": f"💎 Лучшая маржа: <b>{best_margin['отделение']}</b> — {best_margin['маржа']:.1f}%",
        "level": "info",
    })

    low_margin = branch_stats[branch_stats["маржа"] < 15]
    if not low_margin.empty:
        names = ", ".join(low_margin["отделение"].tolist())
        insights.append({
            "text": f"⚠️ Маржа ниже 15%: <b>{names}</b>. Рекомендуется анализ.",
            "level": "danger",
        })

    return insights


def generate_category_insights(df: pd.DataFrame) -> list[dict]:
    insights = []
    if df.empty or "подкатегория" not in df.columns:
        return insights

    cat_stats = df.groupby("подкатегория").agg(
        выручка=("продажа", "sum"),
    ).reset_index()
    cat_stats["доля"] = (cat_stats["выручка"] / cat_stats["выручка"].sum() * 100).round(1)
    cat_stats = cat_stats.sort_values("доля", ascending=False)

    top = cat_stats.iloc[0]
    insights.append({
        "text": f"Главная категория: <b>{top['подкатегория']}</b> — {top['доля']}% выручки",
        "level": "info",
    })

    small = cat_stats[cat_stats["доля"] < 2]
    if not small.empty:
        names = ", ".join(small["подкатегория"].tolist())
        insights.append({
            "text": f"Малые категории (менее 2%): <b>{names}</b>. Есть потенциал роста или кандидаты на вывод.",
            "level": "warning",
        })

    return insights


def generate_employee_insights(df: pd.DataFrame) -> list[dict]:
    insights = []
    if df.empty or "сотрудник" not in df.columns:
        return insights

    emp_stats = df[df["сотрудник"] != "Неизвестно"].groupby("сотрудник").agg(
        выручка=("продажа", "sum"),
        наценка=("наценка", "sum"),
        кол_во=("продажа", "count"),
    ).reset_index()

    if emp_stats.empty:
        return insights

    emp_stats["ср_чек"] = emp_stats["выручка"] / emp_stats["кол_во"]
    emp_stats["маржа"] = (emp_stats["наценка"] / emp_stats["выручка"].replace(0, float("nan")) * 100).fillna(0)

    top_rev = emp_stats.loc[emp_stats["выручка"].idxmax()]
    insights.append({
        "text": f"🏆 Лидер по выручке: <b>{top_rev['сотрудник']}</b> — {top_rev['выручка']:,.0f} тг ({top_rev['кол_во']:.0f} продаж)",
        "level": "success",
    })

    top_qty = emp_stats.loc[emp_stats["кол_во"].idxmax()]
    if top_qty["сотрудник"] != top_rev["сотрудник"]:
        insights.append({
            "text": f"📊 Лидер по количеству: <b>{top_qty['сотрудник']}</b> — {top_qty['кол_во']:.0f} продаж (маржа {top_qty['маржа']:.1f}%)",
            "level": "info",
        })

    top_margin = emp_stats.loc[emp_stats["маржа"].idxmax()]
    insights.append({
        "text": f"💎 Лучшая маржа: <b>{top_margin['сотрудник']}</b> — {top_margin['маржа']:.1f}% (средний чек {top_margin['ср_чек']:,.0f} тг)",
        "level": "info",
    })

    return insights


def generate_alerts(df: pd.DataFrame, margin_threshold: float = 20.0,
                    revenue_drop_threshold: float = -15.0) -> list[dict]:
    alerts = []
    if df.empty:
        return alerts

    dates = df["дата"].sort_values()
    max_date = dates.max()
    current_month = max_date.month
    current_year = max_date.year

    if current_month == 1:
        prev_month, prev_year = 12, current_year - 1
    else:
        prev_month, prev_year = current_month - 1, current_year

    df_curr = df[(df["дата"].dt.month == current_month) & (df["дата"].dt.year == current_year)]
    df_prev = df[(df["дата"].dt.month == prev_month) & (df["дата"].dt.year == prev_year)]

    if not df_curr.empty and not df_prev.empty and "отделение" in df.columns:
        for branch in df_curr["отделение"].unique():
            rev_c = df_curr[df_curr["отделение"] == branch]["продажа"].sum()
            rev_p = df_prev[df_prev["отделение"] == branch]["продажа"].sum()
            if rev_p > 0:
                pct = _pct_change(rev_c, rev_p)
                if pct <= revenue_drop_threshold:
                    alerts.append({
                        "text": f"🚨 <b>{branch}</b>: выручка упала на {abs(pct)}% (с {rev_p:,.0f} до {rev_c:,.0f})",
                        "level": "danger",
                    })
                elif pct >= 30:
                    alerts.append({
                        "text": f"🚀 <b>{branch}</b>: выручка выросла на {pct}% (с {rev_p:,.0f} до {rev_c:,.0f})",
                        "level": "success",
                    })

    overall_margin = (df_curr["наценка"].sum() / df_curr["продажа"].sum() * 100) if not df_curr.empty and df_curr["продажа"].sum() > 0 else 0
    if overall_margin < margin_threshold and not df_curr.empty:
        alerts.append({
            "text": f"⚠️ Общая маржа текущего месяца <b>{overall_margin:.1f}%</b> — ниже порога {margin_threshold}%",
            "level": "warning",
        })

    return alerts
