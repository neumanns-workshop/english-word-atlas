from stop_words.utils import save_stop_words
import subprocess
import sys

def extract():
    """Extract stop words from spaCy"""
    # Setup spaCy
    print("Installing spacy...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "spacy"])
    
    # Download English model if not present
    try:
        import spacy
        spacy.load('en_core_web_sm')
    except OSError:
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    
    import spacy
    nlp = spacy.load('en_core_web_sm')
    words = nlp.Defaults.stop_words
    
    save_stop_words(
        words=words,
        source_name='spacy',
        description='Stop words from spaCy English model',
        version=spacy.__version__
    ) 