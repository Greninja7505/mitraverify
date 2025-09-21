#!/usr/bin/env python3
"""Debug script for fusion engine array error"""

import sys
import os
sys.path.append('src')

from core.text_analyzer import text_analyzer

def test_text_analyzer():
    print("Testing text analyzer...")
    try:
        result = text_analyzer.analyze_text("This is fake news about vaccines being dangerous")
        print(f"Text result type: {type(result)}")
        print(f"Text result: {result}")
        
        # Check prediction field
        prediction = result.get("prediction")
        print(f"Prediction type: {type(prediction)}")
        print(f"Prediction value: {prediction}")
        
        # Test the comparison that might be failing
        if prediction != "error":
            print("Prediction comparison works!")
        else:
            print("Prediction is error")
            
    except Exception as e:
        print(f"Error in text analyzer: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_text_analyzer()