from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from app import db
from app.models import Analysis, Artwork, ReflexionLog
from app.utils import AIAnalyzer, AnomalyDetector, ReflexionEngine

main_bp = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main_bp.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    # Get user's recent analyses
    recent_analyses = Analysis.query.filter_by(user_id=current_user.id)\
        .order_by(Analysis.created_at.desc())\
        .limit(10)\
        .all()
    
    # Calculate statistics
    total_analyses = current_user.get_analysis_count()
    authentic_count = Analysis.query.filter_by(
        user_id=current_user.id, 
        is_authentic=True
    ).count()
    fake_count = Analysis.query.filter_by(
        user_id=current_user.id, 
        is_authentic=False
    ).count()
    
    stats = {
        'total': total_analyses,
        'authentic': authentic_count,
        'fake': fake_count,
        'uncertain': total_analyses - authentic_count - fake_count
    }
    
    return render_template('dashboard.html', 
                         analyses=recent_analyses, 
                         stats=stats)

@main_bp.route('/analyze', methods=['GET', 'POST'])
@login_required
def analyze():
    """Artwork analysis page"""
    if request.method == 'POST':
        # Check if file is uploaded
        if 'artwork_image' not in request.files:
            flash('이미지 파일을 선택해주세요.', 'danger')
            return redirect(request.url)
        
        file = request.files['artwork_image']
        
        if file.filename == '':
            flash('파일이 선택되지 않았습니다.', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Save file
            filename = secure_filename(f"{current_user.id}_{datetime.utcnow().timestamp()}_{file.filename}")
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Get optional context
            context = {}
            if request.form.get('artist'):
                context['artist'] = request.form.get('artist')
            if request.form.get('period'):
                context['period'] = request.form.get('period')
            if request.form.get('medium'):
                context['medium'] = request.form.get('medium')
            
            # Perform analysis
            try:
                # AI Analysis
                ai_model = request.form.get('ai_model', 'gpt-4')
                analyzer = AIAnalyzer(model=ai_model)
                ai_result = analyzer.analyze_artwork(filepath, context)
                
                # Anomaly Detection
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
                
                # Perform Re-flexion (if enabled)
                if request.form.get('enable_reflexion') == 'on':
                    reflexion_engine = ReflexionEngine(model=ai_model)
                    reflexion_engine.perform_reflexion(analysis.id)
                
                flash('분석이 완료되었습니다.', 'success')
                return redirect(url_for('main.analysis_result', analysis_id=analysis.id))
                
            except Exception as e:
                flash(f'분석 중 오류가 발생했습니다: {str(e)}', 'danger')
                return redirect(request.url)
        else:
            flash('허용되지 않는 파일 형식입니다. (png, jpg, jpeg, gif, webp만 가능)', 'danger')
            return redirect(request.url)
    
    return render_template('analyze.html')

@main_bp.route('/analysis/<int:analysis_id>')
@login_required
def analysis_result(analysis_id):
    """View analysis result"""
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Check if user owns this analysis
    if analysis.user_id != current_user.id:
        flash('접근 권한이 없습니다.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Get re-flexion logs if any
    reflexion_logs = ReflexionLog.query.filter_by(analysis_id=analysis_id)\
        .order_by(ReflexionLog.iteration.desc())\
        .all()
    
    return render_template('analysis_result.html', 
                         analysis=analysis, 
                         reflexion_logs=reflexion_logs)

@main_bp.route('/history')
@login_required
def history():
    """Analysis history page"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    pagination = Analysis.query.filter_by(user_id=current_user.id)\
        .order_by(Analysis.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('history.html', pagination=pagination)

@main_bp.route('/reflexion-dashboard')
@login_required
def reflexion_dashboard():
    """Re-flexion learning dashboard"""
    reflexion_engine = ReflexionEngine()
    
    # Get performance metrics
    metrics = reflexion_engine.get_performance_metrics()
    
    # Get recent learning history
    learning_history = reflexion_engine.get_learning_history(limit=20)
    
    return render_template('reflexion_dashboard.html', 
                         metrics=metrics, 
                         learning_history=learning_history)

@main_bp.route('/about')
def about():
    """About Han.Eye page"""
    return render_template('about.html')

