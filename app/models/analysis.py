from app import db
from datetime import datetime
import json

class Analysis(db.Model):
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    artwork_id = db.Column(db.Integer, db.ForeignKey('artworks.id'), nullable=True)
    
    # Image information
    image_path = db.Column(db.String(500), nullable=False)
    image_filename = db.Column(db.String(200))
    
    # Analysis results
    is_authentic = db.Column(db.Boolean)  # True: authentic, False: fake, None: uncertain
    confidence_score = db.Column(db.Float)  # 0.0 to 1.0
    ai_model_used = db.Column(db.String(50))  # gpt-4, claude, gemini
    
    # Detailed analysis
    analysis_result = db.Column(db.Text)  # JSON string with detailed results
    anomaly_score = db.Column(db.Float)  # Anomaly detection score
    style_analysis = db.Column(db.Text)  # JSON string
    technique_analysis = db.Column(db.Text)  # JSON string
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processing_time = db.Column(db.Float)  # seconds
    
    # Feedback for re-flexion
    user_feedback = db.Column(db.String(20))  # correct, incorrect, uncertain
    expert_verification = db.Column(db.Boolean)
    
    def get_analysis_result_dict(self):
        if self.analysis_result:
            return json.loads(self.analysis_result)
        return {}
    
    def set_analysis_result_dict(self, data):
        self.analysis_result = json.dumps(data, ensure_ascii=False)
    
    def get_style_analysis_dict(self):
        if self.style_analysis:
            return json.loads(self.style_analysis)
        return {}
    
    def set_style_analysis_dict(self, data):
        self.style_analysis = json.dumps(data, ensure_ascii=False)
    
    def get_technique_analysis_dict(self):
        if self.technique_analysis:
            return json.loads(self.technique_analysis)
        return {}
    
    def set_technique_analysis_dict(self, data):
        self.technique_analysis = json.dumps(data, ensure_ascii=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'artwork_id': self.artwork_id,
            'image_filename': self.image_filename,
            'is_authentic': self.is_authentic,
            'confidence_score': self.confidence_score,
            'ai_model_used': self.ai_model_used,
            'analysis_result': self.get_analysis_result_dict(),
            'anomaly_score': self.anomaly_score,
            'style_analysis': self.get_style_analysis_dict(),
            'technique_analysis': self.get_technique_analysis_dict(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processing_time': self.processing_time,
            'user_feedback': self.user_feedback,
            'expert_verification': self.expert_verification
        }

