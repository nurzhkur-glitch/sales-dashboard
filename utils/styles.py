import streamlit as st


def inject_custom_css():
    st.markdown(
        """
        <style>
        /* KPI card styling */
        div[data-testid="stMetric"] {
            background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3e 100%);
            border: 1px solid rgba(108, 92, 231, 0.3);
            border-radius: 12px;
            padding: 16px 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        div[data-testid="stMetric"] label {
            color: #a0a0b8 !important;
            font-size: 0.85rem !important;
            font-weight: 500 !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            font-size: 1.8rem !important;
            font-weight: 700 !important;
            color: #ffffff !important;
        }
        div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
            font-size: 0.9rem !important;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background: #0E1117;
            border-right: 1px solid rgba(108, 92, 231, 0.2);
        }

        /* Insight cards */
        .insight-card {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-left: 4px solid #6C5CE7;
            border-radius: 8px;
            padding: 16px 20px;
            margin: 8px 0;
            color: #e0e0e0;
            font-size: 0.95rem;
            line-height: 1.5;
        }
        .insight-card.warning {
            border-left-color: #fdcb6e;
        }
        .insight-card.danger {
            border-left-color: #e17055;
        }
        .insight-card.success {
            border-left-color: #00b894;
        }

        /* Tables */
        .stDataFrame {
            border-radius: 8px;
            overflow: hidden;
        }

        /* Tabs */
        button[data-baseweb="tab"] {
            font-weight: 600 !important;
        }

        /* Section headers */
        .section-header {
            font-size: 1.3rem;
            font-weight: 700;
            color: #FAFAFA;
            margin: 24px 0 12px 0;
            padding-bottom: 8px;
            border-bottom: 2px solid #6C5CE7;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_insight(text: str, level: str = "info"):
    css_class = {
        "info": "insight-card",
        "warning": "insight-card warning",
        "danger": "insight-card danger",
        "success": "insight-card success",
    }.get(level, "insight-card")
    st.markdown(f'<div class="{css_class}">{text}</div>', unsafe_allow_html=True)


def render_section_header(text: str):
    st.markdown(f'<div class="section-header">{text}</div>', unsafe_allow_html=True)


def format_number(value: float, prefix: str = "", suffix: str = "") -> str:
    if abs(value) >= 1_000_000_000:
        return f"{prefix}{value / 1_000_000_000:,.1f} млрд{suffix}"
    if abs(value) >= 1_000_000:
        return f"{prefix}{value / 1_000_000:,.1f} млн{suffix}"
    if abs(value) >= 1_000:
        return f"{prefix}{value:,.0f}{suffix}"
    return f"{prefix}{value:,.2f}{suffix}"
