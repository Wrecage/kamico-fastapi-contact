"""
Vercel ASGI Handler
This is the entry point for Vercel serverless deployment.
Wraps the FastAPI app for Vercel's Python runtime.
"""

from main import app

# Export app for Vercel
# Vercel will use this ASGI app to handle requests
__all__ = ['app']
