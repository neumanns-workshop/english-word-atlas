from stop_words.utils import save_stop_words
import subprocess
import sys

def extract():
    """Extract stop words from Gensim"""
    try:
        # Setup Gensim with specific numpy version
        print("Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy==2.2.4"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "gensim"])
        
        # Import and get stop words
        from gensim.parsing.preprocessing import STOPWORDS
        import gensim
        
        # Get stop words
        words = set(STOPWORDS)
        
        # Save the words
        save_stop_words(
            words=words,
            source_name='gensim',
            description='Stop words from Gensim preprocessing module',
            version=gensim.__version__
        )
        print(f"Successfully extracted {len(words)} stop words from Gensim")
    except Exception as e:
        print(f"Error extracting Gensim stop words: {str(e)}") 