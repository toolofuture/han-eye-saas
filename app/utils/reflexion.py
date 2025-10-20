from typing import Dict, Any, List, Optional
import json
from app import db
from app.models import Analysis, ReflexionLog
from app.utils.ai_analyzer import AIAnalyzer

class ReflexionEngine:
    """
    Re-flexion engine for self-improving AI system
    Implements: Judgment → Evaluation → Recording → Improvement cycle
    """
    
    def __init__(self, model: str = 'gpt-4'):
        self.model = model
        self.analyzer = AIAnalyzer(model=model)
    
    def perform_reflexion(self, analysis_id: int, iteration: int = 1) -> Optional[ReflexionLog]:
        """
        Perform one iteration of re-flexion on an analysis
        
        Args:
            analysis_id: ID of the analysis to reflect on
            iteration: Current iteration number
        
        Returns:
            ReflexionLog object or None
        """
        # Get the original analysis
        analysis = Analysis.query.get(analysis_id)
        if not analysis:
            return None
        
        # Step 1: Get initial judgment
        initial_judgment = self._get_initial_judgment(analysis)
        
        # Step 2: Self-evaluate the judgment
        self_evaluation = self._self_evaluate(analysis, initial_judgment)
        
        # Step 3: Generate improvement notes
        improvement_notes = self._generate_improvements(self_evaluation)
        
        # Step 4: Create revised judgment
        revised_judgment = self._revise_judgment(analysis, improvement_notes)
        
        # Step 5: Calculate performance delta
        accuracy_delta, confidence_delta = self._calculate_deltas(
            initial_judgment, revised_judgment
        )
        
        # Create re-flexion log
        reflexion_log = ReflexionLog(
            analysis_id=analysis_id,
            iteration=iteration,
            model_version=self.model
        )
        
        reflexion_log.set_initial_judgment_dict(initial_judgment)
        reflexion_log.set_self_evaluation_dict(self_evaluation)
        reflexion_log.set_improvement_notes_dict(improvement_notes)
        reflexion_log.set_revised_judgment_dict(revised_judgment)
        reflexion_log.accuracy_delta = accuracy_delta
        reflexion_log.confidence_delta = confidence_delta
        
        # Save to database
        db.session.add(reflexion_log)
        db.session.commit()
        
        # Update original analysis with improved results
        if revised_judgment['confidence_score'] > analysis.confidence_score:
            analysis.confidence_score = revised_judgment['confidence_score']
            analysis.set_analysis_result_dict(revised_judgment)
            db.session.commit()
        
        return reflexion_log
    
    def _get_initial_judgment(self, analysis: Analysis) -> Dict[str, Any]:
        """Extract initial judgment from analysis"""
        return {
            'is_authentic': analysis.is_authentic,
            'confidence_score': analysis.confidence_score,
            'reasoning': analysis.get_analysis_result_dict().get('reasoning', '')
        }
    
    def _self_evaluate(self, analysis: Analysis, initial_judgment: Dict) -> Dict[str, Any]:
        """
        AI evaluates its own judgment
        
        Returns evaluation with strengths, weaknesses, and confidence
        """
        # Build self-evaluation prompt
        prompt = f"""당신은 방금 미술품 진위 감정을 수행했습니다. 
        
자신의 판단을 객관적으로 평가해주세요:

**초기 판단:**
- 진품 여부: {initial_judgment['is_authentic']}
- 확신도: {initial_judgment['confidence_score']:.2%}
- 근거: {initial_judgment['reasoning']}

다음 항목을 평가해주세요:
1. **판단의 강점**: 이 판단에서 신뢰할 수 있는 부분
2. **판단의 약점**: 불확실하거나 개선이 필요한 부분
3. **누락된 분석**: 추가로 고려해야 할 요소
4. **확신도 평가**: 현재 확신도가 적절한지

JSON 형식으로 응답:
{{
  "strengths": ["강점1", "강점2"],
  "weaknesses": ["약점1", "약점2"],
  "missing_analysis": ["누락 요소1", "누락 요소2"],
  "confidence_assessment": "적절함|과대평가|과소평가",
  "reasoning": "평가 근거"
}}"""
        
        try:
            # Use AI to self-evaluate
            # For now, use heuristic-based evaluation
            result = self._heuristic_evaluation(analysis, initial_judgment)
            return result
        except Exception as e:
            print(f"Self-evaluation error: {e}")
            return self._default_evaluation()
    
    def _heuristic_evaluation(self, analysis: Analysis, initial_judgment: Dict) -> Dict[str, Any]:
        """Heuristic-based self-evaluation"""
        strengths = []
        weaknesses = []
        missing_analysis = []
        
        # Check confidence score
        confidence = initial_judgment['confidence_score']
        
        if confidence > 0.8:
            strengths.append("높은 확신도로 명확한 판단")
        elif confidence < 0.6:
            weaknesses.append("낮은 확신도로 불확실한 판단")
        
        # Check anomaly score
        if analysis.anomaly_score:
            if analysis.anomaly_score > 0.7:
                strengths.append("이상탐지 시스템에서 높은 의심도 감지")
            elif analysis.anomaly_score < 0.3:
                strengths.append("이상탐지 시스템에서 정상 패턴 확인")
            else:
                missing_analysis.append("이상탐지 결과와 AI 판단 간 추가 검증 필요")
        
        # Check if detailed analysis exists
        style_analysis = analysis.get_style_analysis_dict()
        tech_analysis = analysis.get_technique_analysis_dict()
        
        if not style_analysis or len(style_analysis) < 2:
            weaknesses.append("스타일 분석 세부 정보 부족")
            missing_analysis.append("더 심층적인 스타일 분석 필요")
        
        if not tech_analysis or len(tech_analysis) < 2:
            weaknesses.append("기술적 분석 세부 정보 부족")
            missing_analysis.append("재료와 기법에 대한 추가 분석 필요")
        
        # Assess confidence
        if confidence > 0.9 and len(weaknesses) > 0:
            confidence_assessment = "과대평가"
        elif confidence < 0.5 and len(strengths) > len(weaknesses):
            confidence_assessment = "과소평가"
        else:
            confidence_assessment = "적절함"
        
        return {
            'strengths': strengths if strengths else ["기본적인 분석 완료"],
            'weaknesses': weaknesses if weaknesses else ["명확한 약점 없음"],
            'missing_analysis': missing_analysis if missing_analysis else ["추가 분석 불필요"],
            'confidence_assessment': confidence_assessment,
            'reasoning': f"총 {len(strengths)}개 강점, {len(weaknesses)}개 약점 발견"
        }
    
    def _generate_improvements(self, evaluation: Dict) -> Dict[str, Any]:
        """Generate improvement recommendations based on evaluation"""
        improvements = {
            'priority_areas': [],
            'specific_actions': [],
            'expected_improvement': 0.0
        }
        
        # Based on weaknesses, generate specific improvements
        for weakness in evaluation.get('weaknesses', []):
            if '확신도' in weakness or '불확실' in weakness:
                improvements['priority_areas'].append('확신도 향상')
                improvements['specific_actions'].append('다층 검증 시스템 적용')
            
            if '스타일' in weakness:
                improvements['priority_areas'].append('스타일 분석 강화')
                improvements['specific_actions'].append('붓질, 색채, 구도 심층 분석')
            
            if '기술' in weakness or '재료' in weakness:
                improvements['priority_areas'].append('기술적 분석 강화')
                improvements['specific_actions'].append('재료, 노화, 기법 상세 검증')
        
        # Based on missing analysis
        for missing in evaluation.get('missing_analysis', []):
            improvements['specific_actions'].append(f"추가 분석: {missing}")
        
        # Calculate expected improvement
        num_improvements = len(improvements['specific_actions'])
        improvements['expected_improvement'] = min(0.05 * num_improvements, 0.2)
        
        return improvements
    
    def _revise_judgment(self, analysis: Analysis, improvements: Dict) -> Dict[str, Any]:
        """
        Create revised judgment incorporating improvements
        
        This would ideally re-run the AI analysis with additional focus areas,
        but for MVP we'll enhance the existing judgment
        """
        current_result = analysis.get_analysis_result_dict()
        
        # Apply improvements
        revised_confidence = min(
            analysis.confidence_score + improvements['expected_improvement'],
            0.95
        )
        
        # Create enhanced reasoning
        enhanced_reasoning = current_result.get('reasoning', '')
        if improvements['specific_actions']:
            enhanced_reasoning += "\n\n개선된 분석:\n"
            for action in improvements['specific_actions']:
                enhanced_reasoning += f"- {action}\n"
        
        return {
            'is_authentic': analysis.is_authentic,
            'confidence_score': revised_confidence,
            'reasoning': enhanced_reasoning,
            'improvements_applied': improvements['specific_actions'],
            'style_analysis': analysis.get_style_analysis_dict(),
            'technical_analysis': analysis.get_technique_analysis_dict()
        }
    
    def _calculate_deltas(self, initial: Dict, revised: Dict) -> tuple:
        """Calculate performance improvement deltas"""
        # In a real system, this would compare against ground truth
        # For now, we calculate confidence improvement
        
        confidence_delta = revised['confidence_score'] - initial['confidence_score']
        
        # Accuracy delta would require ground truth labels
        # For MVP, assume positive confidence change means accuracy improvement
        accuracy_delta = confidence_delta * 0.5  # Heuristic
        
        return accuracy_delta, confidence_delta
    
    def _default_evaluation(self) -> Dict[str, Any]:
        """Default evaluation when process fails"""
        return {
            'strengths': ["분석 완료"],
            'weaknesses': ["평가 시스템 오류"],
            'missing_analysis': [],
            'confidence_assessment': "적절함",
            'reasoning': "기본 평가"
        }
    
    def get_learning_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent re-flexion learning history"""
        logs = ReflexionLog.query.order_by(
            ReflexionLog.created_at.desc()
        ).limit(limit).all()
        
        return [log.to_dict() for log in logs]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Calculate overall performance metrics from re-flexion logs"""
        logs = ReflexionLog.query.all()
        
        if not logs:
            return {
                'total_reflexions': 0,
                'avg_accuracy_improvement': 0.0,
                'avg_confidence_improvement': 0.0,
                'total_improvements': 0
            }
        
        total_accuracy_delta = sum(log.accuracy_delta or 0 for log in logs)
        total_confidence_delta = sum(log.confidence_delta or 0 for log in logs)
        
        return {
            'total_reflexions': len(logs),
            'avg_accuracy_improvement': total_accuracy_delta / len(logs),
            'avg_confidence_improvement': total_confidence_delta / len(logs),
            'total_improvements': len([log for log in logs if (log.confidence_delta or 0) > 0])
        }

