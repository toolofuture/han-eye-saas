# Han.Eye - 자기개선형 가짜 미술품 검증 AI 서비스

![Han.Eye Logo](https://img.shields.io/badge/Han.Eye-AI%20Art%20Authentication-blueviolet)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

> 미술품이 금융 자산처럼 신뢰받을 수 있는 투명한 시장을 만들어, AI 기술로 예술의 진위를 판단하고 스스로 성장하는 새로운 패러다임을 제시합니다.

## 📋 목차

- [프로젝트 소개](#프로젝트-소개)
- [핵심 기능](#핵심-기능)
- [기술 스택](#기술-스택)
- [설치 방법](#설치-방법)
- [사용 방법](#사용-방법)
- [API 문서](#api-문서)
- [프로젝트 구조](#프로젝트-구조)
- [로드맵](#로드맵)
- [기여하기](#기여하기)
- [라이선스](#라이선스)

## 🎨 프로젝트 소개

Han.Eye는 LLM 기반으로 미술품 이미지를 분석하여 진품/가품을 자동 판별하는 AI 감정 시스템입니다. 

### 주요 특징

- **멀티모델 AI 분석**: GPT-4, Claude, Gemini를 활용한 정확한 진위 판별
- **Re-flexion 자기개선**: 판단→평가→기록→개선 순환 구조로 지속적 성능 향상
- **이상탐지 시스템**: 컴퓨터 비전 기반 이중 검증
- **The Met API 통합**: 메트로폴리탄 박물관 데이터 활용
- **실시간 분석**: 10-30초 내 신속한 결과 제공

### 현황

- **현재 정확도**: 50% 이상
- **목표 정확도**: 80% 이상
- **MVP 완성**: 2025 Q4
- **정식 런칭**: 2026 Q3

## ✨ 핵심 기능

### 1. AI 진위 감정

```python
# 이미지 업로드 → AI 분석 → 결과 확인
- 지원 형식: PNG, JPG, JPEG, GIF, WEBP
- 최대 파일 크기: 16MB
- 처리 시간: 10-30초
```

### 2. Re-flexion 자기개선

```
판단 (Judgment) → 평가 (Evaluation) → 기록 (Recording) → 개선 (Improvement)
```

AI가 자신의 판단을 재평가하고 개선하는 순환 학습 시스템

### 3. 이상탐지 시스템

- 텍스처 패턴 분석
- 엣지 검출 및 분석
- 색상 분포 평가
- 노이즈 패턴 감지

### 4. 사용자 대시보드

- 분석 통계 및 히스토리
- Re-flexion 학습 진행 상황
- 성능 향상 추이 확인

## 🛠 기술 스택

### Backend
- **Framework**: Flask 3.0.0
- **Database**: SQLAlchemy (SQLite/PostgreSQL)
- **Authentication**: Flask-Login
- **Migration**: Flask-Migrate

### AI/ML
- **LLM**: OpenAI GPT-4, Anthropic Claude, Google Gemini
- **Computer Vision**: OpenCV, Pillow
- **Data Processing**: NumPy

### Frontend
- **UI Framework**: Bootstrap 5.3.0
- **Icons**: Font Awesome 6.4.0
- **JavaScript**: Vanilla JS

### External APIs
- The Metropolitan Museum of Art Collection API

## 🚀 설치 방법

### 사전 요구사항

- Python 3.9 이상
- pip (Python package manager)
- 가상환경 (권장)

### 설치 단계

1. **저장소 클론**

```bash
git clone https://github.com/toolofuture/han-eye-saas.git
cd han-eye-saas
```

2. **가상환경 생성 및 활성화**

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

3. **의존성 설치**

```bash
pip install -r requirements.txt
```

4. **환경 변수 설정**

`.env` 파일을 생성하고 다음 내용을 입력:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_APP=run.py
FLASK_ENV=development

# Database (선택사항 - 기본값은 SQLite)
DATABASE_URL=sqlite:///han_eye.db

# AI API Keys (하나 이상 필수)
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GOOGLE_API_KEY=your-google-api-key
```

5. **데이터베이스 초기화**

```bash
python init_db.py
```

6. **애플리케이션 실행**

```bash
python run.py
```

7. **브라우저에서 접속**

```
http://localhost:5000
```

## 📖 사용 방법

### 1. 회원가입 및 로그인

1. 메인 페이지에서 "시작하기" 클릭
2. 이메일과 비밀번호로 회원가입
3. 로그인하여 대시보드 접속

### 2. 미술품 분석

1. "분석하기" 메뉴 선택
2. 미술품 이미지 업로드
3. AI 모델 선택 (GPT-4 권장)
4. 선택사항: 작가, 시대, 매체 정보 입력
5. Re-flexion 활성화 (선택사항)
6. "분석 시작" 클릭

### 3. 결과 확인

- **진품 가능성**: 진품/위작/불확실
- **확신도**: 0-100% 신뢰도 점수
- **이상탐지 점수**: 의심스러운 패턴 수준
- **분석 상세**: 스타일, 기술, 의심 요소

### 4. Re-flexion 실행

분석 결과 페이지에서 "Re-flexion 실행" 버튼을 클릭하여 AI 자기개선 프로세스를 시작할 수 있습니다.

## 🔌 API 문서

### 인증

모든 API 요청은 로그인된 세션이 필요합니다.

### 엔드포인트

#### 미술품 분석

```http
POST /api/analyze
Content-Type: multipart/form-data

Parameters:
- artwork_image: file (required)
- artist: string (optional)
- period: string (optional)
- medium: string (optional)
- ai_model: string (optional, default: gpt-4)

Response:
{
  "success": true,
  "analysis_id": 123,
  "result": {
    "is_authentic": true,
    "confidence_score": 0.85,
    "anomaly_score": 0.23,
    ...
  }
}
```

#### 분석 결과 조회

```http
GET /api/analysis/{analysis_id}

Response:
{
  "success": true,
  "analysis": {
    "id": 123,
    "is_authentic": true,
    "confidence_score": 0.85,
    ...
  }
}
```

#### 피드백 제출

```http
POST /api/analysis/{analysis_id}/feedback
Content-Type: application/json

Body:
{
  "feedback": "correct|incorrect|uncertain",
  "expert_verification": true
}
```

#### Re-flexion 실행

```http
POST /api/reflexion/{analysis_id}

Response:
{
  "success": true,
  "reflexion": {
    "iteration": 1,
    "confidence_delta": 0.05,
    ...
  }
}
```

## 📁 프로젝트 구조

```
han-eye-saas/
├── app/
│   ├── __init__.py           # Flask 앱 팩토리
│   ├── models/               # 데이터베이스 모델
│   │   ├── user.py
│   │   ├── artwork.py
│   │   ├── analysis.py
│   │   └── reflexion.py
│   ├── routes/               # 라우트 블루프린트
│   │   ├── main.py
│   │   ├── auth.py
│   │   └── api.py
│   ├── utils/                # 유틸리티 함수
│   │   ├── ai_analyzer.py
│   │   ├── anomaly_detector.py
│   │   ├── met_api.py
│   │   └── reflexion.py
│   ├── static/               # 정적 파일
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── templates/            # HTML 템플릿
│       ├── base.html
│       ├── index.html
│       ├── dashboard.html
│       └── ...
├── data/                     # 데이터 저장소
│   └── uploads/
├── logs/                     # 로그 파일
├── requirements.txt          # Python 의존성
├── .env                      # 환경 변수 (생성 필요)
├── run.py                    # 애플리케이션 진입점
├── init_db.py               # 데이터베이스 초기화
└── README.md                # 프로젝트 문서
```

## 🗺 로드맵

### 2025 Q4 - MVP 완성 ✅
- [x] The Met API 데이터 수집
- [x] LLM 파인튜닝 및 이상탐지 모델 설계
- [x] Flask 기반 웹 구현
- [x] Re-flexion 루프 구축
- [x] 50% 정확도 달성

### 2026 Q1 - Re-flexion 고도화
- [ ] 자동 학습 시스템 고도화
- [ ] 70% 정확도 달성
- [ ] 사용자 피드백 통합
- [ ] 성능 모니터링 대시보드

### 2026 Q2 - 베타 테스트
- [ ] 실제 미술 시장 적용
- [ ] 전문가 그룹 테스트
- [ ] 피드백 기반 개선
- [ ] API 공개 베타

### 2026 Q3 - 정식 서비스
- [ ] 80% 이상 정확도 달성
- [ ] 상용 서비스 런칭
- [ ] B2B 파트너십
- [ ] 블록체인 인증서 시스템

## 🤝 기여하기

Han.Eye 프로젝트에 기여해주셔서 감사합니다!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 👥 팀

- **AI 엔지니어**: LLM 파인튜닝 및 이상탐지 모델 개발
- **풀스택 개발자**: Flask 백엔드 및 웹 프론트엔드 구현
- **미술 전문가**: 데이터 검증 및 도메인 지식 제공
- **데이터 사이언티스트**: 데이터 수집 및 전처리 자동화

## 📞 연락처

- **Email**: contact@han-eye.com
- **Website**: https://han-eye.com
- **Project Link**: https://github.com/toolofuture/han-eye-saas

## 🙏 감사의 말

- The Metropolitan Museum of Art for their Open Access API
- OpenAI, Anthropic, Google for AI model access
- Open source community

---

**Han.Eye** - *예술과 AI가 만나 더 투명하고 신뢰할 수 있는 미술 시장을 만듭니다*
