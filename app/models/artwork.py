from app import db
from datetime import datetime

class Artwork(db.Model):
    __tablename__ = 'artworks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    artist = db.Column(db.String(100))
    period = db.Column(db.String(50))
    medium = db.Column(db.String(100))
    dimensions = db.Column(db.String(100))
    image_url = db.Column(db.String(500))
    met_object_id = db.Column(db.Integer, unique=True)
    department = db.Column(db.String(100))
    culture = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    analyses = db.relationship('Analysis', backref='reference_artwork', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'artist': self.artist,
            'period': self.period,
            'medium': self.medium,
            'dimensions': self.dimensions,
            'image_url': self.image_url,
            'met_object_id': self.met_object_id,
            'department': self.department,
            'culture': self.culture
        }

