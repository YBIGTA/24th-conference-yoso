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
docker compose up --build server
```

### REST API 호출
```bash
GET localhost/search?domain=<도메인>&problem=<문제>&solution=<해결방안>
```