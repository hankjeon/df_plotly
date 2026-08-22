"""판다스 DataFrame을 업로드해서 plotly로 시각화하는 Streamlit 앱.

동적 그래프 생성 기능을 지원합니다.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

st.set_page_config(page_title="df_plotly", layout="wide")

st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 3rem;
        }
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.title("df_plotly")

uploaded_file = st.file_uploader("Upload CSV or Parquet", type=["csv", "parquet"])

if uploaded_file is None:
    st.info("Upload a file to get started.")
    st.stop()

if uploaded_file.name.endswith(".parquet"):
    df = pd.read_parquet(uploaded_file)
else:
    df = pd.read_csv(uploaded_file)

st.caption(f"{uploaded_file.name} - {df.shape[0]} rows x {df.shape[1]} columns")
with st.expander("Preview data"):
    st.dataframe(df.head(20))

columns = list(df.columns)

# 세션 상태(Session State) 초기화: 그래프 목록 저장
if 'graphs' not in st.session_state:
    st.session_state.graphs = []
if 'graph_counter' not in st.session_state:
    st.session_state.graph_counter = 0

st.markdown("---")
st.markdown("### ➕ 새 그래프 추가")
col1, col2 = st.columns([2, 1])
with col1:
    new_graph_type = st.radio("그래프 타입 선택", ["Overlay (하나의 영역에 겹치기)", "Stacked (항목별 위아래 서브플롯)"], horizontal=True)
with col2:
    if st.button("그래프 생성하기", width='stretch'):
        st.session_state.graph_counter += 1
        st.session_state.graphs.append({
            "id": st.session_state.graph_counter,
            "type": "Overlay" if "Overlay" in new_graph_type else "Stacked",
            "x_col": columns[0] if columns else None,
            "y_cols": [],
            "secondary_cols": []
        })
        st.rerun()

st.markdown("---")

# 그래프 렌더링
for idx, g in enumerate(st.session_state.graphs):
    st.markdown(f"### 📊 그래프 {g['id']} ({g['type']})")
    
    col_x, col_y, col_del = st.columns([2, 5, 1])
    
    with col_x:
        # X축 독립 선택
        current_x_index = columns.index(g['x_col']) if g['x_col'] in columns else 0
        g['x_col'] = st.selectbox(f"X축 (기준) - 그래프 {g['id']}", columns, index=current_x_index, key=f"x_{g['id']}")
    
    with col_y:
        # Y축 항목 독립 추가
        valid_y_cols = [c for c in columns if c != g['x_col']]
        g['y_cols'] = st.multiselect(
            f"그래프에 추가할 항목 (Y축) - 그래프 {g['id']}", 
            valid_y_cols, 
            default=[c for c in g['y_cols'] if c in valid_y_cols], 
            key=f"y_{g['id']}"
        )
        
    with col_del:
        st.write("") # 버튼 위치 조정
        if st.button("❌ 삭제", key=f"del_{g['id']}", width='stretch'):
            st.session_state.graphs.pop(idx)
            st.rerun()

    # 오버랩 모드 보조 Y축
    if g['type'] == "Overlay" and len(g['y_cols']) > 1:
        g['secondary_cols'] = st.multiselect(
            f"오른쪽(보조) Y축으로 이동할 항목 (선택) - 그래프 {g['id']}",
            g['y_cols'],
            default=[c for c in g['secondary_cols'] if c in g['y_cols']],
            key=f"sec_{g['id']}"
        )
    elif g['type'] == "Overlay":
        g['secondary_cols'] = []
        
    # 그래프 그리기
    if not g['y_cols']:
        st.info("⬆️ 위에서 추가할 항목을 선택해 주세요.")
        st.markdown("---")
        continue
        
    if g['type'] == "Overlay":
        primary_cols = [c for c in g['y_cols'] if c not in g['secondary_cols']]
        fig = go.Figure()
        
        for y_col in g['y_cols']:
            fig.add_trace(go.Scatter(
                x=df[g['x_col']], 
                y=df[y_col], 
                mode='lines', 
                name=y_col,
                yaxis='y2' if y_col in g['secondary_cols'] else 'y'
            ))
            
        fig.update_layout(
            xaxis_title=g['x_col'],
            yaxis_title=", ".join(primary_cols),
            height=600,
            margin=dict(t=30)
        )
        fig.update_xaxes(showgrid=True)
        if g['secondary_cols']:
            fig.update_layout(yaxis2=dict(title=", ".join(g['secondary_cols']), overlaying='y', side='right'))
            
        st.plotly_chart(fig, width='stretch', height=600)
        
    elif g['type'] == "Stacked":
        # 높이를 줄이고(200), 서브플롯 간 여백(vertical_spacing)을 최소화
        chart_height = max(400, 200 * len(g['y_cols']))
        fig = make_subplots(
            rows=len(g['y_cols']), 
            cols=1, 
            shared_xaxes=True, 
            subplot_titles=g['y_cols'],
            vertical_spacing=0.03
        )
        
        for i, y_col in enumerate(g['y_cols'], start=1):
            fig.add_trace(go.Scatter(x=df[g['x_col']], y=df[y_col], mode='lines', name=y_col), row=i, col=1)
            
        fig.update_xaxes(showgrid=True)
        fig.update_xaxes(title_text=g['x_col'], row=len(g['y_cols']), col=1)
        fig.update_layout(height=chart_height, showlegend=False, margin=dict(t=30))
        
        st.plotly_chart(fig, width='stretch', height=chart_height)

    st.markdown("---")
