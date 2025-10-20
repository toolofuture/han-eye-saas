from app import db
from datetime import datetime
import json

class ReflexionLog(db.Model):
    __tablename__ = 'reflexion_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id'), nullable=False)
    
    # Re-flexion cycle data
    iteration = db.Column(db.Integer, default=1)
    initial_judgment = db.Column(db.Text)  # Initial AI judgment
    self_evaluation = db.Column(db.Text)  # AI's self-evaluation
    improvement_notes = db.Column(db.Text)  # What to improve
    revised_judgment = db.Column(db.Text)  # Revised judgment after reflection
    
    # Performance metrics
    accuracy_delta = db.Column(db.Float)  # Change in accuracy
    confidence_delta = db.Column(db.Float)  # Change in confidence
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    model_version = db.Column(db.String(50))
    
    # Relationships
    analysis = db.relationship('Analysis', backref='reflexion_logs')
    
    def get_initial_judgment_dict(self):
        if self.initial_judgment:
            return json.loads(self.initial_judgment)
        return {}
    
    def set_initial_judgment_dict(self, data):
        self.initial_judgment = json.dumps(data, ensure_ascii=False)
    
    def get_self_evaluation_dict(self):
        if self.self_evaluation:
            return json.loads(self.self_evaluation)
        return {}
    
    def set_self_evaluation_dict(self, data):
        self.self_evaluation = json.dumps(data, ensure_ascii=False)
    
    def get_improvement_notes_dict(self):
        if self.improvement_notes:
            return json.loads(self.improvement_notes)
        return {}
    
    def set_improvement_notes_dict(self, data):
        self.improvement_notes = json.dumps(data, ensure_ascii=False)
    
    def get_revised_judgment_dict(self):
        if self.revised_judgment:
            return json.loads(self.revised_judgment)
        return {}
    
    def set_revised_judgment_dict(self, data):
        self.revised_judgment = json.dumps(data, ensure_ascii=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'analysis_id': self.analysis_id,
            'iteration': self.iteration,
            'initial_judgment': self.get_initial_judgment_dict(),
            'self_evaluation': self.get_self_evaluation_dict(),
            'improvement_notes': self.get_improvement_notes_dict(),
            'revised_judgment': self.get_revised_judgment_dict(),
            'accuracy_delta': self.accuracy_delta,
            'confidence_delta': self.confidence_delta,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'model_version': self.model_version
        }

