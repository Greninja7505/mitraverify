"""
Text Analysis Module for MitraVerify
Handles multilingual misinformation detection using MURIL model
"""
import logging
from typing import Dict, List, Optional, Tuple, Any
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
from sklearn.calibration import CalibratedClassifierCV

from config.settings import settings
from utils.language_detection import detect_language


logger = logging.getLogger(__name__)


class TextAnalyzer:
    """Text analyzer for misinformation detection"""

    def __init__(self, model_name: Optional[str] = None):
        """Initialize the text analyzer with pre-trained model"""
        self.model_name = model_name or settings.text_model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.tokenizer = None
        self.calibrator = None
        self.id2label = {0: "reliable", 1: "misinformation"}
        self.label2id = {v: k for k, v in self.id2label.items()}

        self._load_model()

    def _load_model(self):
        """Load the pre-trained MURIL model"""
        try:
            logger.info(f"Loading text model: {self.model_name}")

            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=settings.model_cache_dir
            )

            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name,
                cache_dir=settings.model_cache_dir,
                num_labels=2,
                id2label=self.id2label,
                label2id=self.label2id
            )

            self.model.to(self.device)
            self.model.eval()

            logger.info("Text model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load text model: {e}")
            raise

    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for model input"""
        # Basic cleaning
        text = text.strip()

        # Language detection and validation
        lang = detect_language(text)
        if lang not in ['en', 'hi']:
            logger.warning(f"Unsupported language detected: {lang}")

        return text

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for misinformation

        Args:
            text: Input text to analyze

        Returns:
            Dict containing prediction, confidence, and explanation
        """
        try:
            # Preprocess text
            processed_text = self._preprocess_text(text)

            # Tokenize
            inputs = self.tokenizer(
                processed_text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            )

            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Get prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=1).cpu().numpy()[0]

            # Get prediction - ensure scalar values
            predicted_class = int(np.argmax(probabilities))
            confidence = float(probabilities[predicted_class])

            # Apply calibration if available
            if self.calibrator:
                try:
                    calibrated_prob = self.calibrator.predict_proba([[confidence]])[0]
                    confidence = float(calibrated_prob[predicted_class])
                except Exception as calib_error:
                    logger.warning(f"Calibration failed, using raw confidence: {calib_error}")
                    # Continue with raw confidence

            # Generate explanation
            explanation = self._generate_explanation(
                text, self.id2label[predicted_class], confidence
            )

            result = {
                "prediction": self.id2label[predicted_class],
                "confidence": confidence,
                "probabilities": {
                    "reliable": float(probabilities[0]),
                    "misinformation": float(probabilities[1])
                },
                "language": detect_language(text),
                "explanation": explanation,
                "model_used": self.model_name
            }

            logger.info(f"Text analysis completed: {result['prediction']} ({result['confidence']:.3f})")
            return result

        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            return {
                "prediction": "error",
                "confidence": 0.0,
                "error": str(e),
                "language": detect_language(text) if text else "unknown"
            }

    def _generate_explanation(self, text: str, prediction: str, confidence: float) -> str:
        """Generate human-readable explanation for the prediction"""
        if prediction == "misinformation":
            if confidence > 0.8:
                return "High confidence detection of misinformation patterns in the text."
            elif confidence > 0.6:
                return "Moderate confidence detection of potential misinformation."
            else:
                return "Low confidence detection of possible misinformation patterns."
        else:
            if confidence > 0.8:
                return "High confidence that the text appears reliable."
            elif confidence > 0.6:
                return "Moderate confidence that the text appears reliable."
            else:
                return "Low confidence assessment - text may need further verification."

    def calibrate_model(self, calibration_data: List[Tuple[str, int]]):
        """
        Calibrate the model using Platt scaling

        Args:
            calibration_data: List of (text, label) tuples for calibration
        """
        try:
            logger.info("Starting model calibration...")

            # Extract features and labels
            texts = [item[0] for item in calibration_data]
            labels = [item[1] for item in calibration_data]

            # Get model predictions
            predictions = []
            for text in texts:
                result = self.analyze_text(text)
                predictions.append(result["probabilities"]["misinformation"])

            # Fit calibrator
            self.calibrator = CalibratedClassifierCV(cv='prefit')
            self.calibrator.fit(np.array(predictions).reshape(-1, 1), labels)

            logger.info("Model calibration completed")

        except Exception as e:
            logger.error(f"Error during calibration: {e}")
            self.calibrator = None

    def batch_analyze(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple texts in batch"""
        return [self.analyze_text(text) for text in texts]


# Global text analyzer instance
text_analyzer = TextAnalyzer()