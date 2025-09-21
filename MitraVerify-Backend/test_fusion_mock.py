#!/usr/bin/env python3
"""
Test fusion engine with mocked dependencies
"""
import sys
import os
from unittest.mock import Mock

# Add src directory to path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_mock_analyzer():
    """Create a mock analyzer for testing"""
    mock = Mock()
    mock.analyze_text.return_value = {
        "prediction": "reliable",
        "confidence": 0.85,
        "processing_time": 0.1
    }
    mock.analyze_image.return_value = {
        "verdict": "authentic", 
        "confidence": 0.75,
        "processing_time": 0.2
    }
    return mock

def create_mock_evidence_retriever():
    """Create a mock evidence retriever"""
    mock = Mock()
    mock.retrieve_evidence.return_value = [
        {
            "id": "test_001",
            "verdict": "true",
            "confidence": 0.9,
            "source": "test_source"
        }
    ]
    return mock

def test_fusion_with_mocks():
    """Test fusion engine with mocked dependencies"""
    try:
        print("Testing fusion engine with mocked dependencies...")
        
        # Mock the dependencies before importing
        sys.modules['core.text_analyzer'] = Mock()
        sys.modules['core.image_analyzer'] = Mock() 
        sys.modules['core.evidence_retrieval'] = Mock()
        
        # Create mock instances
        text_mock = create_mock_analyzer()
        image_mock = create_mock_analyzer()
        evidence_mock = create_mock_evidence_retriever()
        
        sys.modules['core.text_analyzer'].text_analyzer = text_mock
        sys.modules['core.image_analyzer'].image_analyzer = image_mock
        sys.modules['core.evidence_retrieval'].evidence_retriever = evidence_mock
        
        # Now try to import
        from core.fusion_engine import FusionEngine, fusion_engine
        print("✓ Successfully imported FusionEngine with mocks")
        
        # Test creating an instance
        engine = FusionEngine()
        print("✓ Successfully created FusionEngine instance")
        
        # Test analyzing content
        result = engine.analyze_content(text="This is a test message")
        print("✓ Successfully analyzed content")
        print(f"  - Overall verdict: {result.get('overall_verdict')}")
        print(f"  - Confidence: {result.get('confidence')}")
        print(f"  - Processing time: {result.get('processing_time')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing with mocks: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fusion_methods_direct():
    """Test fusion methods directly"""
    try:
        print("\nTesting fusion methods directly...")
        
        # Import just the class definition
        from core.fusion_engine import FusionEngine
        
        # Create instance without initialization
        engine = FusionEngine.__new__(FusionEngine)
        
        # Test the _fuse_results method directly
        test_results = {
            "text_analysis": {
                "prediction": "reliable",
                "confidence": 0.8
            },
            "image_analysis": {
                "verdict": "authentic",
                "confidence": 0.7
            },
            "evidence": []
        }
        
        fused = engine._fuse_results(test_results)
        print("✓ Successfully tested _fuse_results method")
        print(f"  - Fused verdict: {fused.get('overall_verdict')}")
        print(f"  - Fused confidence: {fused.get('confidence')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing methods directly: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run tests"""
    print("=== Fusion Engine Mock Test ===\n")
    
    tests = [
        test_fusion_with_mocks,
        test_fusion_methods_direct
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== Results: {passed}/{len(tests)} tests passed ===")
    
    if passed == len(tests):
        print("\n✓ Fusion engine logic appears to be working correctly!")
        print("  The hanging issue is likely due to model loading in dependencies.")
    else:
        print("\n✗ Some fusion engine logic issues found.")
    
    return 0 if passed == len(tests) else 1

if __name__ == "__main__":
    exit(main())