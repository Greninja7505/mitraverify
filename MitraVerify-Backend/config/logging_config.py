"""
Logging configuration for MitraVerify
"""
import logging
import sys
from pathlib import Path

from .settings import settings


def setup_logging():
    """Configure logging for the application"""

    # Create logs directory if it doesn't exist
    log_dir = Path(settings.log_file).parent
    log_dir.mkdir(exist_ok=True)

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(settings.log_file)
        ]
    )

    # Reduce verbosity of some libraries
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("torch").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")

    return logger


# Global logger instance
logger = setup_logging()