#!/usr/bin/env python3
"""
Sample Data Creation Script for MitraVerify
Creates sample datasets for testing and demonstration
"""
import json
import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings


def create_sample_text_data():
    """Create sample text data for testing"""
    sample_data = [
        {
            "id": "sample_001",
            "text": "COVID-19 vaccines contain microchips that track people",
            "language": "en",
            "verdict": "misinformation",
            "confidence": 0.95,
            "source": "WhatsApp forward"
        },
        {
            "id": "sample_002",
            "text": "5G towers are spreading coronavirus",
            "language": "en",
            "verdict": "misinformation",
            "confidence": 0.92,
            "source": "Social media post"
        },
        {
            "id": "sample_003",
            "text": "Drinking cow urine cures all diseases",
            "language": "en",
            "verdict": "misinformation",
            "confidence": 0.88,
            "source": "Facebook post"
        },
        {
            "id": "sample_004",
            "text": "The earth is flat and NASA is hiding the truth",
            "language": "en",
            "verdict": "misinformation",
            "confidence": 0.96,
            "source": "Twitter thread"
        },
        {
            "id": "sample_005",
            "text": "Vaccines cause autism in children",
            "language": "en",
            "verdict": "misinformation",
            "confidence": 0.89,
            "source": "WhatsApp message"
        },
        {
            "id": "sample_006",
            "text": "WHO officially declared COVID-19 as pandemic on March 11, 2020",
            "language": "en",
            "verdict": "reliable",
            "confidence": 0.87,
            "source": "Official WHO statement"
        },
        {
            "id": "sample_007",
            "text": "India successfully launched Chandrayaan-2 lunar mission",
            "language": "en",
            "verdict": "reliable",
            "confidence": 0.91,
            "source": "ISRO announcement"
        },
        {
            "id": "sample_008",
            "text": "The monsoon season in India typically lasts from June to September",
            "language": "en",
            "verdict": "reliable",
            "confidence": 0.94,
            "source": "IMD weather report"
        },
        {
            "id": "sample_009",
            "text": "कोविड-19 वैक्सीन में ट्रैकिंग चिप होती है",
            "language": "hi",
            "verdict": "misinformation",
            "confidence": 0.93,
            "source": "WhatsApp forward"
        },
        {
            "id": "sample_010",
            "text": "5G टावर कोरोना वायरस फैला रहे हैं",
            "language": "hi",
            "verdict": "misinformation",
            "confidence": 0.90,
            "source": "Social media post"
        }
    ]

    sample_file = Path(settings.model_cache_dir).parent / "sample" / "test_texts.json"
    sample_file.parent.mkdir(parents=True, exist_ok=True)

    with open(sample_file, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)

    print(f"Created sample text data: {sample_file}")
    return sample_data


def create_sample_evidence_data():
    """Create sample evidence database"""
    evidence_data = [
        {
            "id": "fact_001",
            "claim": "COVID-19 vaccines contain microchips",
            "verdict": "false",
            "explanation": "This is a conspiracy theory. COVID-19 vaccines do not contain microchips or tracking devices.",
            "source": "WHO Fact Check",
            "url": "https://www.who.int/news-room/feature-stories/detail/vaccines-and-microchips",
            "language": "en",
            "date_checked": "2023-12-01"
        },
        {
            "id": "fact_002",
            "claim": "5G towers cause COVID-19",
            "verdict": "false",
            "explanation": "There is no scientific evidence linking 5G technology to COVID-19 or any health issues.",
            "source": "CDC",
            "url": "https://www.cdc.gov/coronavirus/2019-ncov/science/science-briefs/5g-mobile-networks-COVID-19.html",
            "language": "en",
            "date_checked": "2023-12-01"
        },
        {
            "id": "fact_003",
            "claim": "कोविड-19 वैक्सीन में माइक्रोचिप हैं",
            "verdict": "false",
            "explanation": "यह एक साजिश सिद्धांत है। कोविड-19 वैक्सीन में माइक्रोचिप या ट्रैकिंग डिवाइस नहीं होते।",
            "source": "WHO Fact Check",
            "url": "https://www.who.int/news-room/feature-stories/detail/vaccines-and-microchips",
            "language": "hi",
            "date_checked": "2023-12-01"
        }
    ]

    evidence_file = Path(settings.evidence_db_path)
    evidence_file.parent.mkdir(parents=True, exist_ok=True)

    with open(evidence_file, 'w', encoding='utf-8') as f:
        json.dump(evidence_data, f, ensure_ascii=False, indent=2)

    print(f"Created sample evidence data: {evidence_file}")
    return evidence_data


def create_sample_image_data():
    """Create sample image data directory structure"""
    image_dir = Path(settings.model_cache_dir).parent / "sample" / "test_images"
    image_dir.mkdir(parents=True, exist_ok=True)

    # Create a placeholder file
    placeholder = image_dir / "README.md"
    with open(placeholder, 'w') as f:
        f.write("""# Sample Images Directory

This directory should contain sample images for testing the image analysis functionality.

## Sample Images to Add:
1. authentic_image_001.jpg - A genuine photograph
2. manipulated_image_001.jpg - An image with digital manipulation
3. reused_image_001.jpg - An image that appears in multiple contexts

## Usage:
- Place test images in this directory
- The system will analyze them for potential manipulation and reuse
- Results will be compared against ground truth labels
""")

    print(f"Created sample image directory: {image_dir}")
    return str(image_dir)


def main():
    """Main function to create all sample data"""
    print("Creating MitraVerify sample data...")

    try:
        # Create sample text data
        text_data = create_sample_text_data()
        print(f"✓ Created {len(text_data)} sample text entries")

        # Create sample evidence data
        evidence_data = create_sample_evidence_data()
        print(f"✓ Created {len(evidence_data)} sample evidence entries")

        # Create sample image directory
        image_dir = create_sample_image_data()
        print(f"✓ Created sample image directory: {image_dir}")

        print("\nSample data creation completed successfully!")
        print("\nNext steps:")
        print("1. Run 'python scripts/download_models.py' to download required models")
        print("2. Run 'python src/api/main.py' to start the API server")
        print("3. Open http://localhost:8000 in your browser")

    except Exception as e:
        print(f"Error creating sample data: {e}")
        return False

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)