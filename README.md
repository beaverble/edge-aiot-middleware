# Edge AIoT 미들웨어 (복합상황인지 · 트래픽 감소)

스마트시티 Edge AIoT 국책 R&D에서 개발한 엣지 미들웨어 구성요소 모음이다.
Edge Gateway에서 환경·영상·음성 센서 데이터를 수집·분석·중계하는 파이프라인 중, 본인이 구현한 부분을 담았다.

<br>

## 담당 구현

- **트래픽 감소 필터링** (`traffic-filtering/`)
  - EMA(지수이동평균) 기준선 이탈량 기반 필터링으로 전송량 저감
  - 공인시험 트래픽 감소율 15%↑ 검증
- **ZeroMQ + CBOR 이벤트 브릿지** (`zeromq-bridge/`)
  - 영상검출·센서 이벤트를 ZeroMQ + CBOR로 수신 → JSON 변환 → MQTT 재발행
- **디바이스 데이터 처리** (`aiot-mqtt/`)
  - TLV·CBOR·Base64 페이로드 디코딩, MQTT 연동
- **디바이스 연동 API** (`device-api/`)
  - OAuth2 토큰 인증 기반 애플리케이션·디바이스 조회 및 MQTT 구독
- **분석 노트북** (`notebooks-aiot/`, `notebooks-mqtt/`)
  - 양수/음수 분리, 절대값 차분 등 트래픽 감소 알고리즘 실험

<br>

## 메모

- 서버 주소·자격증명은 환경변수로 주입하며 저장소에 포함하지 않는다.
- 데이터·모델 가중치는 제외했다.

<br>

## 기술 스택

Python · ZeroMQ · CBOR · TLV · Base64 · MQTT(paho) · Redis
