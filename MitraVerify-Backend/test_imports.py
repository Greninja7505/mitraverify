#!/usr/bin/env python3
"""
Test script for MitraVerify modules
"""
import sys
import os

# Add the project root and src directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_dir)

try:
    from src.core.text_analyzer import text_analyzer
    print("✓ Text analyzer import successful")
except ImportError as e:
    print(f"✗ Text analyzer import failed: {e}")

try:
    from src.core.image_analyzer import image_analyzer
    print("✓ Image analyzer import successful")
except ImportError as e:
    print(f"✗ Image analyzer import failed: {e}")

try:
    from src.core.evidence_retrieval import evidence_retriever
    print("✓ Evidence retrieval import successful")
except ImportError as e:
    print(f"✗ Evidence retrieval import failed: {e}")

try:
    from src.api.main import app
    print("✓ API import successful")
except ImportError as e:
    print(f"✗ API import failed: {e}")

print("\nTest completed!")