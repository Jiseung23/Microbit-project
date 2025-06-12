import streamlit as st
import plotly.graph_objs as go
import serial
import serial.tools.list_ports
import time
import pandas as pd
from collections import deque

# --- 기본 설정 ---
st.set_page_config(page_title="DHT22 온도 모니터링", layout="wide")

# --- 한글 폰트 및 디자인 스타일 설정 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR&display=swap');

    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
    }

    h1, h2, h3, h4, h5, h6 {
        font-weight: 700;
    }

    button[kind="primary"] {
        border-radius: 12px !important;
        background-color: #4CAF50;
        color: white;
        padding: 0.5em 1em;
        font-weight: bold;
        font-size: 16px;
    }

    .stMetric {
        font-size: 18px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 상태 초기화 ---
for key in ["connected", "collecting", "ser", "data1", "data2", "timestamps", "table1", "table2"]:
    if key not in st.session_state:
        st.session_state[key] = False if key in ["connected", "collecting"] else (
            deque(maxlen=50) if "data" in key or key == "timestamps" else deque(maxlen=5)
        )

# --- 포트 검색 함수 ---
def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports if "USB" in port.description or "Serial" in port.description]

# --- 헤더 영역 ---
st.title("🌡️ DHT22 듀얼 온도 측정 실시간 모니터링")

# --- 포트 선택 및 연결 버튼 ---
st.subheader("🔌 마이크로비트 연결")
available_ports = list_serial_ports()
port = st.selectbox("자동 검색된 포트 목록", available_ports)

col_conn, col_stat = st.columns([1, 3])
with col_conn:
    if st.button("🔌 마이크로비트 연결", use_container_width=True):
        if port:
            try:
                st.session_state.ser = serial.Serial(port, 115200, timeout=1)
                st.session_state.connected = True
                st.success(f"{port} 연결 성공!")
            except Exception as e:
                st.error(f"연결 실패: {e}")
        else:
            st.warning("포트를 찾을 수 없습니다.")

with col_stat:
    if st.session_state.connected:
        st.success("🟢 연결됨")
    else:
        st.info("🔴 연결되지 않음")

# --- 데이터 수집 토글 ---
st.subheader("📡 데이터 수집")
col_start, col_stop = st.columns(2)
with col_start:
    if st.session_state.connected and not st.session_state.collecting:
        if st.button("▶️ 수집 시작", use_container_width=True):
            st.session_state.collecting = True

with col_stop:
    if st.session_state.collecting:
        if st.button("⏹️ 수집 종료", use_container_width=True):
            st.session_state.collecting = False

# --- 현재 온도 메트릭 표시 ---
if st.session_state.collecting and st.session_state.connected:
    if st.session_state.ser.in_waiting:
        line = st.session_state.ser.readline().decode("utf-8").strip()
        try:
            temp1_str, temp2_str = line.split(",")
            temp1 = float(temp1_str)
            temp2 = float(temp2_str)
            now = time.strftime("%H:%M:%S")

            st.session_state.data1.append(temp1)
            st.session_state.data2.append(temp2)
            st.session_state.timestamps.append(now)

            st.session_state.table1.append({"시간": now, "센서1 온도": temp1})
            st.session_state.table2.append({"시간": now, "센서2 온도": temp2})

            # --- 메트릭 표시 ---
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("센서 1 현재 온도", f"{temp1:.1f}°C")
            col_m2.metric("센서 2 현재 온도", f"{temp2:.1f}°C")

            # --- 실시간 그래프 ---
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=list(st.session_state.timestamps),
                y=list(st.session_state.data1),
                mode='lines+markers',
                name='센서 1',
                line=dict(color='orange')
            ))
            fig.add_trace(go.Scatter(
                x=list(st.session_state.timestamps),
                y=list(st.session_state.data2),
                mode='lines+markers',
                name='센서 2',
                line=dict(color='dodgerblue')
            ))
            fig.update_layout(
                title="📈 실시간 온도 그래프",
                xaxis_title="시간",
                yaxis_title="온도 (°C)",
                template='simple_white',
                font=dict(family="Noto Sans KR", size=14)
            )
            st.plotly_chart(fig, use_container_width=True)

            # --- 최근 5개 데이터 테이블 ---
            st.subheader("🧾 최근 5개 측정값")
            col_t1, col_t2 = st.columns(2)
            df1 = pd.DataFrame(list(st.session_state.table1))
            df2 = pd.DataFrame(list(st.session_state.table2))
            col_t1.table(df1)
            col_t2.table(df2)

        except ValueError:
            st.warning(f"잘못된 데이터 수신: {line}")
    time.sleep(2)
