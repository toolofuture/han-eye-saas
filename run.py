#!/usr/bin/env python3
"""
Han.Eye SaaS Application Entry Point

Usage:
    python run.py
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app import create_app

# Create Flask application
app = create_app()

if __name__ == '__main__':
    # Get configuration from environment
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', os.environ.get('FLASK_PORT', 5000)))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print("""
    ╔═══════════════════════════════════════════╗
    ║         Han.Eye SaaS Application          ║
    ║   AI-Powered Artwork Authentication       ║
    ╚═══════════════════════════════════════════╝
    
    🚀 Server starting...
    📍 URL: http://{}:{}
    🔧 Debug mode: {}
    
    Press Ctrl+C to stop
    """.format(host, port, debug))
    
    # Run application
    app.run(host=host, port=port, debug=debug)

