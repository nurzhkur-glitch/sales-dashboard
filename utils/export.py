import io
import pandas as pd
from fpdf import FPDF


class ReportPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "Sales Analytics Report", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def add_section(self, title: str):
        self.set_font("Helvetica", "B", 12)
        self.set_fill_color(108, 92, 231)
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, f"  {title}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(3)

    def add_kpi_row(self, kpis: list[tuple[str, str]]):
        self.set_font("Helvetica", "", 10)
        col_w = self.w / len(kpis) - 4 if kpis else 40
        for label, value in kpis:
            self.set_font("Helvetica", "", 8)
            self.cell(col_w, 5, label, align="C")
        self.ln()
        for label, value in kpis:
            self.set_font("Helvetica", "B", 11)
            self.cell(col_w, 6, value, align="C")
        self.ln(8)

    def add_table(self, df: pd.DataFrame, max_rows: int = 20):
        if df.empty:
            return
        df_show = df.head(max_rows)
        cols = list(df_show.columns)
        col_w = (self.w - 20) / len(cols)

        self.set_font("Helvetica", "B", 7)
        self.set_fill_color(230, 230, 230)
        for col in cols:
            self.cell(col_w, 6, str(col)[:18], border=1, fill=True, align="C")
        self.ln()

        self.set_font("Helvetica", "", 7)
        for _, row in df_show.iterrows():
            for col in cols:
                val = row[col]
                if isinstance(val, float):
                    text = f"{val:,.0f}" if abs(val) > 1 else f"{val:.2f}"
                else:
                    text = str(val)[:18]
                self.cell(col_w, 5, text, border=1, align="C")
            self.ln()
        self.ln(4)

    def add_insight(self, text: str):
        self.set_font("Helvetica", "", 9)
        clean = text.replace("<b>", "").replace("</b>", "")
        self.multi_cell(0, 5, f"  • {clean}")
        self.ln(1)


def generate_pdf_report(df: pd.DataFrame, insights: list[dict]) -> bytes:
    pdf = ReportPDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.add_section("Key Metrics")
    total_rev = df["продажа"].sum()
    total_profit = df["наценка"].sum()
    avg_check = total_rev / len(df) if len(df) > 0 else 0
    margin = (total_profit / total_rev * 100) if total_rev > 0 else 0
    pdf.add_kpi_row([
        ("Revenue", f"{total_rev:,.0f}"),
        ("Gross Profit", f"{total_profit:,.0f}"),
        ("Avg Check", f"{avg_check:,.0f}"),
        ("Margin", f"{margin:.1f}%"),
        ("Qty", f"{len(df):,}"),
    ])

    if "отделение" in df.columns:
        pdf.add_section("By Branch")
        branch_table = df.groupby("отделение").agg(
            Revenue=("продажа", "sum"),
            Profit=("наценка", "sum"),
            Qty=("продажа", "count"),
        ).reset_index().sort_values("Revenue", ascending=False)
        branch_table["Margin%"] = (branch_table["Profit"] / branch_table["Revenue"].replace(0, float("nan")) * 100).fillna(0).round(1)
        pdf.add_table(branch_table)

    if "подкатегория" in df.columns:
        pdf.add_section("By Category")
        cat_table = df.groupby("подкатегория").agg(
            Revenue=("продажа", "sum"),
            Profit=("наценка", "sum"),
            Qty=("продажа", "count"),
        ).reset_index().sort_values("Revenue", ascending=False)
        cat_table["Share%"] = (cat_table["Revenue"] / cat_table["Revenue"].sum() * 100).round(1)
        pdf.add_table(cat_table)

    if insights:
        pdf.add_section("Insights & Recommendations")
        for item in insights:
            pdf.add_insight(item["text"])

    buffer = io.BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()
