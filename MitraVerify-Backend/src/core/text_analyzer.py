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
            # Detect language
            detected_language = detect_language(text)
            
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

            # Get raw model prediction
            predicted_class = int(np.argmax(probabilities))
            raw_confidence = float(probabilities[predicted_class])

            # Enhance prediction with content-based features
            enhanced_result = self._enhance_prediction(text, predicted_class, raw_confidence, probabilities, detected_language)

            # Generate explanation
            explanation = self._generate_explanation(
                text, enhanced_result["prediction"], enhanced_result["confidence"]
            )

            result = {
                "prediction": enhanced_result["prediction"],
                "confidence": enhanced_result["confidence"],
                "probabilities": enhanced_result["probabilities"],
                "language": detect_language(text),
                "explanation": explanation,
                "model_used": self.model_name,
                "raw_model_output": {
                    "prediction": self.id2label[predicted_class],
                    "confidence": raw_confidence,
                    "raw_probabilities": {
                        "reliable": float(probabilities[0]),
                        "misinformation": float(probabilities[1])
                    }
                }
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

    def _enhance_prediction(self, text: str, predicted_class: int, raw_confidence: float, probabilities: np.ndarray, detected_language: str) -> Dict[str, Any]:
        """
        Enhance the raw model prediction with content-based analysis
        Since MURIL isn't fine-tuned for misinformation, we need to interpret its outputs better
        """
        text_lower = text.lower()
        
        # Content-based confidence adjustments
        confidence_adjustments = 0.0
        
        # Language complexity analysis
        words = text.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        # Sentence structure analysis
        sentences = text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        # Misinformation indicators (strengthen misinformation prediction)
        misinfo_keywords = [
            'fake', 'hoax', 'conspiracy', 'secret', 'hidden', 'exposed', 'truth',
            'lie', 'cover-up', 'scandal', 'shocking', 'urgent', 'warning'
        ]
        
        # Reliability indicators (strengthen reliable prediction)
        reliable_keywords = [
            'study', 'research', 'evidence', 'data', 'analysis', 'expert',
            'scientist', 'doctor', 'professor', 'university', 'official'
        ]
        
        misinfo_count = sum(1 for keyword in misinfo_keywords if keyword in text_lower)
        reliable_count = sum(1 for keyword in reliable_keywords if keyword in text_lower)
        
        # Adjust confidence based on content analysis
        if misinfo_count > reliable_count and misinfo_count > 0:
            # Lean towards misinformation
            if predicted_class == 1:  # Already predicted misinformation
                confidence_adjustments += 0.1 + (misinfo_count * 0.05)
            else:  # Was predicted reliable but has misinfo indicators
                if misinfo_count >= 2:  # Strong indicators, flip prediction
                    predicted_class = 1
                    confidence_adjustments += 0.2
                else:
                    confidence_adjustments -= 0.1  # Lower confidence in reliable prediction
                    
        elif reliable_count > misinfo_count and reliable_count > 0:
            # Lean towards reliable
            if predicted_class == 0:  # Already predicted reliable
                confidence_adjustments += 0.1 + (reliable_count * 0.05)
            else:  # Was predicted misinformation but has reliable indicators
                if reliable_count >= 2:  # Strong indicators, flip prediction
                    predicted_class = 0
                    confidence_adjustments += 0.2
                else:
                    confidence_adjustments -= 0.1  # Lower confidence in misinfo prediction
        
        # Text quality factors
        if len(words) < 5:  # Very short text
            confidence_adjustments -= 0.1
        
        # Excessive punctuation or caps
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        if caps_ratio > 0.3:  # More than 30% caps
            if predicted_class == 1:  # Predicted misinformation
                confidence_adjustments += 0.1
            else:
                confidence_adjustments -= 0.05
        
        # Calculate final confidence
        final_confidence = raw_confidence + confidence_adjustments
        final_confidence = max(0.1, min(0.95, final_confidence))  # Clamp between 10% and 95%
        
        # Recalculate probabilities based on final prediction and confidence
        if predicted_class == 1:  # misinformation
            final_probabilities = {
                "reliable": 1.0 - final_confidence,
                "misinformation": final_confidence
            }
        else:  # reliable
            final_probabilities = {
                "reliable": final_confidence,
                "misinformation": 1.0 - final_confidence
            }
        
        return {
            "prediction": self.id2label[predicted_class],
            "confidence": float(final_confidence),  # Ensure scalar value
            "probabilities": {
                "reliable": float(final_probabilities["reliable"]),
                "misinformation": float(final_probabilities["misinformation"])
            },
            "language": detected_language,
            "explanation": self._generate_explanation(text, self.id2label[predicted_class], final_confidence),
            "model_used": self.model_name
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
    