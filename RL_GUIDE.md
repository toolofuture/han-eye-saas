

# 🤖 Han.Eye - Reinforcement Learning from Demonstration (RLfD)

**논문 기반 구현**: "Robust quantum control using reinforcement learning from demonstration" (Nature npj Quantum Information, 2025)

## 📚 개요

Han.Eye는 이제 **진짜 강화학습(Reinforcement Learning)**을 사용하여 자가개선됩니다!

### 기존 vs 새로운 방식

| 항목 | 기존 (휴리스틱) | 새로운 (RLfD) |
|------|----------------|---------------|
| **파라미터** | 고정 (threshold=0.7) | 동적 학습 |
| **학습** | 없음 | SAC 강화학습 |
| **개선** | 수동 조정 | 자동 최적화 |
| **데이터 활용** | 저장만 | 학습에 사용 |

## 🏗️ 구조

```
┌─────────────────────────────────────────┐
│  1. Demonstration (초기 지식)            │
│     - 휴리스틱 파라미터                  │
│     - 사용자 피드백                      │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  2. Pre-training (모방 학습)            │
│     - Behavioral Cloning                │
│     - Demonstration Replay Buffer       │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  3. RL Training (강화학습)              │
│     - Algorithm: SAC                    │
│     - Environment: Artwork Analysis     │
│     - Reward: User Feedback             │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  4. Optimized Model (최적화된 모델)     │
│     - 최적 threshold 자동 선택          │
│     - 최적 weights 자동 조정            │
└─────────────────────────────────────────┘
```

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
cd /Users/kangsikseo/Downloads/han-eye-saas

# RL 라이브러리 설치
pip install stable-baselines3 gymnasium
```

### 2. 데이터 수집

웹 인터페이스에서 이미지를 분석하고 피드백을 제공하세요:
- ✅ **정확함**: AI 판단이 맞았을 때
- ❌ **부정확함**: AI 판단이 틀렸을 때

**최소 5개 이상의 피드백이 필요합니다.**

### 3. RL 모델 학습

```bash
python scripts/train_rl_agent.py
```

학습 과정:
```
📊 데이터 수집 중...
✅ 수집된 학습 데이터: 10개
   - 진품: 6개
   - 위작: 4개

🤖 Reinforcement Learning from Demonstration (RLfD)
============================================================

📦 Step 1: 환경 생성...
   ✅ Batch environment with 10 images

🧠 Step 2: 에이전트 생성...
   ✅ RLfD Agent initialized

🎯 Step 3: Demonstration 생성...
   ✅ Total demonstrations: 13

🎓 Step 4: Pre-training (Behavioral Cloning)...
   ✅ Pre-training completed

🚀 Step 5: Reinforcement Learning...
   Training: 100%|████████| 5000/5000

📊 Step 6: 모델 평가...
   Mean Reward: 0.85

💾 Step 7: 모델 저장...
   ✅ Model saved

✅ RLfD Training Complete!
```

### 4. RL 모델 사용

학습된 모델은 자동으로 사용됩니다:

```python
# app/utils/rl_detector.py가 자동으로 로드
from app.utils.rl_detector import RLAnomalyDetector

detector = RLAnomalyDetector()
result = detector.analyze(image_path)

# RL 모델이 최적 파라미터 선택
print(f"RL threshold: {result['rl_threshold']}")  # 예: 0.73
print(f"RL weights: {result['rl_weights']}")      # 예: [0.3, 0.3, 0.2, 0.2]
```

## 🧠 강화학습 구조

### Environment (환경)

```python
class ArtworkAuthEnv:
    # State: 이미지 특징 [texture, edge, color, noise]
    observation_space = Box(low=0, high=1, shape=(4,))
    
    # Action: 이상탐지 파라미터 [threshold, weights...]
    action_space = Box(low=0, high=1, shape=(5,))
    
    # Reward: 사용자 피드백
    # +1: 정확한 판단
    # -1: 틀린 판단
```

### Agent (에이전트)

```python
# SAC (Soft Actor-Critic) 알고리즘
- Policy Network: 최적 action 선택
- Q-Networks: action의 가치 평가
- Entropy Regularization: 탐색과 활용 균형
```

### Demonstration

```python
# 1. 휴리스틱 파라미터
{
    'threshold': 0.7,
    'weights': [0.25, 0.25, 0.25, 0.25]
}

# 2. 사용자 피드백
{
    'image': 'artwork.jpg',
    'ground_truth': True,  # 진품
    'feedback': 'correct'
}
```

## 📊 성능 개선 예시

```
Initial (Heuristic):
  Threshold: 0.70 (fixed)
  Accuracy: 50%

After RLfD (100 samples):
  Threshold: 0.73 (learned)
  Accuracy: 65% (+15%p)

After RLfD (1000 samples):
  Threshold: 0.68 (learned)
  Accuracy: 78% (+28%p)
```

## 🔧 고급 설정

### 학습 파라미터 조정

```python
# scripts/train_rl_agent.py

train_with_rlfd(
    pretrain_epochs=100,      # Pre-training 반복 횟수
    train_timesteps=10000,    # RL 학습 스텝
)
```

### 알고리즘 변경

```python
# PPO 사용
from stable_baselines3 import PPO

model = PPO(
    "MlpPolicy",
    env,
    verbose=1,
    learning_rate=3e-4,
)
```

## 📈 모니터링

### TensorBoard 사용

```bash
# 학습 과정 시각화
tensorboard --logdir logs/

# 브라우저에서
http://localhost:6006
```

### 성능 평가

```python
from app.utils.rl_agent import RLfDAgent

agent = RLfDAgent(env)
agent.load('models/rl_artwork_agent')

metrics = agent.evaluate(n_eval_episodes=10)
print(f"Mean Reward: {metrics['mean_reward']}")
```

## 🎯 모범 사례

### 1. 충분한 데이터 수집

- ✅ 최소 10개 이상의 피드백
- ✅ 진품/위작 균형 (50:50)
- ✅ 다양한 스타일의 작품

### 2. 정기적인 재학습

```bash
# 새로운 피드백이 쌓이면 재학습
python scripts/train_rl_agent.py
```

### 3. A/B 테스트

```python
# 휴리스틱 vs RL 비교
heuristic_detector = AnomalyDetector()
rl_detector = RLAnomalyDetector()

# 동일 이미지로 비교
result1 = heuristic_detector.analyze(image)
result2 = rl_detector.analyze(image)
```

## 🐛 문제 해결

### "stable-baselines3 not installed"

```bash
pip install stable-baselines3 gymnasium
```

### "No training data available"

웹에서 피드백을 더 수집하세요 (최소 5개)

### "Training failed"

```bash
# 로그 확인
tail -f logs/rl_training.log

# 환경 테스트
python -c "from app.utils.rl_environment import ArtworkAuthEnv; print('OK')"
```

## 📚 참고 자료

- **논문**: [Robust quantum control using reinforcement learning from demonstration](https://doi.org/10.1038/s41534-025-01065-2)
- **Stable-Baselines3**: https://stable-baselines3.readthedocs.io/
- **Gymnasium**: https://gymnasium.farama.org/

## 🎉 결과

RLfD를 사용하면:
- ✅ **자동 파라미터 최적화**: 수동 조정 불필요
- ✅ **지속적 개선**: 피드백이 쌓일수록 정확도 향상
- ✅ **샘플 효율성**: 적은 데이터로도 학습 가능
- ✅ **안정적 학습**: Demonstration으로 초기화

**50% → 80% 정확도 목표를 달성하기 위한 핵심 기술입니다!** 🚀

