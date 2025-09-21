#!/usr/bin/env python3
"""
Model Download Script for MitraVerify
Downloads pre-trained models and sets up the model cache
"""
import os
import sys
import logging
from pathlib import Path
import sys
import codecs

if sys.stdout.encoding != 'utf-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from config.logging_config import setup_logging

# Setup logging
logger = setup_logging()


def download_text_model():
    """Download MURIL text model"""
    try:
        logger.info("Downloading MURIL text model...")
        from transformers import AutoTokenizer, AutoModelForSequenceClassification

        model_name = settings.text_model_name
        cache_dir = settings.model_cache_dir

        logger.info(f"Downloading tokenizer: {model_name}")
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            cache_dir=cache_dir
        )

        logger.info(f"Downloading model: {model_name}")
        model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            num_labels=2,
            id2label={0: "reliable", 1: "misinformation"},
            label2id={"reliable": 0, "misinformation": 1}
        )

        logger.info("Text model downloaded successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to download text model: {e}")
        return False


def download_embedding_model():
    """Download sentence transformer model"""
    try:
        logger.info("Downloading sentence transformer model...")
        # Import here to avoid linter warnings when package is not installed
        import sentence_transformers
        from sentence_transformers import SentenceTransformer

        model_name = settings.embedding_model_name
        cache_dir = settings.model_cache_dir

        logger.info(f"Downloading embedding model: {model_name}")
        model = SentenceTransformer(model_name, cache_folder=cache_dir)

        # Test the model
        test_sentences = ["This is a test sentence.", "यह एक परीक्षण वाक्य है।"]
        embeddings = model.encode(test_sentences)
        logger.info(f"Embedding model test successful. Output shape: {embeddings.shape}")

        logger.info("Embedding model downloaded successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to download embedding model: {e}")
        return False


def download_image_model():
    """Download CLIP model for image analysis"""
    try:
        logger.info("Downloading CLIP image model...")
        from transformers import CLIPProcessor, CLIPModel

        model_name = settings.image_model_name
        cache_dir = settings.model_cache_dir

        logger.info(f"Downloading CLIP processor: {model_name}")
        processor = CLIPProcessor.from_pretrained(
            model_name,
            cache_dir=cache_dir
        )

        logger.info(f"Downloading CLIP model: {model_name}")
        model = CLIPModel.from_pretrained(
            model_name,
            cache_dir=cache_dir
        )

        logger.info("CLIP model downloaded successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to download CLIP model: {e}")
        return False


def setup_directories():
    """Create necessary directories"""
    try:
        directories = [
            Path(settings.model_cache_dir),
            Path(settings.evidence_db_path).parent,
            Path(settings.image_db_path)
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")

        return True

    except Exception as e:
        logger.error(f"Failed to create directories: {e}")
        return False


def main():
    """Main download function"""
    logger.info("Starting MitraVerify model download...")

    # Setup directories
    if not setup_directories():
        logger.error("Failed to setup directories")
        return False

    success_count = 0
    total_models = 3

    # Download models
    models = [
        ("Text Model (MURIL)", download_text_model),
        ("Embedding Model", download_embedding_model),
        ("Image Model (CLIP)", download_image_model)
    ]

    for model_name, download_func in models:
        logger.info(f"Downloading {model_name}...")
        if download_func():
            success_count += 1
            logger.info(f"✓ {model_name} downloaded successfully")
        else:
            logger.error(f"✗ Failed to download {model_name}")

    # Summary
    logger.info(f"Download complete: {success_count}/{total_models} models downloaded")

    if success_count == total_models:
        logger.info("All models downloaded successfully!")
        logger.info("You can now run the MitraVerify application.")
        return True
    else:
        logger.warning(f"Only {success_count}/{total_models} models downloaded.")
        logger.warning("Some features may not work properly.")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Download interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)