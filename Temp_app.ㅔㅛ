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

# 마이크로비트 포트 자동 탐색
def find_microbit_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "MicroPython" in p.description or "mbed" in p.description or "micro:bit" in p.description.lower():
            return p.device
    return None

# 데이터 수집 스레드 함수
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

# Streamlit 설정
st.set_page_config(page_title="마이크로비트 실시간 온도 측정기", layout="centered")
st.title("🌡️ 마이크로비트 실시간 온도 측정기")
st.markdown("USB로 연결된 마이크로비트에서 온도 데이터를 실시간으로 받아 시각화합니다.")

# CSS 스타일 및 한글 폰트
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nanum+Gothic&display=swap');
html, body, [class*="css"] {
    font-family: 'Nanum Gothic', sans-serif;
}
.stButton>button {
    font-size: 1.1em;
    padding: 0.6em 1.2em;
    border-radius: 12px;
    background-color: #4CAF50;
    color: white;
    border: none;
}
.stButton>button:hover {
    background-color: #45a049;
}
</style>
""", unsafe_allow_html=True)

# 마이크로비트 연결 버튼
if st.button("🔌 마이크로비트 연결"):
    port = find_microbit_port()
    if port:
        try:
            ser = serial.Serial(port, 115200, timeout=1)
            st.success(f"마이크로비트 연결 성공! ({port})")
        except Exception as e:
            st.error(f"포트 열기 실패: {e}")
    else:
        st.error("마이크로비트를 찾을 수 없습니다. USB 연결 상태를 확인해주세요.")

# 수집 시작/종료 버튼
col1, col2 = st.columns(2)

if col1.button("▶ 데이터 수집 시작", use_container_width=True):
    if ser:
        if not is_collecting:
            is_collecting = True
            threading.Thread(target=collect_data, daemon=True).start()
            st.success("데이터 수집을 시작했습니다.")
    else:
        st.error("먼저 마이크로비트를 연결해주세요.")

if col2.button("■ 데이터 수집 종료", use_container_width=True):
    if is_collecting:
        is_collecting = False
        st.warning("데이터 수집이 중지되었습니다.")

# 데이터프레임 생성
df = pd.DataFrame(data)

# 실시간 그래프 출력
if not df.empty:
    st.subheader("📈 실시간 온도 변화 그래프")
    fig = px.line(df, x="시간", y="온도(℃)", markers=True, title="실시간 온도 추이")
    fig.update_layout(
        font=dict(family="Nanum Gothic"),
        margin=dict(l=30, r=30, t=40, b=30),
        yaxis_title="온도 (℃)",
        xaxis_title="시간",
        xaxis=dict(autorange=True)  # X축 자동 확장 설정
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 최근 측정값 (5개)")
    st.dataframe(df.tail(5), use_container_width=True)

# 안내 메시지
st.markdown("---")
st.markdown("💡 **Tip:** 마이크로비트를 먼저 USB로 연결한 후 '마이크로비트 연결' 버튼을 눌러주세요.")
