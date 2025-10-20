#!/usr/bin/env python3
"""
Database Initialization Script

This script initializes the database and creates an admin user.

Usage:
    python init_db.py
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app import create_app, db
from app.models import User, Artwork, Analysis, ReflexionLog

def init_database():
    """Initialize database and create tables"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Initializing database...")
        
        # Drop all tables (comment out in production!)
        # db.drop_all()
        # print("   Dropped existing tables")
        
        # Create all tables
        db.create_all()
        print("   Created database tables")
        
        # Check if admin user exists
        admin = User.query.filter_by(email='admin@han-eye.com').first()
        
        if not admin:
            # Create admin user
            admin = User(
                username='admin',
                email='admin@han-eye.com',
                subscription_type='pro'
            )
            admin.set_password('admin123')  # Change this in production!
            
            db.session.add(admin)
            db.session.commit()
            
            print("   Created admin user")
            print("   Email: admin@han-eye.com")
            print("   Password: admin123")
            print("   ⚠️  Please change the admin password after first login!")
        else:
            print("   Admin user already exists")
        
        # Create upload directories
        upload_dir = os.path.join(os.path.dirname(__file__), 'data', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        print(f"   Created upload directory: {upload_dir}")
        
        # Create logs directory
        logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        print(f"   Created logs directory: {logs_dir}")
        
        print("\n✅ Database initialization completed!")
        print("\n🚀 You can now run the application with: python run.py")

if __name__ == '__main__':
    init_database()

