# Han.Eye 빠른 시작 가이드

## 1단계: 환경 설정

```bash
cd /Users/kangsikseo/Downloads/han-eye-saas

# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

## 2단계: 환경 변수 설정

`.env` 파일을 생성하세요:

```bash
cp .env.example .env
```

그리고 `.env` 파일을 편집하여 최소한 하나의 AI API 키를 설정하세요:

```env
SECRET_KEY=han-eye-secret-key-2025
FLASK_APP=run.py
FLASK_ENV=development

# 최소 하나의 API 키 필요 (테스트 시에는 없어도 demo 모드로 동작)
OPENAI_API_KEY=your-key-here
# ANTHROPIC_API_KEY=your-key-here
# GOOGLE_API_KEY=your-key-here
```

## 3단계: 데이터베이스 초기화

```bash
python init_db.py
```

이 명령어는:
- 데이터베이스 테이블 생성
- 관리자 계정 생성 (admin@han-eye.com / admin123)
- 필요한 디렉토리 생성

## 4단계: 애플리케이션 실행

```bash
python run.py
```

## 5단계: 브라우저에서 접속

```
http://localhost:5000
```

## 기본 계정 정보

- **이메일**: admin@han-eye.com
- **비밀번호**: admin123

⚠️ **중요**: 첫 로그인 후 반드시 비밀번호를 변경하세요!

## 주요 기능 테스트

1. **회원가입**: 새 계정 생성
2. **로그인**: 생성한 계정으로 로그인
3. **분석하기**: 미술품 이미지 업로드 및 분석
4. **대시보드**: 분석 통계 확인
5. **Re-flexion**: 자기개선 시스템 테스트
6. **API**: REST API 엔드포인트 사용

## AI API 키 없이 테스트

API 키가 없어도 Demo 모드로 실행됩니다:
- 랜덤한 분석 결과 생성
- 모든 기능 테스트 가능
- UI/UX 확인 가능

실제 AI 분석을 위해서는 최소 하나의 API 키가 필요합니다.

## 문제 해결

### 포트가 이미 사용 중인 경우

```bash
# .env 파일에 다른 포트 지정
FLASK_PORT=5001
```

### 데이터베이스 초기화 오류

```bash
# 기존 데이터베이스 삭제 후 재생성
rm han_eye.db
python init_db.py
```

### 의존성 설치 오류

```bash
# pip 업그레이드
pip install --upgrade pip

# 개별 설치
pip install Flask==3.0.0
pip install Flask-SQLAlchemy==3.1.1
# ... 나머지 패키지
```

## 다음 단계

- README.md 파일을 읽어 전체 프로젝트 이해
- API 문서를 참조하여 REST API 사용
- The Met API로 실제 미술품 데이터 수집
- Re-flexion 시스템으로 AI 성능 향상

즐거운 개발 되세요! 🎨✨

