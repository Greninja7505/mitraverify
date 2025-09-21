"""
Evidence Retrieval Module for MitraVerify
Basic fact-checking against curated sources
"""
import logging
from typing import Dict, List, Optional, Any
import json
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer

from config.settings import settings


logger = logging.getLogger(__name__)


class EvidenceRetriever:
    """Evidence retriever for fact-checking"""

    def __init__(self):
        """Initialize the evidence retriever"""
        self.evidence_db_path = Path(settings.evidence_db_path)
        self.embedding_model_name = settings.embedding_model_name
        self.model = None
        self.evidence_data = []
        self.embeddings = None

        self._load_evidence_database()
        self._load_embedding_model()

    def _load_evidence_database(self):
        """Load the fact-check evidence database"""
        if not self.evidence_db_path.exists():
            logger.warning(f"Evidence database not found: {self.evidence_db_path}")
            self._create_sample_evidence()
            return

        try:
            with open(self.evidence_db_path, 'r', encoding='utf-8') as f:
                self.evidence_data = json.load(f)
            logger.info(f"Loaded {len(self.evidence_data)} evidence items")
        except Exception as e:
            logger.error(f"Error loading evidence database: {e}")
            self.evidence_data = []

    def _create_sample_evidence(self):
        """Create sample evidence database for MVP"""
        sample_evidence = [
            {
                "id": "sample_001",
                "claim": "COVID-19 vaccines contain microchips",
                "verdict": "false",
                "explanation": "This is a conspiracy theory. COVID-19 vaccines do not contain microchips or tracking devices.",
                "source": "WHO Fact Check",
                "url": "https://www.who.int/news-room/feature-stories/detail/vaccines-and-microchips",
                "language": "en"
            },
            {
                "id": "sample_002",
                "claim": "5G towers cause COVID-19",
                "verdict": "false",
                "explanation": "There is no scientific evidence linking 5G technology to COVID-19 or any health issues.",
                "source": "CDC",
                "url": "https://www.cdc.gov/coronavirus/2019-ncov/science/science-briefs/5g-mobile-networks-COVID-19.html",
                "language": "en"
            },
            {
                "id": "sample_003",
                "claim": "कोविड-19 वैक्सीन में माइक्रोचिप हैं",
                "verdict": "false",
                "explanation": "यह एक साजिश सिद्धांत है। कोविड-19 वैक्सीन में माइक्रोचिप या ट्रैकिंग डिवाइस नहीं होते।",
                "source": "WHO Fact Check",
                "url": "https://www.who.int/news-room/feature-stories/detail/vaccines-and-microchips",
                "language": "hi"
            }
        ]

        self.evidence_data = sample_evidence

        # Save to file
        try:
            with open(self.evidence_db_path, 'w', encoding='utf-8') as f:
                json.dump(sample_evidence, f, ensure_ascii=False, indent=2)
            logger.info("Created sample evidence database")
        except Exception as e:
            logger.error(f"Error creating sample evidence: {e}")

    def _load_embedding_model(self):
        """Load the sentence transformer model"""
        try:
            self.model = SentenceTransformer(
                self.embedding_model_name,
                cache_folder=settings.model_cache_dir
            )
            logger.info("Embedding model loaded successfully")

            # Generate embeddings for evidence
            if self.evidence_data:
                texts = [item['claim'] for item in self.evidence_data]
                self.embeddings = self.model.encode(texts, convert_to_numpy=True)
                logger.info(f"Generated embeddings for {len(texts)} evidence items")

        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            self.model = None

    def retrieve_evidence(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve relevant evidence for a given query

        Args:
            query: The claim or text to fact-check
            top_k: Number of top results to return

        Returns:
            List of relevant evidence items
        """
        if not self.model or not self.embeddings:
            logger.warning("Embedding model not available")
            return []

        try:
            # Encode query
            query_embedding = self.model.encode([query], convert_to_numpy=True)[0]

            # Calculate similarities
            similarities = np.dot(self.embeddings, query_embedding) / (
                np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
            )

            # Get top-k results
            top_indices = np.argsort(similarities)[::-1][:top_k]

            results = []
            for idx in top_indices:
                similarity = float(similarities[idx])
                # Ensure similarity is a scalar value for comparison
                if float(similarity) > 0.3:  # Similarity threshold
                    evidence = self.evidence_data[idx].copy()
                    evidence['similarity'] = similarity
                    results.append(evidence)

            logger.info(f"Retrieved {len(results)} evidence items for query")
            return results

        except Exception as e:
            logger.error(f"Error retrieving evidence: {e}")
            return []

    def add_evidence(self, claim: str, verdict: str, explanation: str,
                    source: str, url: Optional[str] = None, language: str = "en"):
        """Add new evidence to the database"""
        new_evidence = {
            "id": f"evidence_{len(self.evidence_data) + 1:03d}",
            "claim": claim,
            "verdict": verdict,
            "explanation": explanation,
            "source": source,
            "url": url,
            "language": language
        }

        self.evidence_data.append(new_evidence)

        # Update embeddings
        if self.model:
            texts = [item['claim'] for item in self.evidence_data]
            self.embeddings = self.model.encode(texts, convert_to_numpy=True)

        # Save to file
        try:
            with open(self.evidence_db_path, 'w', encoding='utf-8') as f:
                json.dump(self.evidence_data, f, ensure_ascii=False, indent=2)
            logger.info("Added new evidence to database")
        except Exception as e:
            logger.error(f"Error saving evidence: {e}")


# Global evidence retriever instance
evidence_retriever = EvidenceRetriever()