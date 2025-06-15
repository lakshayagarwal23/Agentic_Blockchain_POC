import pytest
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_python_version():
    """Test that Python version is compatible"""
    assert sys.version_info >= (3, 8), "Python 3.8 or higher required"

def test_imports():
    """Test that basic imports work"""
    try:
        import flask
        import sqlalchemy
        import spacy
        import nltk
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_spacy_model():
    """Test that spaCy model is available"""
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✅ spaCy model loaded successfully")
        return True
    except Exception as e:
        print(f"❌ spaCy model error: {e}")
        return False

def test_nltk_data():
    """Test that NLTK data is available"""
    try:
        import nltk
        from nltk.sentiment import SentimentIntensityAnalyzer
        analyzer = SentimentIntensityAnalyzer()
        print("✅ NLTK data loaded successfully")
        return True
    except Exception as e:
        print(f"❌ NLTK data error: {e}")
        return False

if __name__ == '__main__':
    print("🧪 Running basic tests...")
    
    tests = [
        test_python_version,
        test_imports, 
        test_spacy_model,
        test_nltk_data
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Ready to start the application.")
    else:
        print("⚠ Some tests failed. Please resolve issues before continuing.")
