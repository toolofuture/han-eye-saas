from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Analysis
import numpy as np

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/learning-progress')
@login_required
def learning_progress():
    """자가개선 학습 진행 상황 대시보드"""
    return render_template('admin/learning_progress.html')

@admin_bp.route('/api/learning-stats')
@login_required
def api_learning_stats():
    """학습 통계 API"""
    
    # 전체 분석 수
    total_analyses = Analysis.query.count()
    
    # 피드백 받은 분석 수
    feedback_count = Analysis.query.filter(
        Analysis.user_feedback.isnot(None)
    ).count()
    
    # 피드백 비율
    feedback_ratio = feedback_count / total_analyses if total_analyses > 0 else 0
    
    # 정확도 계산
    correct_predictions = Analysis.query.filter_by(user_feedback='correct').count()
    total_feedback = Analysis.query.filter(
        Analysis.user_feedback.in_(['correct', 'incorrect'])
    ).count()
    
    accuracy = correct_predictions / total_feedback if total_feedback > 0 else 0
    
    # 시간대별 정확도 추이
    analyses_with_feedback = Analysis.query.filter(
        Analysis.user_feedback.in_(['correct', 'incorrect'])
    ).order_by(Analysis.created_at.asc()).all()
    
    accuracy_over_time = []
    window_size = 10  # 최근 10개 기준
    
    for i in range(window_size, len(analyses_with_feedback) + 1, 5):
        window = analyses_with_feedback[i-window_size:i]
        correct = sum(1 for a in window if a.user_feedback == 'correct')
        acc = correct / len(window)
        accuracy_over_time.append({
            'index': i,
            'accuracy': acc,
            'timestamp': window[-1].created_at.isoformat()
        })
    
    # 현재 임계값 (최신 분석 기준)
    from app.utils import AnomalyDetector
    detector = AnomalyDetector()
    current_threshold = detector.threshold
    
    # Few-shot 예시 개수
    from app.utils import AIAnalyzer
    analyzer = AIAnalyzer()
    few_shot_count = len(analyzer._get_feedback_examples())
    
    return jsonify({
        'success': True,
        'stats': {
            'total_analyses': total_analyses,
            'feedback_count': feedback_count,
            'feedback_ratio': feedback_ratio,
            'current_accuracy': accuracy,
            'accuracy_over_time': accuracy_over_time,
            'adaptive_threshold': current_threshold,
            'few_shot_examples': few_shot_count,
            'learning_status': '활성화됨' if feedback_count >= 10 else '데이터 수집 중'
        }
    })

@admin_bp.route('/api/performance-improvement')
@login_required
def api_performance_improvement():
    """성능 개선 추이 API"""
    
    # 초기 분석들 (피드백 없음)
    initial_analyses = Analysis.query.filter(
        Analysis.user_feedback == None
    ).limit(50).all()
    
    # 최근 분석들 (피드백 후)
    recent_analyses = Analysis.query.filter(
        Analysis.user_feedback.isnot(None)
    ).order_by(Analysis.created_at.desc()).limit(50).all()
    
    if not initial_analyses or not recent_analyses:
        return jsonify({
            'success': True,
            'improvement': {
                'initial_confidence': 0,
                'recent_confidence': 0,
                'improvement_rate': 0
            }
        })
    
    # 평균 확신도 비교
    initial_confidence = np.mean([a.confidence_score for a in initial_analyses])
    recent_confidence = np.mean([a.confidence_score for a in recent_analyses])
    
    improvement_rate = (recent_confidence - initial_confidence) / initial_confidence if initial_confidence > 0 else 0
    
    return jsonify({
        'success': True,
        'improvement': {
            'initial_confidence': float(initial_confidence),
            'recent_confidence': float(recent_confidence),
            'improvement_rate': float(improvement_rate),
            'message': f"확신도 {improvement_rate*100:+.1f}% 개선!"
        }
    })

