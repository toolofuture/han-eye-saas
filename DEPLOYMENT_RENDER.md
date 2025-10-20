# 🚀 Render.com 배포 가이드

## ✅ 완전 무료!

Render.com은 Python/Flask 앱을 **완전 무료**로 배포할 수 있어!

## 📋 배포 단계

### 1. Render 가입
1. https://dashboard.render.com 접속
2. **"Get Started for Free"** 클릭
3. GitHub 계정으로 로그인

### 2. GitHub 저장소 연결
1. Dashboard에서 **"New +"** → **"Blueprint"** 클릭
2. **"Connect a repository"** 선택
3. `toolofuture/han-eye-saas` 선택
4. **"Connect"** 클릭

### 3. 자동 배포 시작!
- `render.yaml` 파일을 Render가 자동으로 감지
- Web Service와 PostgreSQL 데이터베이스 자동 생성
- 5-10분 후 배포 완료!

### 4. 환경변수 설정
배포 완료 후 Dashboard에서:

**Environment** 탭에서 추가:
```
OPENAI_API_KEY=sk-your-key
ANTHROPIC_API_KEY=sk-ant-your-key
GOOGLE_API_KEY=AIza-your-key
```

### 5. 배포 URL 확인
```
https://han-eye-saas.onrender.com
```

## 🎯 render.yaml 설명

```yaml
services:
  - type: web
    name: han-eye-saas
    runtime: python
    plan: free              # 완전 무료!
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn run:app
    
databases:
  - name: han-eye-db
    plan: free              # PostgreSQL 무료!
```

## ✨ Render 장점

- ✅ **완전 무료 티어**
- ✅ **자동 배포**: GitHub push할 때마다 자동 재배포
- ✅ **PostgreSQL 무료**: 1GB 저장소
- ✅ **SSL 인증서**: 자동 설정
- ✅ **Custom 도메인**: 무료 지원
- ✅ **롤백**: 이전 버전으로 쉽게 복구

## ⚠️ 무료 티어 제한

- **Sleep 모드**: 15분 비활성 시 sleep (첫 요청 시 깨어남, ~30초 소요)
- **월 750시간**: 충분한 시간
- **1GB RAM**: 기본적인 사용에 충분

## 🔧 문제 해결

### 1. 배포 실패
- **Logs** 탭에서 에러 확인
- `requirements.txt` 확인
- Python 버전 확인

### 2. 데이터베이스 연결 오류
- `DATABASE_URL` 환경변수 자동 설정 확인
- PostgreSQL 서비스 상태 확인

### 3. AI API 오류
- Environment 탭에서 API 키 설정
- 서비스 재배포: Manual Deploy 클릭

## 📊 모니터링

- **Metrics**: CPU, 메모리, 응답 시간
- **Logs**: 실시간 로그 확인
- **Events**: 배포 히스토리

## 🎉 배포 완료!

배포가 완료되면:
```
https://han-eye-saas.onrender.com
```

이 주소로 Han.Eye SaaS에 접속할 수 있어!

