# 🚀 Han.Eye Vercel 배포 가이드

## 1. GitHub에 올리기

```bash
# GitHub에서 새 저장소 생성 후
git remote add origin https://github.com/YOUR_USERNAME/han-eye-saas.git
git push -u origin main
```

## 2. Vercel 배포

### 방법 1: Vercel CLI
```bash
npm i -g vercel
vercel login
vercel --prod
```

### 방법 2: Vercel Dashboard
1. https://vercel.com 접속
2. "New Project" 클릭
3. GitHub 저장소 연결
4. 자동 배포!

## 3. 환경변수 설정

Vercel Dashboard에서 다음 환경변수 설정:

```
SECRET_KEY=your-secret-key
OPENAI_API_KEY=sk-your-key
ANTHROPIC_API_KEY=sk-ant-your-key
GOOGLE_API_KEY=AIza-your-key
```

## 4. 데이터베이스 설정

Vercel Postgres 추가:
1. Vercel Dashboard → Storage
2. "Create Database" → Postgres
3. DATABASE_URL 자동 설정됨

## 5. 파일 업로드 설정

Vercel은 서버리스이므로 파일 업로드를 위해:
- AWS S3 또는 Cloudinary 사용 권장
- 또는 Vercel Blob Storage 사용

## 6. 강화학습 모델

학습된 모델은 GitHub에 포함되어 있지만:
- Vercel에서는 파일 시스템이 읽기 전용
- 모델을 외부 저장소에 업로드 필요 (AWS S3 등)

## 7. 배포 후 확인

```
https://your-app.vercel.app
```

## 문제 해결

### 1. 모듈 import 오류
```bash
pip install -r requirements.txt
```

### 2. 데이터베이스 연결 오류
- DATABASE_URL 확인
- Vercel Postgres 연결 상태 확인

### 3. 파일 업로드 오류
- 외부 스토리지 서비스 사용
- 또는 Vercel Blob Storage 설정
