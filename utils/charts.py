import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

COLORS = [
    "#6C5CE7", "#00b894", "#fdcb6e", "#e17055", "#74b9ff",
    "#a29bfe", "#55efc4", "#ffeaa7", "#fab1a0", "#81ecec",
    "#dfe6e9", "#ff7675",
]

LAYOUT_DEFAULTS = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#FAFAFA", size=13),
    margin=dict(l=40, r=20, t=50, b=40),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(108,92,231,0.3)",
        borderwidth=1,
    ),
    hoverlabel=dict(bgcolor="#1a1a2e", font_size=13),
)


def _apply_defaults(fig: go.Figure, height: int = 400) -> go.Figure:
    fig.update_layout(**LAYOUT_DEFAULTS, height=height)
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.05)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)", zeroline=False)
    return fig


def line_chart(df: pd.DataFrame, x: str, y: str, title: str,
               color: str | None = None, height: int = 400) -> go.Figure:
    fig = px.line(
        df, x=x, y=y, color=color, title=title,
        color_discrete_sequence=COLORS, markers=True,
    )
    fig.update_traces(line=dict(width=2.5))
    return _apply_defaults(fig, height)


def bar_chart(df: pd.DataFrame, x: str, y: str, title: str,
              color: str | None = None, orientation: str = "v",
              height: int = 400, text_auto: bool = True) -> go.Figure:
    fig = px.bar(
        df, x=x, y=y, color=color, title=title,
        orientation=orientation,
        color_discrete_sequence=COLORS,
        text_auto=".2s" if text_auto else False,
    )
    fig.update_traces(textposition="outside", textfont_size=11)
    return _apply_defaults(fig, height)


def donut_chart(df: pd.DataFrame, values: str, names: str, title: str,
                height: int = 400) -> go.Figure:
    fig = px.pie(
        df, values=values, names=names, title=title, hole=0.5,
        color_discrete_sequence=COLORS,
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        textfont_size=12,
    )
    return _apply_defaults(fig, height)


def heatmap_chart(df_pivot: pd.DataFrame, title: str,
                  height: int = 450) -> go.Figure:
    fig = go.Figure(data=go.Heatmap(
        z=df_pivot.values,
        x=df_pivot.columns.tolist(),
        y=df_pivot.index.tolist(),
        colorscale=[[0, "#0E1117"], [0.5, "#6C5CE7"], [1, "#a29bfe"]],
        hovertemplate="<b>%{y}</b><br>%{x}: %{z:,.0f}<extra></extra>",
    ))
    fig.update_layout(title=title)
    return _apply_defaults(fig, height)


def comparison_chart(df1: pd.DataFrame, df2: pd.DataFrame,
                     x: str, y: str, label1: str, label2: str,
                     title: str, height: int = 400) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df1[x], y=df1[y], name=label1,
        marker_color=COLORS[0], opacity=0.85,
    ))
    fig.add_trace(go.Bar(
        x=df2[x], y=df2[y], name=label2,
        marker_color=COLORS[1], opacity=0.85,
    ))
    fig.update_layout(title=title, barmode="group")
    return _apply_defaults(fig, height)


def forecast_chart(df_history: pd.DataFrame, df_forecast: pd.DataFrame,
                   x: str, y: str, title: str,
                   height: int = 400) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_history[x], y=df_history[y], name="Факт",
        mode="lines+markers", line=dict(color=COLORS[0], width=2.5),
    ))
    fig.add_trace(go.Scatter(
        x=df_forecast[x], y=df_forecast[y], name="Прогноз",
        mode="lines+markers",
        line=dict(color=COLORS[3], width=2.5, dash="dash"),
    ))
    fig.update_layout(title=title)
    return _apply_defaults(fig, height)
