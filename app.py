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


if "charts" not in st.session_state:
    st.session_state.charts = [{"id": 0}]
if "next_id" not in st.session_state:
    st.session_state.next_id = 1

def add_chart():
    st.session_state.charts.append({"id": st.session_state.next_id})
    st.session_state.next_id += 1

def remove_chart(cid):
    st.session_state.charts = [c for c in st.session_state.charts if c["id"] != cid]

x_col = st.selectbox("Global X axis", columns, index=0)

st.write("---")

valid_charts = []

for i, chart in enumerate(st.session_state.charts):
    cid = chart["id"]
    with st.container():
        c1, c2, c3 = st.columns([2, 5, 1])
        with c1:
            mode = st.radio("Layout", ["Overlay", "Stacked"], horizontal=True, key=f"mode_{cid}")
        with c2:
            y_cols = st.multiselect("Y axis", [c for c in columns if c != x_col], key=f"y_{cid}")
            secondary_cols = []
            if mode == "Overlay" and len(y_cols) > 1:
                secondary_cols = st.multiselect("Secondary Y axis", y_cols, key=f"sec_y_{cid}")
        with c3:
            st.button("Remove", key=f"remove_{cid}", on_click=remove_chart, args=(cid,))

        if y_cols:
            valid_charts.append({
                "mode": mode,
                "y_cols": y_cols,
                "secondary_cols": secondary_cols
            })
    st.write("---")

st.button("Add Chart", on_click=add_chart)

if not valid_charts:
    st.info("Select at least one Y axis column in any chart to render.")
    st.stop()

# Calculate total rows and specs for subplots
total_rows = 0
specs = []
subplot_titles = []

for chart in valid_charts:
    if chart["mode"] == "Overlay":
        total_rows += 1
        specs.append([{"secondary_y": bool(chart["secondary_cols"])}])
        subplot_titles.append(", ".join(chart["y_cols"]))
    else:
        total_rows += len(chart["y_cols"])
        for y_col in chart["y_cols"]:
            specs.append([{"secondary_y": False}])
            subplot_titles.append(y_col)

fig = make_subplots(
    rows=total_rows,
    cols=1,
    shared_xaxes=True,
    subplot_titles=subplot_titles,
    specs=specs
)

current_row = 1
for chart in valid_charts:
    if chart["mode"] == "Overlay":
        primary_cols = [c for c in chart["y_cols"] if c not in chart["secondary_cols"]]
        for y_col in chart["y_cols"]:
            fig.add_trace(
                go.Scatter(
                    x=df[x_col],
                    y=df[y_col],
                    mode="lines",
                    name=y_col,
                ),
                row=current_row,
                col=1,
                secondary_y=(y_col in chart["secondary_cols"])
            )

        # update y axis titles if needed
        fig.update_yaxes(title_text=", ".join(primary_cols), row=current_row, col=1, secondary_y=False)
        if chart["secondary_cols"]:
            fig.update_yaxes(title_text=", ".join(chart["secondary_cols"]), row=current_row, col=1, secondary_y=True)

        current_row += 1
    else:
        for y_col in chart["y_cols"]:
            fig.add_trace(
                go.Scatter(
                    x=df[x_col],
                    y=df[y_col],
                    mode="lines",
                    name=y_col
                ),
                row=current_row,
                col=1
            )
            current_row += 1

fig.update_xaxes(title_text=x_col, row=total_rows, col=1)
chart_height = 300 * total_rows
fig.update_layout(height=chart_height, showlegend=True)

st.plotly_chart(fig, use_container_width=True, height=chart_height)
