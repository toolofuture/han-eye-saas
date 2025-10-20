"""
Vercel serverless function entry point for Han.Eye Flask app
"""
from app import create_app

# Create Flask application
app = create_app()

# Vercel serverless function handler
def handler(request):
    """Handle incoming requests"""
    return app(request.environ, lambda *args: None)

