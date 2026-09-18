import random
import time
import ssl
import paho.mqtt.client as mqtt

# --- 설정 정보 ---
broker = "HOST"
port = 0  # MQTTS 포트
client_id = f'test-client-{random.randint(1000, 9999)}'


def on_connect(client, userdata, flags, rc):
    """연결 시도 후 결과를 출력하는 콜백 함수"""
    if rc == 0:
        print("✅ MQTT 브로커 연결 성공!")
        # 연결에 성공하면 바로 연결을 끊고 종료합니다.
        client.disconnect()
    elif rc == 5:
        print("❌ 연결 실패: 반환 코드 5 (인증 실패). 사용자 이름/비밀번호를 확인하세요.")
    else:
        print(f"❌ 연결 실패: 반환 코드 {rc}")

    # 연결 상태 확인 후 루프 종료를 요청합니다.
    client.loop_stop()


# --- 메인 연결 로직 ---
try:
    # 1. 클라이언트 생성
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
    client.on_connect = on_connect

    # 2. TLS/SSL 설정 (8883 포트 사용)
    # 서버 인증서 검증을 생략하고 TLSv1.2 프로토콜을 사용합니다.
    client.tls_set(tls_version=ssl.PROTOCOL_TLSv1_2, cert_reqs=ssl.CERT_NONE)

    # 3. 사용자 인증 정보 (필요시 주석을 해제하고 사용하세요)
    # client.username_pw_set("your_username", "your_password")

    print(f"➡️ 브로커 {broker}:{port} 로 연결 시도 중...")

    # 4. 연결 시도
    client.connect(broker, port, keepalive=60)

    # 5. 네트워크 루프 시작 (콜백 함수 처리를 위해 필요)
    client.loop_start()

    # 연결 결과가 나올 때까지 잠시 대기
    time.sleep(5)

    # loop_start() 후 on_connect 콜백에서 client.loop_stop()을 호출하여 종료되기를 기다립니다.

except KeyboardInterrupt:
    print("\n테스트 중지 요청")
except Exception as e:
    print(f"🔥 치명적인 오류 발생: {e}")
finally:
    try:
        if client.is_connected():
            client.disconnect()
        print("👋 연결 해제 및 프로그램 종료")
    except NameError:
        pass  # client 객체가 정의되지 않은 경우 통과