"""
Image Analysis Module for MitraVerify
Basic image forensics and reuse detection
"""
import logging
from typing import Dict, List, Optional, Any
import os
from pathlib import Path
import imagehash
from PIL import Image
import numpy as np

from config.settings import settings


logger = logging.getLogger(__name__)


class ImageAnalyzer:
    """Image analyzer for basic forensics and reuse detection"""

    def __init__(self):
        """Initialize the image analyzer"""
        self.image_db_path = Path(settings.image_db_path)
        self.image_db_path.mkdir(exist_ok=True)
        self.known_hashes = self._load_known_hashes()

    def _load_known_hashes(self) -> Dict[str, str]:
        """Load known image hashes from database"""
        hash_file = self.image_db_path / "image_hashes.txt"
        if not hash_file.exists():
            return {}

        hashes = {}
        try:
            with open(hash_file, 'r') as f:
                for line in f:
                    if ':' in line:
                        hash_val, filename = line.strip().split(':', 1)
                        hashes[hash_val] = filename
        except Exception as e:
            logger.error(f"Error loading image hashes: {e}")

        return hashes

    def _save_hash(self, hash_val: str, filename: str):
        """Save image hash to database"""
        hash_file = self.image_db_path / "image_hashes.txt"
        try:
            with open(hash_file, 'a') as f:
                f.write(f"{hash_val}:{filename}\n")
            self.known_hashes[hash_val] = filename
        except Exception as e:
            logger.error(f"Error saving image hash: {e}")

    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze image for potential manipulation and reuse

        Args:
            image_path: Path to the image file

        Returns:
            Dict containing analysis results
        """
        try:
            # Open and validate image
            image = Image.open(image_path)

            # Calculate perceptual hash
            phash = imagehash.phash(image)
            hash_str = str(phash)

            # Check for reuse
            is_reused = hash_str in self.known_hashes
            reused_source = self.known_hashes.get(hash_str) if is_reused else None

            # Basic metadata analysis
            metadata = self._extract_metadata(image_path)

            # Simple manipulation detection (basic checks)
            manipulation_score = self._detect_basic_manipulation(image)

            # Determine verdict
            if is_reused:
                verdict = "potentially_manipulated"
                confidence = 0.8
                explanation = f"Image appears to be reused from: {reused_source}"
            elif manipulation_score > 0.7:
                verdict = "potentially_manipulated"
                confidence = manipulation_score
                explanation = "Basic analysis suggests possible image manipulation"
            else:
                verdict = "authentic"
                confidence = 0.6
                explanation = "No obvious signs of manipulation detected"

            result = {
                "verdict": verdict,
                "confidence": confidence,
                "is_reused": is_reused,
                "reused_source": reused_source,
                "manipulation_score": manipulation_score,
                "metadata": metadata,
                "explanation": explanation,
                "hash": hash_str
            }

            # Save hash for future comparison
            if not is_reused:
                filename = Path(image_path).name
                self._save_hash(hash_str, filename)

            logger.info(f"Image analysis completed: {verdict} ({confidence:.3f})")
            return result

        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return {
                "verdict": "error",
                "confidence": 0.0,
                "error": str(e)
            }

    def _extract_metadata(self, image_path: str) -> Dict[str, Any]:
        """Extract basic metadata from image"""
        try:
            image = Image.open(image_path)
            return {
                "format": image.format,
                "size": image.size,
                "mode": image.mode,
                "has_exif": hasattr(image, '_getexif') and image._getexif() is not None
            }
        except Exception:
            return {"error": "Could not extract metadata"}

    def _detect_basic_manipulation(self, image: Image.Image) -> float:
        """
        Basic manipulation detection using simple heuristics

        Returns:
            Score between 0-1 indicating likelihood of manipulation
        """
        score = 0.0

        # Convert to numpy array
        img_array = np.array(image)

        # Check for unusual color distributions
        if len(img_array.shape) == 3:
            # Check for uniform colors (possible generated images)
            std_dev = np.std(img_array, axis=(0, 1))
            if np.mean(std_dev) < 10:  # Very low variance
                score += 0.3

            # Check for artificial patterns
            # This is a very basic check
            edges = np.abs(np.diff(img_array, axis=0)).mean()
            if edges < 5:  # Very smooth image
                score += 0.2

        # Check file size vs dimensions (unusually small files might be compressed)
        file_size = os.path.getsize(image.filename) if hasattr(image, 'filename') else 0
        expected_size = image.size[0] * image.size[1] * 3  # Rough estimate

        if file_size < expected_size * 0.1:  # Much smaller than expected
            score += 0.3

        return min(score, 1.0)

    def compare_images(self, image1_path: str, image2_path: str) -> Dict[str, Any]:
        """Compare two images for similarity"""
        try:
            img1 = Image.open(image1_path)
            img2 = Image.open(image2_path)

            hash1 = imagehash.phash(img1)
            hash2 = imagehash.phash(img2)

            # Calculate Hamming distance
            distance = hash1 - hash2
            max_distance = len(str(hash1)) * 4  # Rough max distance
            similarity = 1 - (distance / max_distance)

            return {
                "similarity": float(similarity),
                "distance": distance,
                "are_similar": similarity > 0.9  # Threshold for similarity
            }

        except Exception as e:
            logger.error(f"Error comparing images: {e}")
            return {"error": str(e)}


# Global image analyzer instance
image_analyzer = ImageAnalyzer()