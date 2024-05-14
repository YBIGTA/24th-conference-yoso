## 논문 생성 보조기
데이터베이스 서버
- 논모정 DB: MongoDB
- 임베딩 DB: Pinecone

## 실행
### 환경 변수 설정
`.env.example` 파일을 `.env`로 복사 후 모든 값 채워넣기

### 요구사항 설치
```bash
pip install -r requirements.txt
```

### JSON 파일 데이터 DB에 저장
```bash
python prototype/main.py
```
`dataset-test.json`에 있는 샘플 데이터 읽어서 Pinecone, MongoDB에 저장

### 쿼리
```bash
python prototype/query.py

도메인 (<q> to quit): Computer Vision
해결하고자 하는 문제: There's something wrong with ViT
해결 방법: I want to utilize convolutional neural network with idea from ViT

┌────────────┬────────┬────────────────────────────────────────────────────────┐
│ Embedding  │ Score  │ Title                                                  │
├────────────┼────────┼────────────────────────────────────────────────────────┤
│ Abstract   │ 0.5372 │ A ConvNet for the 2020s                                │
├────────────┼────────┼────────────────────────────────────────────────────────┤
│ Summarized │ 0.5220 │ Deep ViT: Towards Deeper Vision Transformer            │
└────────────┴────────┴────────────────────────────────────────────────────────┘
```
검색할 논문에 대한 문장 프롬프트 입력 후 결과 반환.
