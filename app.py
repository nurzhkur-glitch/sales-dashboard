import streamlit as st

st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.data_loader import prepare_data
from utils.styles import inject_custom_css
import pandas as pd

inject_custom_css()


@st.cache_data(ttl=3600)
def get_data():
    return prepare_data()


df = get_data()

# ── Sidebar ──
st.sidebar.title("📊 Sales Dashboard")
st.sidebar.caption(f"Данных: {len(df):,} продаж")
st.sidebar.divider()
st.sidebar.subheader("Фильтры")

min_date = df["дата"].min().date()
max_date = df["дата"].max().date()
date_range = st.sidebar.date_input(
    "Период",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = date_range
else:
    start, end = min_date, max_date

quick = st.sidebar.radio(
    "Быстрый период",
    ["Всё", "Этот год", "Этот квартал", "Этот месяц", "Эта неделя"],
    horizontal=True,
)
today = pd.Timestamp.today()
if quick == "Этот год":
    start = today.replace(month=1, day=1).date()
    end = max_date
elif quick == "Этот квартал":
    q_start_month = ((today.month - 1) // 3) * 3 + 1
    start = today.replace(month=q_start_month, day=1).date()
    end = max_date
elif quick == "Этот месяц":
    start = today.replace(day=1).date()
    end = max_date
elif quick == "Эта неделя":
    start = (today - pd.Timedelta(days=today.weekday())).date()
    end = max_date

branches = sorted(df["отделение"].dropna().unique().tolist()) if "отделение" in df.columns else []
selected_branches = st.sidebar.multiselect("Филиал", branches, default=branches)

categories = sorted(df["подкатегория"].dropna().unique().tolist()) if "подкатегория" in df.columns else []
selected_categories = st.sidebar.multiselect("Подкатегория", categories, default=categories)

sources = sorted(df["источник"].dropna().unique().tolist()) if "источник" in df.columns else []
selected_sources = st.sidebar.multiselect("Источник", sources, default=sources)

employees = sorted([e for e in df["сотрудник"].dropna().unique().tolist() if e != "Неизвестно"])
selected_employees = st.sidebar.multiselect("Сотрудник", employees, default=employees)

# ── Apply filters ──
mask = (
    (df["дата"].dt.date >= start)
    & (df["дата"].dt.date <= end)
)
if selected_branches:
    mask &= df["отделение"].isin(selected_branches)
if selected_categories:
    mask &= df["подкатегория"].isin(selected_categories)
if selected_sources:
    mask &= df["источник"].isin(selected_sources)
if selected_employees:
    mask &= (df["сотрудник"].isin(selected_employees)) | (df["сотрудник"] == "Неизвестно")

filtered_df = df[mask].copy()

st.session_state["filtered_df"] = filtered_df
st.session_state["full_df"] = df
st.session_state["date_range"] = (start, end)

# ── Navigation ──
overview_page = st.Page("pages/1_overview.py", title="Обзор", icon="📊", default=True)
branches_page = st.Page("pages/2_branches.py", title="Филиалы", icon="🏢")
categories_page = st.Page("pages/3_categories.py", title="Категории", icon="📦")
employees_page = st.Page("pages/4_employees.py", title="Сотрудники", icon="👤")
comparison_page = st.Page("pages/5_comparison.py", title="Сравнение и прогноз", icon="🔮")

pg = st.navigation([overview_page, branches_page, categories_page, employees_page, comparison_page])
pg.run()
