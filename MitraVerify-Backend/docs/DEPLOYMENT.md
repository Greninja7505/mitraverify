# Deployment Guide

This guide covers deploying MitraVerify in various environments.

## Local Development

### Prerequisites
- Python 3.8+
- 8GB+ RAM
- 10GB+ disk space

### Quick Start
```bash
# 1. Clone and setup
git clone <repository>
cd mitraverify
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download models
python scripts/download_models.py

# 4. Create sample data
python scripts/create_sample_data.py

# 5. Start server
python src/api/main.py
```

Visit `http://localhost:8000` to access the web interface.

## Docker Deployment

### Build Docker Image
```bash
# Build image
docker build -t mitraverify:latest .

# Or use docker-compose
docker-compose build
```

### Run with Docker
```bash
# Run container
docker run -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  mitraverify:latest

# Or use docker-compose
docker-compose up -d
```

### Environment Variables
```bash
# In docker-compose.yml or as -e flags
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
LOG_LEVEL=INFO
```

## Production Deployment

### 1. Server Requirements
- **CPU**: 4+ cores recommended
- **RAM**: 16GB+ recommended
- **Storage**: 20GB+ for models and data
- **OS**: Linux (Ubuntu 20.04+ recommended)

### 2. Web Server Setup (Nginx)
```nginx
# /etc/nginx/sites-available/mitraverify
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/mitraverify/frontend/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 3. SSL Certificate (Let's Encrypt)
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com
```

### 4. Process Manager (systemd)
```ini
# /etc/systemd/system/mitraverify.service
[Unit]
Description=MitraVerify API Server
After=network.target

[Service]
User=mitraverify
Group=mitraverify
WorkingDirectory=/path/to/mitraverify
Environment="PATH=/path/to/mitraverify/venv/bin"
ExecStart=/path/to/mitraverify/venv/bin/uvicorn src.api.main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable mitraverify
sudo systemctl start mitraverify
sudo systemctl status mitraverify
```

### 5. Monitoring
```bash
# Check logs
sudo journalctl -u mitraverify -f

# Monitor resources
htop
df -h
free -h
```

## Cloud Deployment

### AWS EC2
```bash
# Launch EC2 instance (t3.large or better)
# Ubuntu 20.04 LTS, security group with ports 22, 80, 443

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Clone repository
git clone <repository>
cd mitraverify

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download models
python scripts/download_models.py

# Configure environment
cp .env.example .env
nano .env  # Edit configuration

# Start with screen or tmux
screen -S mitraverify
python src/api/main.py

# Detach: Ctrl+A, D
```

### Google Cloud Run
```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/mitraverify', '.']

  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/mitraverify']

  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'mitraverify'
      - '--image'
      - 'gcr.io/$PROJECT_ID/mitraverify'
      - '--platform'
      - 'managed'
      - '--port'
      - '8000'
      - '--memory'
      - '4Gi'
      - '--cpu'
      - '2'
      - '--max-instances'
      - '10'
```

### Heroku
```yaml
# Procfile
web: uvicorn src.api.main:app --host 0.0.0.0 --port $PORT

# runtime.txt
python-3.11.4

# requirements.txt (add gunicorn)
gunicorn==20.1.0
```

```bash
# Deploy
heroku create mitraverify-app
git push heroku main
```

## Performance Optimization

### Model Optimization
```python
# Use model quantization for smaller footprint
from transformers import BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_enable_fp32_cpu_offload=True
)

model = AutoModelForSequenceClassification.from_pretrained(
    model_name,
    quantization_config=quantization_config
)
```

### Caching
```python
# Implement Redis for result caching
import redis

cache = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_result(key):
    return cache.get(key)

def set_cached_result(key, value, ttl=3600):
    cache.setex(key, ttl, json.dumps(value))
```

### Load Balancing
```nginx
# Nginx load balancer
upstream mitraverify_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    location / {
        proxy_pass http://mitraverify_backend;
        proxy_set_header Host $host;
    }
}
```

## Security Considerations

### API Security
```python
# Add API key authentication
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

@app.middleware("http")
async def authenticate(request: Request, call_next):
    api_key = request.headers.get("X-API-Key")
    if api_key != settings.api_key:
        return JSONResponse(
            status_code=HTTP_403_FORBIDDEN,
            content={"detail": "Invalid API key"}
        )
    response = await call_next(request)
    return response
```

### File Upload Security
```python
# Validate file uploads
from fastapi import UploadFile, HTTPException

async def validate_image_file(file: UploadFile):
    # Check file size
    file_size = 0
    content = await file.read()
    file_size = len(content)

    if file_size > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(413, "File too large")

    # Check MIME type
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(415, "Unsupported file type")

    # Reset file pointer
    await file.seek(0)
```

### Rate Limiting
```python
# Implement rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/v1/analyze")
@limiter.limit("10/minute")
async def analyze_content(request: Request, ...):
    # Your endpoint logic
    pass
```

## Backup and Recovery

### Database Backup
```bash
# Backup evidence database
cp data/evidence/fact_check_corpus.json data/evidence/backup_$(date +%Y%m%d_%H%M%S).json

# Backup models (if fine-tuned)
tar -czf models_backup_$(date +%Y%m%d).tar.gz data/models/
```

### Automated Backups
```bash
# Add to crontab
0 2 * * * /path/to/backup_script.sh
```

## Monitoring and Logging

### Application Monitoring
```python
# Add Prometheus metrics
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('request_count', 'Total requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('request_latency', 'Request latency', ['method', 'endpoint'])

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    REQUEST_COUNT.labels(request.method, request.url.path).inc()

    with REQUEST_LATENCY.labels(request.method, request.url.path).time():
        response = await call_next(request)

    return response

@app.get("/metrics")
def metrics():
    return generate_latest()
```

### Log Aggregation
```python
# Configure structured logging
import structlog

shared_processors = [
    structlog.stdlib.filter_by_level,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    structlog.processors.UnicodeDecoder(),
]

structlog.configure(
    processors=shared_processors + [
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

## Troubleshooting

### Common Issues

1. **Model loading fails**
   ```bash
   # Check disk space
   df -h

   # Clear cache and retry
   rm -rf ~/.cache/huggingface/
   python scripts/download_models.py
   ```

2. **Memory errors**
   ```bash
   # Increase swap space
   sudo fallocate -l 8G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

3. **Port already in use**
   ```bash
   # Find process using port
   sudo lsof -i :8000

   # Kill process
   sudo kill -9 <PID>
   ```

4. **Slow response times**
   - Check CPU/memory usage
   - Enable model caching
   - Consider model quantization
   - Use faster instance types

### Debug Mode
```bash
# Run with debug logging
DEBUG=True LOG_LEVEL=DEBUG python src/api/main.py
```

## Support

For deployment issues:
- Check application logs: `tail -f logs/mitraverify.log`
- Monitor system resources: `htop`, `free -h`
- Test API endpoints with curl
- Check network connectivity to model repositories