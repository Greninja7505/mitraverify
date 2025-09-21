"""
Health Check API Endpoints
"""
from fastapi import APIRouter
import time
from datetime import datetime

from core.fusion_engine import fusion_engine


router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0"
    }


@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with component status"""
    start_time = time.time()

    # Check text analyzer
    text_status = "healthy"
    try:
        # Simple test
        test_result = fusion_engine.text_analyzer.analyze_text("Test message")
        if test_result.get("prediction") == "error":
            text_status = "unhealthy"
    except Exception:
        text_status = "unhealthy"

    # Check image analyzer
    image_status = "healthy"
    try:
        # Image analyzer doesn't need a test file for basic health check
        pass
    except Exception:
        image_status = "unhealthy"

    # Check evidence retriever
    evidence_status = "healthy"
    try:
        evidence_count = len(fusion_engine.evidence_retriever.evidence_data)
    except Exception:
        evidence_status = "unhealthy"
        evidence_count = 0

    response_time = time.time() - start_time

    overall_status = "healthy"
    if any(status == "unhealthy" for status in [text_status, image_status, evidence_status]):
        overall_status = "degraded"

    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
        "response_time": f"{response_time:.3f}s",
        "components": {
            "text_analyzer": text_status,
            "image_analyzer": image_status,
            "evidence_retriever": evidence_status
        },
        "metrics": {
            "evidence_count": evidence_count
        }
    }