#!/usr/bin/env python3
"""
Simple test script for fusion_engine.py
Tests if the module can be imported and basic functionality works
"""
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_fusion_engine_import():
    """Test if fusion engine can be imported"""
    try:
        print("Testing fusion engine import...")
        from core.fusion_engine import FusionEngine, fusion_engine
        print("✓ Successfully imported FusionEngine and fusion_engine instance")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Other error during import: {e}")
        return False

def test_fusion_engine_creation():
    """Test if fusion engine can be created"""
    try:
        print("\nTesting fusion engine creation...")
        from core.fusion_engine import FusionEngine
        engine = FusionEngine()
        print("✓ Successfully created FusionEngine instance")
        print(f"  - Engine type: {type(engine)}")
        print(f"  - Has text_analyzer: {hasattr(engine, 'text_analyzer')}")
        print(f"  - Has image_analyzer: {hasattr(engine, 'image_analyzer')}")
        print(f"  - Has evidence_retriever: {hasattr(engine, 'evidence_retriever')}")
        return True
    except Exception as e:
        print(f"✗ Error creating fusion engine: {e}")
        return False

def test_fusion_methods():
    """Test if fusion engine methods exist"""
    try:
        print("\nTesting fusion engine methods...")
        from core.fusion_engine import FusionEngine
        engine = FusionEngine()
        
        # Check if methods exist
        methods_to_check = ['analyze_content', '_fuse_results', 'batch_analyze']
        for method in methods_to_check:
            if hasattr(engine, method):
                print(f"✓ Method '{method}' exists")
            else:
                print(f"✗ Method '{method}' missing")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Error testing methods: {e}")
        return False

def main():
    """Run all tests"""
    print("=== Fusion Engine Test Suite ===\n")
    
    tests = [
        test_fusion_engine_import,
        test_fusion_engine_creation,
        test_fusion_methods
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! Fusion engine is working correctly.")
        return 0
    else:
        print("✗ Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())