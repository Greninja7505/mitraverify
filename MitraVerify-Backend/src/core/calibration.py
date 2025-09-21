"""
Calibration Module for MitraVerify
Implements confidence calibration for model predictions
"""
import logging
from typing import Dict, List, Optional, Any
import numpy as np
from sklearn.calibration import CalibratedClassifierCV

logger = logging.getLogger(__name__)


class ConfidenceCalibrator:
    """Confidence calibrator for model predictions"""

    def __init__(self):
        """Initialize the calibrator"""
        self.calibrators = {}
        self.calibration_data = {}

    def calibrate_model(self, model_name: str, predictions: List[float],
                       true_labels: List[int]) -> bool:
        """
        Calibrate a model's confidence scores

        Args:
            model_name: Name/identifier of the model
            predictions: List of prediction probabilities
            true_labels: List of true binary labels

        Returns:
            True if calibration successful, False otherwise
        """
        try:
            if len(predictions) != len(true_labels):
                logger.error("Predictions and labels must have same length")
                return False

            if len(predictions) < 10:
                logger.warning("Need at least 10 samples for calibration")
                return False

            # Prepare data
            X = np.array(predictions).reshape(-1, 1)
            y = np.array(true_labels)

            # Fit calibrator
            calibrator = CalibratedClassifierCV(cv='prefit')
            calibrator.fit(X, y)

            self.calibrators[model_name] = calibrator
            self.calibration_data[model_name] = {
                'predictions': predictions,
                'labels': true_labels
            }

            logger.info(f"Calibrated model: {model_name}")
            return True

        except Exception as e:
            logger.error(f"Error calibrating model {model_name}: {e}")
            return False

    def calibrate_prediction(self, model_name: str, prediction: float) -> float:
        """
        Apply calibration to a prediction

        Args:
            model_name: Name/identifier of the model
            prediction: Raw prediction probability

        Returns:
            Calibrated prediction probability
        """
        if model_name not in self.calibrators:
            logger.warning(f"No calibrator found for model: {model_name}")
            return prediction

        try:
            calibrator = self.calibrators[model_name]
            calibrated = calibrator.predict_proba([[prediction]])[0]

            # Return probability for positive class (misinformation)
            return float(calibrated[1])

        except Exception as e:
            logger.error(f"Error applying calibration: {e}")
            return prediction

    def get_calibration_stats(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get calibration statistics for a model"""
        if model_name not in self.calibration_data:
            return None

        data = self.calibration_data[model_name]
        predictions = np.array(data['predictions'])
        labels = np.array(data['labels'])

        # Calculate ECE (Expected Calibration Error)
        n_bins = 10
        bins = np.linspace(0, 1, n_bins + 1)
        bin_indices = np.digitize(predictions, bins) - 1

        ece = 0
        for i in range(n_bins):
            mask = bin_indices == i
            if np.sum(mask) > 0:
                bin_pred = np.mean(predictions[mask])
                bin_true = np.mean(labels[mask])
                bin_size = np.sum(mask)
                ece += (bin_size / len(predictions)) * abs(bin_pred - bin_true)

        return {
            'ece': float(ece),
            'n_samples': len(predictions),
            'accuracy': float(np.mean((predictions > 0.5) == labels))
        }

    def save_calibration(self, filepath: str):
        """Save calibration data to file"""
        try:
            import pickle
            with open(filepath, 'wb') as f:
                pickle.dump({
                    'calibrators': self.calibrators,
                    'calibration_data': self.calibration_data
                }, f)
            logger.info(f"Calibration data saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving calibration: {e}")

    def load_calibration(self, filepath: str):
        """Load calibration data from file"""
        try:
            import pickle
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                self.calibrators = data.get('calibrators', {})
                self.calibration_data = data.get('calibration_data', {})
            logger.info(f"Calibration data loaded from {filepath}")
        except Exception as e:
            logger.error(f"Error loading calibration: {e}")


# Global calibrator instance
calibrator = ConfidenceCalibrator()