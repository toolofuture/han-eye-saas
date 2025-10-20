#!/usr/bin/env python3
"""
Train RL Agent with Reinforcement Learning from Demonstration (RLfD)

Usage:
    python scripts/train_rl_agent.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app, db
from app.models import Analysis
from app.utils.rl_environment import ArtworkAuthEnv, BatchArtworkEnv
from app.utils.rl_agent import RLfDAgent, create_default_demonstrations
import numpy as np


def collect_training_data():
    """사용자 피드백이 있는 분석 데이터 수집"""
    app = create_app()
    
    with app.app_context():
        # 피드백이 있는 분석들
        analyses = Analysis.query.filter(
            Analysis.user_feedback.in_(['correct', 'incorrect'])
        ).all()
        
        if len(analyses) < 5:
            print(f"⚠️  피드백 데이터 부족: {len(analyses)}개 (최소 5개 권장)")
            print("   사용자 피드백을 더 수집해주세요!")
            return []
        
        image_paths = []
        ground_truths = []
        
        for analysis in analyses:
            if not os.path.exists(analysis.image_path):
                continue
            
            # Ground truth 결정
            if analysis.user_feedback == 'correct':
                ground_truth = analysis.is_authentic
            else:
                ground_truth = not analysis.is_authentic
            
            image_paths.append(analysis.image_path)
            ground_truths.append(ground_truth)
        
        print(f"✅ 수집된 학습 데이터: {len(image_paths)}개")
        print(f"   - 진품: {sum(ground_truths)}개")
        print(f"   - 위작: {len(ground_truths) - sum(ground_truths)}개")
        
        return image_paths, ground_truths


def train_with_rlfd(image_paths=None, ground_truths=None, 
                    pretrain_epochs=100, train_timesteps=10000):
    """
    RLfD 방식으로 RL 에이전트 학습
    
    1. Demonstration 생성 (휴리스틱 파라미터)
    2. Pre-training (Behavioral Cloning)
    3. RL Training (SAC)
    """
    
    print("\n" + "="*60)
    print("🤖 Reinforcement Learning from Demonstration (RLfD)")
    print("="*60 + "\n")
    
    # Step 1: 환경 생성
    print("📦 Step 1: 환경 생성...")
    
    if image_paths and len(image_paths) > 1:
        # 여러 이미지 배치 환경
        env = BatchArtworkEnv(image_paths, ground_truths)
        print(f"   ✅ Batch environment with {len(image_paths)} images")
    elif image_paths and len(image_paths) == 1:
        # 단일 이미지 환경
        env = ArtworkAuthEnv(image_paths[0], ground_truths[0] if ground_truths else None)
        print(f"   ✅ Single image environment")
    else:
        print("   ⚠️  No training data available. Using demo mode.")
        # 데모용 더미 환경
        demo_image = os.path.join(os.path.dirname(__file__), '..', 'data', 'uploads', '.gitkeep')
        if not os.path.exists(demo_image):
            print("   ❌ No images available for training")
            return None
        env = ArtworkAuthEnv(demo_image, None)
    
    # Step 2: 에이전트 생성
    print("\n🧠 Step 2: 에이전트 생성...")
    agent = RLfDAgent(env)
    print("   ✅ RLfD Agent initialized")
    
    # Step 3: Demonstration 생성
    print("\n🎯 Step 3: Demonstration 생성...")
    
    # 3-1: 휴리스틱 파라미터에서
    agent.load_demonstrations_from_heuristics()
    
    # 3-2: 사용자 피드백에서
    if image_paths:
        app = create_app()
        with app.app_context():
            agent.load_demonstrations_from_feedback(db.session)
    
    print(f"   ✅ Total demonstrations: {len(agent.demonstrations)}")
    
    # Step 4: Pre-training
    print(f"\n🎓 Step 4: Pre-training (Behavioral Cloning)...")
    print(f"   Epochs: {pretrain_epochs}")
    
    try:
        agent.pretrain_with_demonstrations(epochs=pretrain_epochs)
    except Exception as e:
        print(f"   ⚠️  Pre-training error: {e}")
        print("   Continuing with demonstration replay buffer only...")
    
    # Step 5: RL Training
    print(f"\n🚀 Step 5: Reinforcement Learning...")
    print(f"   Timesteps: {train_timesteps}")
    print(f"   Algorithm: SAC (Soft Actor-Critic)")
    
    try:
        agent.train(total_timesteps=train_timesteps)
    except ImportError:
        print("\n⚠️  stable-baselines3가 설치되지 않았습니다!")
        print("   설치: pip install stable-baselines3 gymnasium")
        print("   지금은 demonstration만 저장합니다.")
    except Exception as e:
        print(f"   ❌ Training error: {e}")
        return None
    
    # Step 6: 평가
    print("\n📊 Step 6: 모델 평가...")
    try:
        metrics = agent.evaluate(n_eval_episodes=5)
        print(f"   Mean Reward: {metrics.get('mean_reward', 0):.2f}")
        print(f"   Std Reward: {metrics.get('std_reward', 0):.2f}")
    except:
        print("   ⚠️  Evaluation skipped")
    
    # Step 7: 저장
    print("\n💾 Step 7: 모델 저장...")
    agent.save('models/rl_artwork_agent')
    
    print("\n" + "="*60)
    print("✅ RLfD Training Complete!")
    print("="*60 + "\n")
    
    return agent


def main():
    """메인 함수"""
    print("""
╔═══════════════════════════════════════════════════════╗
║  Han.Eye - Reinforcement Learning from Demonstration  ║
║  Inspired by Quantum Control RLfD Paper               ║
╚═══════════════════════════════════════════════════════╝
    """)
    
    # 학습 데이터 수집
    print("📊 데이터 수집 중...")
    result = collect_training_data()
    
    if result:
        image_paths, ground_truths = result
    else:
        image_paths, ground_truths = None, None
    
    # RLfD 학습
    agent = train_with_rlfd(
        image_paths=image_paths,
        ground_truths=ground_truths,
        pretrain_epochs=100,
        train_timesteps=5000  # 빠른 테스트용
    )
    
    if agent:
        print("\n🎉 학습 완료!")
        print("\n사용 방법:")
        print("1. 웹에서 이미지 분석 시 자동으로 RL 모델 사용")
        print("2. 피드백을 더 주면 모델이 계속 개선됩니다")
        print("3. python scripts/train_rl_agent.py 로 재학습")
    else:
        print("\n⚠️  학습 실패")
        print("\n해결 방법:")
        print("1. pip install stable-baselines3 gymnasium 설치")
        print("2. 사용자 피드백 더 수집 (최소 5개)")
        print("3. 이미지 데이터 확인")


if __name__ == '__main__':
    main()

