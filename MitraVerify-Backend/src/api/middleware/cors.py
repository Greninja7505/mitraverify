"""
CORS Middleware Configuration
"""
from fastapi.middleware.cors import CORSMiddleware


def create_cors_middleware():
    """Create CORS middleware with appropriate settings"""
    return CORSMiddleware(
        allow_origins=["*"],  # In production, specify allowed origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )