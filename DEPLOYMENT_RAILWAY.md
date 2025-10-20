# 🚀 Railway 배포 가이드

## 1. Railway 접속 및 설정

### 1.1 Railway 가입
1. https://railway.app 접속
2. GitHub 계정으로 로그인
3. "New Project" 클릭

### 1.2 GitHub 저장소 연결
1. "Deploy from GitHub repo" 선택
2. `toolofuture/han-eye-saas` 저장소 선택
3. "Deploy Now" 클릭

## 2. 환경변수 설정

Railway Dashboard → Variables 탭에서 다음 환경변수 추가:

```
SECRET_KEY=han-eye-production-secret-2025
FLASK_APP=run.py
FLASK_ENV=production
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
GOOGLE_API_KEY=AIza-your-google-key
```

## 3. 데이터베이스 설정

### 3.1 PostgreSQL 추가
1. Railway Dashboard → "New" → "Database" → "PostgreSQL"
2. `DATABASE_URL` 자동 설정됨

### 3.2 데이터베이스 초기화
Railway Console에서:
```bash
python init_db.py
```

## 4. 배포 확인

### 4.1 배포 URL
- Railway Dashboard → "Deployments" → URL 확인
- 예: `https://han-eye-saas-production.up.railway.app`

### 4.2 로그 확인
- Railway Dashboard → "Deployments" → "View Logs"
- 오류 발생시 로그 확인

## 5. 파일 업로드 설정

Railway는 파일 시스템이 영구적이므로:
- 업로드된 파일이 유지됨
- 별도 스토리지 서비스 불필요

## 6. 강화학습 모델

- GitHub에 포함된 모델 파일 사용 가능
- Railway 파일 시스템에서 정상 작동

## 7. 무료 티어 제한

- **월 $5 크레딧**
- **750시간 실행 시간**
- **1GB RAM**
- **1GB 디스크**

## 8. 문제 해결

### 8.1 배포 실패
- 로그 확인: Railway Dashboard → Logs
- 환경변수 확인: Variables 탭
- 의존성 확인: requirements.txt

### 8.2 데이터베이스 연결 오류
- `DATABASE_URL` 확인
- PostgreSQL 서비스 상태 확인

### 8.3 AI API 오류
- API 키 유효성 확인
- API 사용량 확인

## 9. 성능 최적화

### 9.1 메모리 사용량
- 이미지 처리 최적화
- 캐싱 전략 구현

### 9.2 응답 시간
- AI API 호출 최적화
- 데이터베이스 쿼리 최적화

## 10. 모니터링

- Railway Dashboard → Metrics
- CPU, 메모리, 네트워크 사용량 확인
- 오류율 모니터링
