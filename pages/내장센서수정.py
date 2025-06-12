import streamlit as st
import pandas as pd
import plotly.express as px
import serial
import serial.tools.list_ports
import threading
import time

data = []
ser = None
is_collecting = False
lock = threading.Lock()

st.set_page_config(page_title="🌡️ 온도 실시간 측정", layout="centered")
st.title("🌡️ 마이크로비트 온도 측정기")
st.caption("USB로 연결된 마이크로비트를 직접 포트로 선택할 수 있어요.")

# 👉 모든 포트 나열
available_ports = list(serial.tools.list_ports.comports())
port_options = [f"{p.device} - {p.description}" for p in available_ports]

# ✅ 포트 수동 선택 UI
selected_port = st.selectbox("연결할 마이크로비트 포트를 선택하세요:", port_options)

# 포트 추출 (COM3 - USB Serial Port → COM3)
def extract_port(port_string):
    return port_string.split(" - ")[0] if port_string else None

# 마이크로비트 연결
if st.button("🔗 선택한 포트로 연결"):
    try:
        port_name = extract_port(selected_port)
        ser = serial.Serial(port_name, 115200, timeout=1)
        st.success(f"✅ {port_name} 포트에 성공적으로 연결되었습니다!")
    except Exception as e:
        st.error(f"❌ 포트 연결 실패: {e}")

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

# 수집 시작 / 종료
col1, col2 = st.columns(2)

if col1.button("▶ 데이터 수집 시작"):
    if ser:
        if not is_collecting:
            is_collecting = True
            threading.Thread(target=collect_data, daemon=True).start()
            st.success("📡 온도 데이터 수집을 시작했습니다.")
    else:
        st.warning("먼저 포트를 선택하여 마이크로비트를 연결하세요.")

if col2.button("■ 데이터 수집 종료"):
    if is_collecting:
        is_collecting = False
        st.warning("🛑 데이터 수집을 중지했습니다.")

# 실시간 그래프 및 최근 5개 표시
df = pd.DataFrame(data)

if not df.empty:
    fig = px.line(df, x="시간", y="온도(℃)", markers=True, title="📈 실시간 온도 변화")
    fig.update_layout(
        yaxis_title="온도 (℃)",
        xaxis_title="시간",
        font=dict(family="Nanum Gothic"),
        xaxis=dict(autorange=True),
        margin=dict(l=30, r=30, t=40, b=30),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### 🧾 최근 5개 측정값")
    st.dataframe(df.tail(5), use_container_width=True)
else:
    st.info("아직 수집된 데이터가 없습니다. 데이터를 수집해보세요!")

