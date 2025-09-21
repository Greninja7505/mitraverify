# MitraVerify

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**AI-powered misinformation detection system for Indian digital ecosystem**

MitraVerify is a real-time misinformation detection system that analyzes text claims and images to provide explainable verdicts with confidence scores. Built for the Indian context, it supports both English and Hindi languages with multimodal analysis capabilities.

## 🚀 Features

- **Multilingual Text Analysis**: Detect misinformation in English and Hindi using MURIL (Multilingual Representations for Indian Languages)
- **Image Forensics**: Basic image manipulation and reuse detection using perceptual hashing
- **Explainable AI**: Clear reasoning for each prediction with confidence scores
- **RESTful API**: FastAPI-based endpoints for easy integration
- **Interactive Web Demo**: User-friendly interface for testing the system
- **Evidence Retrieval**: Fact-checking against curated sources using semantic search
- **Real-time Processing**: Fast analysis with sub-3-second response times

## 🏗️ Architecture

```
mitraverify/
├── src/
│   ├── core/           # Core analysis modules
│   │   ├── text_analyzer.py      # MURIL-based text classification
│   │   ├── image_analyzer.py     # Image forensics
│   │   ├── evidence_retrieval.py # Fact-checking
│   │   └── fusion_engine.py      # Multimodal fusion
│   ├── api/            # FastAPI application
│   │   ├── main.py              # Main API app
│   │   └── endpoints/           # API endpoints
│   └── utils/          # Utility functions
├── frontend/           # Web interface
├── data/              # Models and datasets
└── scripts/           # Setup and utility scripts
```

## 📋 Requirements

- Python 3.8+
- 8GB+ RAM (for model loading)
- 10GB+ disk space (for models)

## 🛠️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/mitraverify/mitraverify.git
cd mitraverify
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Download models
```bash
python scripts/download_models.py
```

This will download:
- **MURIL-base-cased**: Multilingual text classification for Indian languages
- **CLIP-ViT-base-patch32**: Image analysis and semantic understanding
- **Sentence-Transformers**: Evidence retrieval and semantic search

### 5. Create sample data
```bash
python scripts/create_sample_data.py
```

## 🚀 Usage

### Start the API Server

```bash
# Development mode
python src/api/main.py

# Or using uvicorn directly
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### Web Interface

Open `http://localhost:8000` in your browser to access the interactive demo.

### API Endpoints

#### Analyze Content
```bash
# Text analysis
curl -X POST "http://localhost:8000/api/v1/verify/text" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "text=COVID-19 vaccines contain microchips"

# Image analysis
curl -X POST "http://localhost:8000/api/v1/verify/image" \
     -F "file=@image.jpg"

# Combined analysis
curl -X POST "http://localhost:8000/api/v1/analyze" \
     -F "text=Sample text" \
     -F "file=@image.jpg"
```

#### Response Format
```json
{
  "overall_verdict": "misinformation",
  "confidence": 0.89,
  "text_analysis": {
    "prediction": "misinformation",
    "confidence": 0.91,
    "language": "en",
    "explanation": "High confidence detection of misinformation patterns"
  },
  "image_analysis": {
    "verdict": "authentic",
    "confidence": 0.76,
    "explanation": "No obvious signs of manipulation detected"
  },
  "evidence": [
    {
      "claim": "COVID-19 vaccines contain microchips",
      "verdict": "false",
      "source": "WHO Fact Check",
      "similarity": 0.95
    }
  ],
  "processing_time": 1.23
}
```

## 🧪 Testing

### Run Unit Tests
```bash
python -m pytest tests/
```

### Test with Sample Data
```bash
# Test text analysis
python -c "
from src.core.text_analyzer import text_analyzer
result = text_analyzer.analyze_text('COVID-19 vaccines contain microchips')
print(result)
"

# Test image analysis
python -c "
from src.core.image_analyzer import image_analyzer
result = image_analyzer.analyze_image('path/to/image.jpg')
print(result)
"
```

## 📊 Performance Metrics

- **Accuracy**: >75% on test dataset
- **Response Time**: <3 seconds per analysis
- **Supported Languages**: English, Hindi
- **Supported Formats**: Text, Images (JPG, PNG, GIF, WebP)

## 🔧 Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Model Configuration
TEXT_MODEL_NAME=google/muril-base-cased
IMAGE_MODEL_NAME=openai/clip-vit-base-patch32
EMBEDDING_MODEL_NAME=sentence-transformers/paraphrase-multilingual-mpnet-base-v2

# Data Paths
MODEL_CACHE_DIR=./data/models/pretrained
EVIDENCE_DB_PATH=./data/evidence/fact_check_corpus.json

# Logging
LOG_LEVEL=INFO
DEBUG=True
```

## 🐳 Docker Deployment

### Build and Run
```bash
# Build image
docker build -t mitraverify .

# Run container
docker run -p 8000:8000 -v $(pwd)/data:/app/data mitraverify
```

### Docker Compose
```bash
docker-compose up --build
```

## 📈 Model Details

### Text Analysis Model
- **Model**: google/muril-base-cased
- **Architecture**: Transformer-based multilingual model
- **Languages**: 17 Indian languages including English and Hindi
- **Task**: Binary classification (reliable vs misinformation)

### Image Analysis Model
- **Model**: openai/clip-vit-base-patch32
- **Architecture**: Vision Transformer with contrastive learning
- **Capabilities**: Image understanding and semantic analysis
- **Integration**: Used for advanced image forensics (future enhancement)

### Evidence Retrieval Model
- **Model**: sentence-transformers/paraphrase-multilingual-mpnet-base-v2
- **Architecture**: Transformer-based sentence embeddings
- **Task**: Semantic similarity and evidence retrieval
- **Languages**: Multilingual support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google AI** for MURIL model
- **OpenAI** for CLIP model
- **Hugging Face** for transformers library
- **Sentence Transformers** for multilingual embeddings
- **FastAPI** for the web framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/mitraverify/mitraverify/issues)
- **Documentation**: [API Docs](/docs)
- **Discussions**: [GitHub Discussions](https://github.com/mitraverify/mitraverify/discussions)

## 🎯 Roadmap

- [ ] Advanced image deepfake detection
- [ ] Real-time social media monitoring
- [ ] Multi-language expansion (Tamil, Telugu, etc.)
- [ ] Integration with fact-checking APIs
- [ ] Mobile application
- [ ] Batch processing capabilities
- [ ] Model fine-tuning on Indian datasets

---

**Built with ❤️ for India's digital ecosystem**