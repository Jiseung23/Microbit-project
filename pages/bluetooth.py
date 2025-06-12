import streamlit as st
import serial
import serial.tools.list_ports

# 블루투스로 연결된 COM 포트 자동 탐색 (이름에 'Bluetooth' 또는 'HC-05'가 포함될 수 있음)
def find_bluetooth_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if 'HC-05' in p.description.upper() or 'BLUETOOTH' in p.description.upper():
            return p.device
    return None

st.subheader("📶 마이크로비트 블루투스 연결")

selected_method = st.radio("포트 연결 방법 선택", ["자동 연결", "수동 입력"], horizontal=True)
selected_port = None

if selected_method == "자동 연결":
    if st.button("🔍 블루투스 포트 자동 탐색"):
        with st.spinner("블루투스 포트 탐색 중..."):
            port = find_bluetooth_port()
            if port:
                st.success(f"✅ 블루투스 포트 발견: `{port}`")
                selected_port = port
            else:
                st.error("❌ 블루투스 장치를 찾을 수 없습니다.\n페어링 후 COM 포트가 생성되었는지 확인하세요.")
elif selected_method == "수동 입력":
    manual_port = st.text_input("블루투스 COM 포트를 직접 입력하세요 (예: `COM6`, `/dev/tty.HC-05-DevB`)")  
    if manual_port:
        selected_port = manual_port
        st.info(f"🔗 입력된 포트: `{manual_port}`")

if selected_port:
    if st.button("✅ 블루투스 포트에 연결"):
        try:
            ser = serial.Serial(selected_port, 9600, timeout=1)  # HC-05는 보통 9600bps
            st.success(f"🎉 블루투스 연결 성공: `{selected_port}`")
            st.session_state.ser = ser  # 이후 데이터 수집 코드에서 사용
        except Exception as e:
            st.error(f"⚠️ 연결 실패: {e}")
