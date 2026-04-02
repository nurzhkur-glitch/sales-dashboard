import streamlit as st
import pandas as pd
import io

SPREADSHEET_IDS = {
    "employee": "1P1pXtdiVRyhSMKcN0YFz9vky4Y2Hk-5eS062Eyuovwc",
    "sales": "164NMj0zKihkwGgViQ56mG4HkDvofnU2ZIzAOTMoCQgU",
    "source": "1QWh3JwvNU9k-bMDG1fKe9Q7njCegO6tcZsngQO76a8Y",
}


def _has_gcp_secrets() -> bool:
    try:
        return "gcp_service_account" in st.secrets
    except Exception:
        return False


def _public_csv_url(spreadsheet_id: str, gid: int = 0) -> str:
    return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={gid}"


def _load_public_sheet(spreadsheet_id: str) -> pd.DataFrame:
    url = _public_csv_url(spreadsheet_id)
    return pd.read_csv(url, dtype=str, keep_default_na=False)


@st.cache_data(ttl=3600, show_spinner="Загрузка данных из Google Sheets...")
def load_raw_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df_sales = _load_public_sheet(SPREADSHEET_IDS["sales"])
    df_employee = _load_public_sheet(SPREADSHEET_IDS["employee"])
    df_source = _load_public_sheet(SPREADSHEET_IDS["source"])
    return df_sales, df_employee, df_source


def _clean_numeric(series: pd.Series) -> pd.Series:
    cleaned = series.astype(str)
    cleaned = cleaned.str.replace("\u00a0", "", regex=False)
    cleaned = cleaned.str.replace(" ", "", regex=False)
    cleaned = cleaned.str.replace(r"[^\d\-.,]", "", regex=True)
    cleaned = cleaned.str.replace(",", ".", regex=False)
    return pd.to_numeric(cleaned, errors="coerce").fillna(0)


def _normalize_id(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.lower()


def prepare_data() -> pd.DataFrame:
    df_sales, df_employee, df_source = load_raw_data()

    sales_id_col = "id" if "id" in df_sales.columns else "ID"
    emp_id_col = "ID" if "ID" in df_employee.columns else "id"
    src_id_col = "ID" if "ID" in df_source.columns else "id"

    df_sales["_join_id"] = _normalize_id(df_sales[sales_id_col])
    df_employee["_join_id"] = _normalize_id(df_employee[emp_id_col])
    df_source["_join_id"] = _normalize_id(df_source[src_id_col])

    emp_dedup = df_employee.drop_duplicates(subset="_join_id", keep="first")
    src_dedup = df_source.drop_duplicates(subset="_join_id", keep="first")

    emp_cols = {"_join_id": "_join_id", "Сотрудник": "сотрудник"}
    emp_renamed = emp_dedup[list(emp_cols.keys())].rename(columns=emp_cols)

    src_rename_map = {"_join_id": "_join_id"}
    sourse_col = "sourse" if "sourse" in df_source.columns else "source"
    src_rename_map[sourse_col] = "источник"
    src_renamed = src_dedup[list(src_rename_map.keys())].rename(columns=src_rename_map)

    df = df_sales.merge(emp_renamed, on="_join_id", how="left")
    df = df.merge(src_renamed, on="_join_id", how="left")

    date_col = "дата продажи" if "дата продажи" in df.columns else "Дата продажи"
    df["дата"] = pd.to_datetime(df[date_col], format="%d.%m.%Y", errors="coerce")
    df = df.dropna(subset=["дата"])

    for col in ["наценка", "себестоимость", "витрина", "продажа"]:
        if col in df.columns:
            df[col] = _clean_numeric(df[col])

    df["маржа_%"] = (df["наценка"] / df["продажа"].replace(0, float("nan")) * 100).fillna(0).round(2)

    df["год"] = df["дата"].dt.year
    df["месяц"] = df["дата"].dt.month
    df["месяц_название"] = df["дата"].dt.strftime("%B")
    df["неделя"] = df["дата"].dt.isocalendar().week.astype(int)
    df["день_недели"] = df["дата"].dt.day_name()

    if "подкатегория" not in df.columns:
        for candidate in ["Подкатегория", "категория", "Категория"]:
            if candidate in df.columns:
                df["подкатегория"] = df[candidate]
                break

    if "отделение" not in df.columns:
        for candidate in ["Отделение", "филиал", "Филиал"]:
            if candidate in df.columns:
                df["отделение"] = df[candidate]
                break

    df["сотрудник"] = df.get("сотрудник", pd.Series(["Неизвестно"] * len(df)))
    df["сотрудник"] = df["сотрудник"].fillna("Неизвестно")
    df["источник"] = df.get("источник", pd.Series(["Неизвестно"] * len(df)))
    df["источник"] = df["источник"].fillna("Неизвестно")

    df = df.drop(columns=["_join_id"], errors="ignore")
    return df.sort_values("дата").reset_index(drop=True)
