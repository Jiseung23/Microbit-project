import streamlit as st
import serial
import serial.tools.list_ports

# 마이크로비트 VID:PID 목록
MICROBIT_IDS = ["0D28:0204"]  # 필요시 다른 VID:PID 추가 가능

# 자동 포트 탐색 함수
def find_microbit_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if any(vid_pid in p.hwid.upper() for vid_pid in MICROBIT_IDS):
            return p.device
    return None

# 앱 UI
st.subheader("🔌 마이크로비트 연결")

# 포트 선택 섹션
selected_method = st.radio("포트 연결 방법 선택", ["자동 연결", "수동 입력"], horizontal=True)

selected_port = None

if selected_method == "자동 연결":
    if st.button("🔍 자동으로 포트 찾기"):
        with st.spinner("마이크로비트를 찾는 중..."):
            port = find_microbit_port()
            if port:
                st.success(f"✅ 마이크로비트 포트: `{port}` 연결 가능")
                selected_port = port
            else:
                st.error("❌ 마이크로비트를 찾을 수 없습니다. USB 연결 또는 펌웨어 상태를 확인하세요.")
elif selected_method == "수동 입력":
    manual_port = st.text_input("포트를 직접 입력하세요 (예: `COM3`, `/dev/ttyACM0`, `/dev/tty.usbmodem1101`)")
    if manual_port:
        selected_port = manual_port
        st.info(f"🔗 입력된 포트: `{manual_port}`")

# 연결 시도 버튼
if selected_port:
    if st.button("✅ 선택한 포트로 연결"):
        try:
            ser = serial.Serial(selected_port, 115200, timeout=1)
            st.success(f"🎉 성공적으로 연결되었습니다: `{selected_port}`")
            # 이후 ser 인스턴스를 전역으로 전달하거나 세션 상태에 저장하세요
        except Exception as e:
            st.error(f"⚠️ 연결 실패: {e}")
