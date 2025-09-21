#!/usr/bin/env python3
"""
Real-time Text Analysis Demo
Shows dynamic confidence scores based on content
"""
import sys
import os

# Add the project root and src directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_dir)

def test_dynamic_analysis():
    """Test the enhanced text analyzer with various examples"""
    try:
        from src.core.text_analyzer import TextAnalyzer
        
        # Initialize the text analyzer
        text_analyzer = TextAnalyzer()
        text_analyzer.load_model()  # Load the model
        
        # Test cases with different content types
        test_cases = [
            {
                "text": "According to a peer-reviewed study published in Nature, researchers found that the new treatment is effective.",
                "expected": "reliable",
                "description": "Scientific reference"
            },
            {
                "text": "DOCTORS DON'T WANT YOU TO KNOW THIS SECRET CURE! BIG PHARMA IS HIDING THE TRUTH!",
                "expected": "misinformation", 
                "description": "Conspiracy language with caps"
            },
            {
                "text": "Breaking news: Unverified sources claim miracle vaccine cure banned by government!",
                "expected": "misinformation",
                "description": "Suspicious claims"
            },
            {
                "text": "The WHO recommends vaccination based on clinical trial data and FDA approval.",
                "expected": "reliable",
                "description": "Official health guidance"
            },
            {
                "text": "COVID is fake and 5G causes cancer wake up people!",
                "expected": "misinformation",
                "description": "Conspiracy theories"
            },
            {
                "text": "Research shows that exercise may improve health outcomes.",
                "expected": "reliable", 
                "description": "Moderate health claim"
            },
            {
                "text": "Fake!",
                "expected": "misinformation",
                "description": "Very short suspicious text"
            }
        ]
        
        print("🔍 MitraVerify Enhanced Text Analysis Demo")
        print("=" * 60)
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n📝 Test Case {i}: {case['description']}")
            print(f"Text: \"{case['text']}\"")
            print("-" * 40)
            
            # Analyze the text
            result = text_analyzer.analyze_text(case['text'])
            
            # Display results
            prediction = result.get('prediction', 'unknown')
            confidence = result.get('confidence', 0.0)
            explanation = result.get('explanation', 'No explanation')
            
            print(f"🎯 Prediction: {prediction.upper()}")
            print(f"📊 Confidence: {confidence:.1%}")
            print(f"💡 Explanation: {explanation}")
            
            # Check if prediction matches expectation
            match_status = "✅ MATCH" if prediction == case['expected'] else "❌ DIFFERENT"
            print(f"🔍 Expected: {case['expected']} | Result: {match_status}")
            
        print("\n" + "=" * 60)
        print("🚀 Demo completed! The analysis shows dynamic confidence scores")
        print("   based on content patterns, not static 50% values.")
        
    except Exception as e:
        print(f"❌ Error in demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dynamic_analysis()