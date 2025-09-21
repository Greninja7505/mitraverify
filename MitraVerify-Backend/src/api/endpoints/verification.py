"""
Verification API Endpoints
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import tempfile
import os
from pathlib import Path

from core.fusion_engine import fusion_engine


router = APIRouter()


@router.post("/verify")
async def verify_content(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Verify content for misinformation

    Args:
        text: Text content to verify
        file: Image file to verify

    Returns:
        Verification result with verdict, confidence, and explanation
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
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if file.content_type not in allowed_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type. Allowed: {', '.join(allowed_types)}"
                )

            # Save uploaded file temporarily
            suffix = Path(file.filename).suffix or '.jpg'
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
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
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/verify/text")
async def verify_text(text: str = Form(...)):
    """
    Verify text content for misinformation

    Args:
        text: Text content to verify

    Returns:
        Text verification result
    """
    try:
        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="Text content is required")

        result = fusion_engine.analyze_content(text=text)
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text analysis failed: {str(e)}")


@router.post("/verify/image")
async def verify_image(file: UploadFile = File(...)):
    """
    Verify image for manipulation

    Args:
        file: Image file to verify

    Returns:
        Image verification result
    """
    try:
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_types)}"
            )

        # Save uploaded file temporarily
        suffix = Path(file.filename).suffix or '.jpg'
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            image_path = temp_file.name

        # Analyze image
        result = fusion_engine.analyze_content(image_path=image_path)

        # Clean up temporary file
        if os.path.exists(image_path):
            os.unlink(image_path)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")


@router.get("/stats")
async def get_stats():
    """Get system statistics"""
    return {
        "status": "operational",
        "supported_languages": ["en", "hi"],
        "supported_formats": ["text", "image/jpeg", "image/png", "image/gif", "image/webp"],
        "model_info": {
            "text_model": "google/muril-base-cased",
            "image_model": "perceptual_hashing",
            "embedding_model": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
        }
    }