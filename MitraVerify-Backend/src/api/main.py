"""
Main FastAPI Application for MitraVerify
"""
import logging
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import tempfile
import os
import sys
from pathlib import Path

# Add the project root and src directory to the Python path
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_dir)

from config.settings import settings
from config.logging_config import setup_logging
from core.fusion_engine import fusion_engine
from api.endpoints.verification import router as verification_router
from api.endpoints.health import router as health_router


# Setup logging
logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title="MitraVerify API",
    description="AI-powered misinformation detection system for Indian digital ecosystem",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates are not needed for backend-only API
# app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
# templates = Jinja2Templates(directory=str(templates_path)) if templates_path.exists() else None

# Include routers
app.include_router(verification_router, prefix="/api/v1", tags=["verification"])
app.include_router(health_router, prefix="/api/v1", tags=["health"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to MitraVerify API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.post("/api/v1/analyze")
async def analyze_content(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Analyze content for misinformation

    Supports both text and image analysis
    """
    try:
        # Validate input
        if not text and not file:
            raise HTTPException(
                status_code=400,
                detail="Either text or file must be provided"
            )

        image_path = None

        # Handle file upload
        if file:
            # Validate file type
            if not file.content_type.startswith(('image/', 'text/')):
                raise HTTPException(
                    status_code=400,
                    detail="Only image and text files are supported"
                )

            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
                content = await file.read()
                temp_file.write(content)
                image_path = temp_file.name

        # Analyze content
        result = fusion_engine.analyze_content(text=text, image_path=image_path)

        # Clean up temporary file
        if image_path and os.path.exists(image_path):
            os.unlink(image_path)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "0.1.0"}


def main():
    """Main entry point for running the server"""
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main()