from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from app import db
from app.models import Analysis, Artwork, User
from app.utils import AIAnalyzer, AnomalyDetector, ReflexionEngine, MetAPI

api_bp = Blueprint('api', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_bp.route('/analyze', methods=['POST'])
@login_required
def api_analyze():
    """
    API endpoint for artwork analysis
    
    Request (multipart/form-data):
        - artwork_image: image file
        - artist: (optional) artist name
        - period: (optional) time period
        - medium: (optional) medium/material
        - ai_model: (optional) gpt-4, claude, or gemini
    
    Response:
        {
            "success": true,
            "analysis_id": 123,
            "result": {...}
        }
    """
    try:
        # Check file
        if 'artwork_image' not in request.files:
            return jsonify({'success': False, 'error': '이미지 파일이 필요합니다'}), 400
        
        file = request.files['artwork_image']
        
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'success': False, 'error': '유효하지 않은 파일입니다'}), 400
        
        # Save file
        filename = secure_filename(f"{current_user.id}_{datetime.utcnow().timestamp()}_{file.filename}")
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Get context
        context = {}
        if request.form.get('artist'):
            context['artist'] = request.form.get('artist')
        if request.form.get('period'):
            context['period'] = request.form.get('period')
        if request.form.get('medium'):
            context['medium'] = request.form.get('medium')
        
        # Perform analysis
        ai_model = request.form.get('ai_model', 'gpt-4')
        analyzer = AIAnalyzer(model=ai_model)
        ai_result = analyzer.analyze_artwork(filepath, context)
        
        # Anomaly detection
        anomaly_detector = AnomalyDetector()
        anomaly_result = anomaly_detector.analyze(filepath)
        
        # Create analysis record
        analysis = Analysis(
            user_id=current_user.id,
            image_path=filepath,
            image_filename=file.filename,
            is_authentic=ai_result['is_authentic'],
            confidence_score=ai_result['confidence_score'],
            ai_model_used=ai_model,
            anomaly_score=anomaly_result['anomaly_score'],
            processing_time=ai_result.get('processing_time', 0)
        )
        
        analysis.set_analysis_result_dict(ai_result)
        analysis.set_style_analysis_dict(ai_result.get('style_analysis', {}))
        analysis.set_technique_analysis_dict(ai_result.get('technical_analysis', {}))
        
        db.session.add(analysis)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'analysis_id': analysis.id,
            'result': analysis.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/analysis/<int:analysis_id>', methods=['GET'])
@login_required
def api_get_analysis(analysis_id):
    """Get analysis result by ID"""
    analysis = Analysis.query.get(analysis_id)
    
    if not analysis:
        return jsonify({'success': False, 'error': '분석을 찾을 수 없습니다'}), 404
    
    if analysis.user_id != current_user.id:
        return jsonify({'success': False, 'error': '접근 권한이 없습니다'}), 403
    
    return jsonify({
        'success': True,
        'analysis': analysis.to_dict()
    }), 200

@api_bp.route('/analysis/<int:analysis_id>/feedback', methods=['POST'])
@login_required
def api_submit_feedback(analysis_id):
    """
    Submit feedback for an analysis
    
    Request (JSON):
        {
            "feedback": "correct|incorrect|uncertain",
            "expert_verification": true|false
        }
    """
    analysis = Analysis.query.get(analysis_id)
    
    if not analysis:
        return jsonify({'success': False, 'error': '분석을 찾을 수 없습니다'}), 404
    
    if analysis.user_id != current_user.id:
        return jsonify({'success': False, 'error': '접근 권한이 없습니다'}), 403
    
    data = request.get_json()
    
    analysis.user_feedback = data.get('feedback')
    analysis.expert_verification = data.get('expert_verification')
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '피드백이 저장되었습니다'
    }), 200

@api_bp.route('/reflexion/<int:analysis_id>', methods=['POST'])
@login_required
def api_perform_reflexion(analysis_id):
    """Trigger re-flexion on an analysis"""
    analysis = Analysis.query.get(analysis_id)
    
    if not analysis:
        return jsonify({'success': False, 'error': '분석을 찾을 수 없습니다'}), 404
    
    if analysis.user_id != current_user.id:
        return jsonify({'success': False, 'error': '접근 권한이 없습니다'}), 403
    
    try:
        reflexion_engine = ReflexionEngine(model=analysis.ai_model_used)
        reflexion_log = reflexion_engine.perform_reflexion(analysis_id)
        
        return jsonify({
            'success': True,
            'reflexion': reflexion_log.to_dict() if reflexion_log else None
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/user/stats', methods=['GET'])
@login_required
def api_user_stats():
    """Get user statistics"""
    total = current_user.get_analysis_count()
    authentic = Analysis.query.filter_by(user_id=current_user.id, is_authentic=True).count()
    fake = Analysis.query.filter_by(user_id=current_user.id, is_authentic=False).count()
    
    return jsonify({
        'success': True,
        'stats': {
            'total_analyses': total,
            'authentic_count': authentic,
            'fake_count': fake,
            'uncertain_count': total - authentic - fake,
            'subscription_type': current_user.subscription_type
        }
    }), 200

@api_bp.route('/met/search', methods=['GET'])
@login_required
def api_met_search():
    """Search The Met collection"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'success': False, 'error': '검색어를 입력해주세요'}), 400
    
    try:
        met_api = MetAPI()
        object_ids = met_api.search_objects(query)
        
        return jsonify({
            'success': True,
            'object_ids': object_ids[:20],  # Limit to 20
            'total': len(object_ids)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/met/object/<int:object_id>', methods=['GET'])
@login_required
def api_met_object(object_id):
    """Get Met object details"""
    try:
        met_api = MetAPI()
        obj_data = met_api.get_object(object_id)
        
        if not obj_data:
            return jsonify({'success': False, 'error': '객체를 찾을 수 없습니다'}), 404
        
        artwork_info = met_api.extract_artwork_info(obj_data)
        
        return jsonify({
            'success': True,
            'artwork': artwork_info
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

