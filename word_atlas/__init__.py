"""
English Word Atlas - A comprehensive linguistic and semantic atlas of English

A dataset and toolkit for exploring English words and phrases through
their linguistic features, semantic categories, and vector embeddings.
"""

__version__ = "0.1.3"

from word_atlas.atlas import WordAtlas
from word_atlas.wordlist import WordlistBuilder

__all__ = [
    "WordAtlas",
    "WordlistBuilder",
]
