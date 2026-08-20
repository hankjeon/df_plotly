"""판다스 DataFrame을 업로드해서 plotly로 자유롭게 시각화하는 Streamlit 앱.

CSV/Parquet 파일을 올리면 컬럼 목록이 나오고, x축과 y축(복수 선택 가능)을 고르면 바로 그래프가 그려진다.
y축을 여러 개 고르면 한 그래프에 겹쳐서(Overlay) 보거나, 컬럼별 서브플롯으로 나눠서(Stacked) 볼 수 있다.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

st.set_page_config(page_title="df_plotly", layout="wide")
st.title("df_plotly")

uploaded_file = st.file_uploader("Upload CSV or Parquet", type=["csv", "parquet"])

if uploaded_file is None:
    st.info("Upload a file to get started.")
    st.stop()

if uploaded_file.name.endswith(".parquet"):
    df = pd.read_parquet(uploaded_file)
else:
    df = pd.read_csv(uploaded_file)

st.caption(f"{uploaded_file.name} — {df.shape[0]} rows x {df.shape[1]} columns")
with st.expander("Preview data"):
    st.dataframe(df.head(20))

columns = list(df.columns)

col1, col2 = st.columns([1, 2])
with col1:
    x_col = st.selectbox("X axis", columns, index=0)
with col2:
    y_cols = st.multiselect("Y axis (select one or more)", [c for c in columns if c != x_col])

if not y_cols:
    st.info("Select at least one Y axis column.")
    st.stop()

mode = st.radio("Layout", ["Overlay", "Stacked"], horizontal=True)

if mode == "Overlay":
    secondary_cols = []
    if len(y_cols) > 1:
        secondary_cols = st.multiselect(
            "Secondary Y axis (optional — for columns on a different scale)",
            y_cols,
        )
    primary_cols = [c for c in y_cols if c not in secondary_cols]

    chart_height = 600
    fig = go.Figure()
    for y_col in y_cols:
        fig.add_trace(
            go.Scatter(
                x=df[x_col],
                y=df[y_col],
                mode="lines",
                name=y_col,
                yaxis="y2" if y_col in secondary_cols else "y",
            )
        )
    fig.update_layout(
        xaxis_title=x_col,
        yaxis_title=", ".join(primary_cols),
        height=chart_height,
    )
    if secondary_cols:
        fig.update_layout(
            yaxis2=dict(title=", ".join(secondary_cols), overlaying="y", side="right")
        )
else:
    chart_height = 300 * len(y_cols)
    fig = make_subplots(rows=len(y_cols), cols=1, shared_xaxes=True, subplot_titles=y_cols)
    for i, y_col in enumerate(y_cols, start=1):
        fig.add_trace(go.Scatter(x=df[x_col], y=df[y_col], mode="lines", name=y_col), row=i, col=1)
    fig.update_xaxes(title_text=x_col, row=len(y_cols), col=1)
    fig.update_layout(height=chart_height, showlegend=False)

# st.plotly_chart의 height 기본값('content')은 fig.update_layout(height=...)를 반영하지 않고
# 고정 크기로 렌더링해 서브플롯이 잘리는 문제가 있어 - 여기서 명시적으로 넘겨줘야 함.
st.plotly_chart(fig, use_container_width=True, height=chart_height)
