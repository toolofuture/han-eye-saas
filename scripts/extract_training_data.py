#!/usr/bin/env python3
"""
사용자 피드백을 기반으로 학습 데이터 추출

Usage:
    python scripts/extract_training_data.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app, db
from app.models import Analysis
import json

def extract_training_data():
    """사용자 피드백이 있는 분석 데이터를 추출"""
    app = create_app()
    
    with app.app_context():
        # 피드백이 있는 모든 분석
        analyses = Analysis.query.filter(
            Analysis.user_feedback.isnot(None)
        ).all()
        
        training_data = []
        
        for analysis in analyses:
            # Ground Truth 결정
            if analysis.user_feedback == 'correct':
                # AI 판단이 맞았음 → AI 판단을 레이블로 사용
                ground_truth = analysis.is_authentic
            elif analysis.user_feedback == 'incorrect':
                # AI 판단이 틀렸음 → 반대가 정답
                ground_truth = not analysis.is_authentic
            else:  # uncertain
                continue  # 불확실한 것은 제외
            
            training_data.append({
                'image_path': analysis.image_path,
                'label': int(ground_truth),  # 1: 진품, 0: 위작
                'confidence': analysis.confidence_score,
                'ai_prediction': analysis.is_authentic,
                'user_feedback': analysis.user_feedback,
                'created_at': analysis.created_at.isoformat()
            })
        
        # 통계 출력
        authentic_count = sum(1 for d in training_data if d['label'] == 1)
        fake_count = sum(1 for d in training_data if d['label'] == 0)
        
        print(f"📊 학습 데이터 추출 완료!")
        print(f"총 샘플: {len(training_data)}개")
        print(f"진품: {authentic_count}개 ({authentic_count/len(training_data)*100:.1f}%)")
        print(f"위작: {fake_count}개 ({fake_count/len(training_data)*100:.1f}%)")
        print()
        
        # JSON 파일로 저장
        output_file = 'data/training_data.json'
        os.makedirs('data', exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 저장 완료: {output_file}")
        
        # 샘플 출력
        print("\n📝 샘플 데이터:")
        for i, data in enumerate(training_data[:3]):
            print(f"\n{i+1}. {data['image_path']}")
            print(f"   레이블: {'진품' if data['label'] == 1 else '위작'}")
            print(f"   AI 판단: {'진품' if data['ai_prediction'] else '위작'}")
            print(f"   피드백: {data['user_feedback']}")
        
        return training_data

if __name__ == '__main__':
    extract_training_data()

