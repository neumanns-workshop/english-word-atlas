from stop_words.utils import save_stop_words

def extract():
    """Extract stop words from NLTK"""
    # Setup NLTK
    import subprocess
    import sys
    
    print("Installing nltk...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "nltk"])
    
    import nltk
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')
    
    from nltk.corpus import stopwords
    words = set(stopwords.words('english'))
    
    save_stop_words(
        words=words,
        source_name='nltk',
        description='Stop words from NLTK English corpus',
        version=nltk.__version__
    ) 