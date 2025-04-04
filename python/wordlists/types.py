"""Type definitions for the wordlists package."""

from enum import Enum
from typing import Dict, List, Optional, Union, Set, Any
from typing_extensions import TypedDict

class WordlistId(str, Enum):
    """Available wordlist identifiers."""
    
    # Historical and Fundamental Lists
    SWADESH_100 = "swadesh-100"
    SWADESH_207 = "swadesh-207"
    BASIC_ENGLISH = "basic-english"
    ROGET_COMPLETE = "roget-complete"
    
    # Common English Lists
    DOLCH = "dolch"
    FRY_1000 = "fry-1000"
    
    # Grammatical Parts of Speech
    PREPOSITIONS = "prepositions"
    ARTICLES = "articles"
    CONJUNCTIONS = "conjunctions"
    PRONOUNS = "pronouns"
    AUXILIARY_VERBS = "auxiliary-verbs"
    
    # Stop Words
    STOP_WORDS_NLTK = "stop-words-nltk"
    STOP_WORDS_SPACY = "stop-words-spacy"
    STOP_WORDS_SKLEARN = "stop-words-sklearn"
    STOP_WORDS_FOX = "stop-words-fox"
    STOP_WORDS_COMPREHENSIVE = "stop-words-comprehensive"

# Type alias for a single word
Word = str

# Type alias for a list of words
WordList = List[Word]

class WordlistMeta(TypedDict, total=False):
    """Metadata for a wordlist."""
    
    id: WordlistId
    name: str
    description: str
    count: int
    source: Optional[str]
    type: Optional[str]
    year: Optional[int]
    citation: Optional[str]
    license: Optional[str]
    version: Optional[str]
    url: Optional[str]

class RogetCategory(TypedDict):
    """Data structure for a Roget thesaurus category."""
    
    id: str
    name: str
    words: List[str]

class RogetSection(TypedDict):
    """Data structure for a Roget thesaurus section."""
    
    name: str
    categories: Dict[str, RogetCategory]

class RogetClass(TypedDict):
    """Data structure for a Roget thesaurus class."""
    
    name: str
    sections: Dict[str, RogetSection]

class RogetThesaurus(TypedDict):
    """Data structure for the complete Roget thesaurus."""
    
    classes: Dict[str, RogetClass]
    total_categories: int
    total_words: int

class StopWordsOptions(TypedDict, total=False):
    """Options for creating custom stop word lists."""
    
    base: Optional[WordlistId]
    include: Optional[List[Union[WordlistId, Word]]]
    exclude: Optional[List[Word]]

class OverlapStats(TypedDict):
    """Statistics about overlap between two word lists."""
    
    words: int
    percent_of_first: float
    percent_of_second: float

# Type alias for results of checking word membership in a list
IsInListResult = Dict[str, bool]

# Type alias for wordlist registry
WordlistRegistry = Dict[str, WordlistMeta] 