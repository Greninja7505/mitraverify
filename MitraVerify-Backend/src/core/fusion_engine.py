"""
Fusion Engine for MitraVerify
Combines text and image analysis results
"""
import logging
from typing import Dict, List, Optional, Any
import numpy as np

from core.text_analyzer import text_analyzer
from core.image_analyzer import image_analyzer
from core.evidence_retrieval import evidence_retriever


logger = logging.getLogger(__name__)


class FusionEngine:
    """Fusion engine for combining multimodal analysis"""

    def __init__(self):
        """Initialize the fusion engine"""
        self.text_analyzer = text_analyzer
        self.image_analyzer = image_analyzer
        self.evidence_retriever = evidence_retriever

    def analyze_content(self, text: Optional[str] = None,
                       image_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze content combining text and image analysis

        Args:
            text: Text content to analyze
            image_path: Path to image file to analyze

        Returns:
            Combined analysis result
        """
        results = {
            "overall_verdict": "unknown",
            "confidence": 0.0,
            "text_analysis": None,
            "image_analysis": None,
            "evidence": [],
            "explanation": "",
            "processing_time": 0
        }

        try:
            import time
            start_time = time.time()

            # Analyze text if provided
            if text:
                text_result = self.text_analyzer.analyze_text(text)
                results["text_analysis"] = text_result

                # Only retrieve evidence if text analysis was successful
                if text_result.get("prediction") != "error":
                    try:
                        evidence = self.evidence_retriever.retrieve_evidence(text, top_k=2)
                        results["evidence"] = evidence
                    except Exception as e:
                        logger.warning(f"Evidence retrieval failed: {e}")
                        results["evidence"] = []

            # Analyze image if provided
            if image_path:
                image_result = self.image_analyzer.analyze_image(image_path)
                results["image_analysis"] = image_result

            # Fuse results
            overall_result = self._fuse_results(results)
            results.update(overall_result)

            results["processing_time"] = time.time() - start_time

            logger.info(f"Content analysis completed: {results['overall_verdict']} ({results['confidence']:.3f})")
            return results

        except Exception as e:
            logger.error(f"Error in content analysis: {e}")
            results["error"] = str(e)
            return results

    def _fuse_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Fuse text and image analysis results"""
        text_result = results.get("text_analysis")
        image_result = results.get("image_analysis")

        # Initialize with neutral values
        overall_verdict = "unknown"
        confidence = 0.5
        explanations = []

        # Text analysis contribution
        if text_result:
            prediction = text_result.get("prediction")
            # Safe string comparison to avoid array issues - convert everything to string first
            prediction_str = str(prediction) if prediction is not None else ""
            if prediction_str and prediction_str != "error" and prediction_str != "None":
                text_pred = prediction_str
                text_conf = text_result.get("confidence", 0.5)
                
                # Ensure text_conf is a scalar value
                if isinstance(text_conf, (list, np.ndarray)):
                    text_conf = float(text_conf[0]) if len(text_conf) > 0 else 0.5
                else:
                    text_conf = float(text_conf)

                # Use the model's actual analysis results
                if text_pred == "misinformation":
                    overall_verdict = "misinformation"
                    confidence = text_conf
                    explanations.append(f"Text analysis indicates misinformation with {text_conf:.1%} confidence")
                else:
                    overall_verdict = "reliable"
                    confidence = text_conf
                    explanations.append(f"Text analysis indicates reliable content with {text_conf:.1%} confidence")
                
                # Add model explanation if available
                text_explanation = text_result.get("explanation", "")
                if text_explanation and len(text_explanation) > 10:
                    explanations.append(f"Analysis details: {text_explanation}")

        # Image analysis contribution
        if image_result and image_result.get("verdict") != "error":
            image_verdict = image_result["verdict"]
            image_conf = image_result.get("confidence", 0.5)
            
            # Ensure image_conf is a scalar value
            if isinstance(image_conf, (list, np.ndarray)):
                image_conf = float(image_conf[0]) if len(image_conf) > 0 else 0.5
            else:
                image_conf = float(image_conf)

            if image_verdict == "potentially_manipulated":
                if overall_verdict == "reliable":
                    # Conflict - image suggests manipulation but text is reliable
                    overall_verdict = "needs_verification"
                    confidence = min(confidence, image_conf)
                    explanations.append(f"Image analysis suggests potential manipulation with {image_conf:.1%} confidence")
                else:
                    # Both suggest issues
                    overall_verdict = "misinformation"
                    confidence = max(confidence, image_conf)
                    explanations.append(f"Image analysis confirms potential manipulation with {image_conf:.1%} confidence")
            elif image_verdict == "authentic":
                if overall_verdict == "unknown":
                    overall_verdict = "reliable"
                    confidence = image_conf
                    explanations.append(f"Image analysis indicates authentic content with {image_conf:.1%} confidence")
                elif overall_verdict == "reliable":
                    # Both text and image suggest reliable content
                    confidence = max(confidence, image_conf)
                    explanations.append(f"Image analysis confirms authentic content with {image_conf:.1%} confidence")

        # Evidence contribution
        evidence = results.get("evidence", [])
        if evidence and len(evidence) > 0:
            false_evidence = [e for e in evidence if e.get("verdict") == "false"]
            if len(false_evidence) > 0:
                if overall_verdict == "unknown":
                    overall_verdict = "likely_misinformation"
                    confidence = 0.7
                elif overall_verdict == "reliable":
                    overall_verdict = "needs_verification"
                    confidence = min(confidence, 0.6)
                explanations.append(f"Found {len(false_evidence)} similar debunked claims in evidence database")

        # Ensure confidence is within valid range and is a scalar
        confidence = max(0.0, min(1.0, float(confidence)))

        # Generate final explanation
        if explanations:
            final_explanation = " ".join(explanations)
        else:
            final_explanation = "Analysis completed but no clear indicators found"

        return {
            "overall_verdict": overall_verdict,
            "confidence": confidence,
            "explanation": final_explanation
        }

    def batch_analyze(self, contents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze multiple content items in batch"""
        results = []
        for content in contents:
            try:
                result = self.analyze_content(**content)
                results.append(result)
            except Exception as e:
                logger.error(f"Error in batch analysis: {e}")
                results.append({
                    "overall_verdict": "error",
                    "confidence": 0.0,
                    "error": str(e)
                })
        return results


# Global fusion engine instance
fusion_engine = FusionEngine()