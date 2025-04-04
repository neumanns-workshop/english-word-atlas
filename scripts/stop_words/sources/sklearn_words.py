from stop_words.utils import save_stop_words
import subprocess
import sys

def extract():
    """Extract stop words from scikit-learn"""
    try:
        # Setup scikit-learn
        print("Installing scikit-learn...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "scikit-learn"])
        
        # Import and get stop words
        from sklearn.feature_extraction import text
        import sklearn
        words = set(text.ENGLISH_STOP_WORDS)
        
        # Save the words
        save_stop_words(
            words=words,
            source_name='sklearn',
            description='Stop words from scikit-learn English corpus',
            version=sklearn.__version__
        )
        print(f"Successfully extracted {len(words)} stop words from scikit-learn")
    except Exception as e:
        print(f"Error extracting sklearn stop words: {str(e)}") 