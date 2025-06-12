import streamlit as st
import serial
import serial.tools.list_ports

def find_usb_serial_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "USB SERIAL" in p.description.upper():
            return p.device
    return None

st.subheader("🔌 마이크로비트 연결")

selected_method = st.radio("포트 연결 방법 선택", ["자동 연결", "수동 입력"], horizontal=True)
selected_port = None

if selected_method == "자동 연결":
    if st.button("🔍 자동으로 포트 찾기"):
        with st.spinner("USB Serial 장치를 검색 중입니다..."):
            port = find_usb_serial_port()
            if port:
                st.success(f"✅ 포트 발견됨: `{port}`")
                selected_port = port
            else:
                st.error("❌ USB Serial 장치를 찾을 수 없습니다.")
elif selected_method == "수동 입력":
    manual_port = st.text_input("직접 포트를 입력하세요 (예: `COM3`, `/dev/ttyACM0` 등)")
    if manual_port:
        selected_port = manual_port
        st.info(f"🔗 입력된 포트: `{manual_port}`")

# 포트 연결 시도
if selected_port:
    if st.button("✅ 선택한 포트로 연결"):
        try:
            ser = serial.Serial(selected_port, 115200, timeout=1)
            st.success(f"🎉 연결 성공: `{selected_port}`")
            # 이후 코드에서 ser 사용 가능
        except Exception as e:
            st.error(f"⚠️ 연결 실패: {e}")
