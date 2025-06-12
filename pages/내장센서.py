import streamlit as st
import pandas as pd
import plotly.express as px
import serial
import serial.tools.list_ports
import threading
import time

# 전역 변수
data = []
ser = None
is_collecting = False
lock = threading.Lock()

# Streamlit 설정
st.set_page_config(page_title="🌡️ 온도 실시간 측정", layout="centered")
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Nanum+Gothic&display=swap');
        html, body, [class*="css"] {
            font-family: 'Nanum Gothic', sans-serif;
        }
        .stButton>button {
            font-size: 1.05em;
            padding: 0.5em 1.2em;
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🌡️ 마이크로비트 온도 측정기")
st.caption("마이크로비트를 USB로 연결하고, 버튼을 눌러 실시간 온도를 측정하세요.")

# 포트 탐색 함수
def find_microbit_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "MicroPython" in p.description or "mbed" in p.description or "micro:bit" in p.description.lower():
            return p.device
    return None

# 데이터 수집 스레드
def collect_data():
    global ser, is_collecting, data
    while is_collecting:
        try:
            line = ser.readline().decode("utf-8").strip()
            if line.isdigit():
                temp = int(line)
                timestamp = time.strftime("%H:%M:%S")
                with lock:
                    data.append({"시간": timestamp, "온도(℃)": temp})
        except Exception:
            continue
    if ser:
        ser.close()

# 마이크로비트 연결 섹션
st.subheader("🔌 Step 1. 마이크로비트 연결")

port = find_microbit_port()
available_ports = [p.device for p in serial.tools.list_ports.comports()]

port_option = st.selectbox(
    "자동으로 포트를 찾지 못하면 아래에서 수동으로 선택하세요:",
    options=["자동 선택"] + available_ports
)

if st.button("🔗 마이크로비트 연결"):
    try:
        selected = port if port_option == "자동 선택" else port_option
        ser = serial.Serial(selected, 115200, timeout=1)
        st.success(f"✅ 연결 성공! 포트: {selected}")
    except Exception as e:
        st.error(f"❌ 연결 실패: {e}")

# 수집 시작/정지 버튼
st.subheader("📡 Step 2. 온도 데이터 수집")

col1, col2 = st.columns(2)

if col1.button("▶ 시작", use_container_width=True):
    if ser:
        if not is_collecting:
            is_collecting = True
            threading.Thread(target=collect_data, daemon=True).start()
            st.success("📊 데이터 수집을 시작했습니다.")
    else:
        st.warning("먼저 마이크로비트를 연결하세요.")

if col2.button("■ 종료", use_container_width=True):
    if is_collecting:
        is_collecting = False
        st.warning("🛑 데이터 수집을 중지했습니다.")

# 실시간 시각화 섹션
st.subheader("📈 실시간 그래프 & 데이터")

df = pd.DataFrame(data)

if not df.empty:
    fig = px.line(df, x="시간", y="온도(℃)", markers=True, title="실시간 온도 변화")
    fig.update_layout(
        font=dict(family="Nanum Gothic"),
        margin=dict(l=30, r=30, t=40, b=30),
        yaxis_title="온도 (℃)",
        xaxis_title="시간",
        xaxis=dict(autorange=True)  # 자동 스케일
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### 📋 최근 측정값 (5개)")
    st.dataframe(df.tail(5), use_container_width=True)

else:
    st.info("아직 측정된 데이터가 없습니다. 수집을 시작하세요!")

# 하단 안내
st.markdown("---")
st.markdown("💡 **Tip:** 마이크로비트에 MicroPython이 업로드되어 있어야 연결이 됩니다.")
