## 논문 생성 보조기
데이터베이스 서버
- 논모정 DB: MongoDB
- 임베딩 DB: Pinecone
- 그래프 DB: Neo4j

## 실행
### 환경 변수 설정
`.env.example` 파일을 `.env`로 복사 후 모든 값 채워넣기

### 도커 컨테이너 실행
```bash
docker compose up --build server graph
```

### 실행 테스트
```bash
curl -X 'GET' \
  'http://localhost/ping' \
  -H 'accept: application/json'
```

### 프로토타입 데이터로 DB 초기화
```bash
python initialize.py
```