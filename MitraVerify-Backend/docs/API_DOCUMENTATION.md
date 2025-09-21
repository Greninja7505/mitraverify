# MitraVerify API Documentation

## Overview

MitraVerify provides a RESTful API for real-time misinformation detection in text and images. The API supports both English and Hindi languages with multimodal analysis capabilities.

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
Currently, no authentication is required. In production, consider adding API key authentication.

## Endpoints

### 1. Health Check

**GET** `/health`

Check the health status of the API and its components.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2023-12-01T10:00:00Z",
  "version": "0.1.0",
  "response_time": "0.023s",
  "components": {
    "text_analyzer": "healthy",
    "image_analyzer": "healthy",
    "evidence_retriever": "healthy"
  },
  "metrics": {
    "evidence_count": 12
  }
}
```

### 2. Verify Text

**POST** `/verify/text`

Analyze text content for misinformation.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/verify/text" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "text=COVID-19 vaccines contain microchips"
```

**Parameters:**
- `text` (string, required): Text content to analyze

**Response:**
```json
{
  "overall_verdict": "misinformation",
  "confidence": 0.95,
  "text_analysis": {
    "prediction": "misinformation",
    "confidence": 0.95,
    "probabilities": {
      "reliable": 0.05,
      "misinformation": 0.95
    },
    "language": "en",
    "explanation": "High confidence detection of misinformation patterns in the text.",
    "model_used": "google/muril-base-cased"
  },
  "evidence": [
    {
      "id": "fact_001",
      "claim": "COVID-19 vaccines contain microchips",
      "verdict": "false",
      "explanation": "This is a conspiracy theory...",
      "source": "WHO Fact Check",
      "url": "https://www.who.int/...",
      "language": "en",
      "similarity": 0.98
    }
  ],
  "processing_time": 1.23
}
```

### 3. Verify Image

**POST** `/verify/image`

Analyze image for potential manipulation.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/verify/image" \
     -F "file=@image.jpg"
```

**Parameters:**
- `file` (file, required): Image file to analyze (JPG, PNG, GIF, WebP)

**Response:**
```json
{
  "overall_verdict": "authentic",
  "confidence": 0.78,
  "image_analysis": {
    "verdict": "authentic",
    "confidence": 0.78,
    "is_reused": false,
    "reused_source": null,
    "manipulation_score": 0.12,
    "metadata": {
      "format": "JPEG",
      "size": [1920, 1080],
      "mode": "RGB",
      "has_exif": true
    },
    "explanation": "No obvious signs of manipulation detected",
    "hash": "abcd1234..."
  },
  "processing_time": 0.89
}
```

### 4. Analyze Combined Content

**POST** `/analyze`

Analyze both text and image content together.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
     -F "text=Sample text content" \
     -F "file=@image.jpg"
```

**Parameters:**
- `text` (string, optional): Text content to analyze
- `file` (file, optional): Image file to analyze

**Response:**
```json
{
  "overall_verdict": "misinformation",
  "confidence": 0.87,
  "text_analysis": { ... },
  "image_analysis": { ... },
  "evidence": [ ... ],
  "explanation": "Combined analysis indicates potential misinformation",
  "processing_time": 2.01
}
```

### 5. Get System Statistics

**GET** `/stats`

Get system capabilities and statistics.

**Response:**
```json
{
  "status": "operational",
  "supported_languages": ["en", "hi"],
  "supported_formats": ["text", "image/jpeg", "image/png", "image/gif", "image/webp"],
  "model_info": {
    "text_model": "google/muril-base-cased",
    "image_model": "perceptual_hashing",
    "embedding_model": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
  }
}
```

## Response Codes

- `200`: Success
- `400`: Bad Request (missing or invalid parameters)
- `413`: Payload Too Large (file too big)
- `415`: Unsupported Media Type (invalid file format)
- `422`: Unprocessable Entity (validation error)
- `500`: Internal Server Error

## Error Response Format

```json
{
  "detail": "Error description",
  "error_code": "ERROR_TYPE"
}
```

## Rate Limiting

- No rate limiting implemented in MVP
- Consider implementing in production deployment

## File Upload Limits

- Maximum file size: 10MB
- Supported image formats: JPG, PNG, GIF, WebP
- Text input: Maximum 512 tokens (approximately 400 words)

## Performance

- Average response time: < 3 seconds
- Text-only analysis: ~1-2 seconds
- Image analysis: ~0.5-1.5 seconds
- Combined analysis: ~2-3 seconds

## Examples

### Python Client

```python
import requests

# Text analysis
response = requests.post(
    "http://localhost:8000/api/v1/verify/text",
    data={"text": "Your text here"}
)
result = response.json()

# Image analysis
with open("image.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/verify/image",
        files={"file": f}
    )
result = response.json()
```

### JavaScript Client

```javascript
// Text analysis
const formData = new FormData();
formData.append('text', 'Your text here');

fetch('/api/v1/verify/text', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(result => console.log(result));

// Image analysis
const imageFormData = new FormData();
imageFormData.append('file', imageFile);

fetch('/api/v1/verify/image', {
    method: 'POST',
    body: imageFormData
})
.then(response => response.json())
.then(result => console.log(result));
```

## Versioning

API versioning is handled through URL paths (`/api/v1/`). Future versions will be added as `/api/v2/`, etc.

## Changelog

### v0.1.0 (Current)
- Initial MVP release
- Text analysis in English and Hindi
- Basic image forensics
- Evidence retrieval
- RESTful API with FastAPI
- Interactive web interface