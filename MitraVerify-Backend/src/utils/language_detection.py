"""
Language Detection Utilities for MitraVerify
"""
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


def detect_language(text: str) -> str:
    """
    Detect the language of the input text

    Args:
        text: Input text

    Returns:
        Language code ('en' for English, 'hi' for Hindi, 'unknown' for others)
    """
    if not text or not text.strip():
        return "unknown"

    text = text.strip()

    # Simple heuristic-based detection
    # Check for Hindi characters (Devanagari script)
    hindi_chars = re.findall(r'[\u0900-\u097F]', text)
    english_chars = re.findall(r'[a-zA-Z]', text)

    hindi_ratio = len(hindi_chars) / len(text) if text else 0
    english_ratio = len(english_chars) / len(text) if text else 0

    if hindi_ratio > 0.1:
        return "hi"
    elif english_ratio > 0.1:
        return "en"
    else:
        # Check for common Hindi words
        hindi_words = ['hai', 'hai', 'नहीं', 'क्या', 'हो', 'था', 'थी', 'होता', 'होती']
        for word in hindi_words:
            if word in text.lower():
                return "hi"

        return "en"  # Default to English


def is_supported_language(lang: str) -> bool:
    """Check if the language is supported by MitraVerify"""
    return lang in ['en', 'hi']


def get_language_name(lang_code: str) -> str:
    """Get full language name from code"""
    language_names = {
        'en': 'English',
        'hi': 'Hindi',
        'unknown': 'Unknown'
    }
    return language_names.get(lang_code, 'Unknown')