"""Registry of available wordlists with metadata."""

from typing import List, Optional

from .types import WordlistId, WordlistMeta, WordlistRegistry

# Registry of all available wordlists with metadata
registry: WordlistRegistry = {
    # Historical and Fundamental Lists
    WordlistId.SWADESH_100.value: {
        "id": WordlistId.SWADESH_100,
        "name": "Swadesh 100 Word List",
        "description": "Core vocabulary list used in comparative linguistics",
        "count": 100,
        "source": "Morris Swadesh",
        "year": 1952,
        "url": "https://en.wikipedia.org/wiki/Swadesh_list",
    },
    WordlistId.BASIC_ENGLISH.value: {
        "id": WordlistId.BASIC_ENGLISH,
        "name": "Basic English",
        "description": "Simplified subset of the English language with 850 words",
        "count": 850,
        "source": "Charles Kay Ogden",
        "year": 1930,
        "url": "https://en.wikipedia.org/wiki/Basic_English",
    },
    
    # Common English Lists
    WordlistId.DOLCH.value: {
        "id": WordlistId.DOLCH,
        "name": "Dolch Sight Words",
        "description": "220 most common words that readers should recognize on sight",
        "count": 220,
        "source": "Edward William Dolch",
        "year": 1936,
        "url": "https://en.wikipedia.org/wiki/Dolch_word_list",
    },
    WordlistId.FRY_1000.value: {
        "id": WordlistId.FRY_1000,
        "name": "Fry's 1000 Instant Words",
        "description": "Most frequently used English words in reading",
        "count": 1000,
        "source": "Edward Fry",
        "year": 1980,
    },
    
    # Grammatical Parts of Speech
    WordlistId.PREPOSITIONS.value: {
        "id": WordlistId.PREPOSITIONS,
        "name": "English Prepositions",
        "description": "Common English prepositions",
        "count": 70,
    },
    WordlistId.ARTICLES.value: {
        "id": WordlistId.ARTICLES,
        "name": "English Articles",
        "description": "Definite and indefinite articles in English",
        "count": 3,
    },
    WordlistId.CONJUNCTIONS.value: {
        "id": WordlistId.CONJUNCTIONS,
        "name": "English Conjunctions",
        "description": "Coordinating and subordinating conjunctions",
        "count": 25,
    },
    WordlistId.PRONOUNS.value: {
        "id": WordlistId.PRONOUNS,
        "name": "English Pronouns",
        "description": "Personal, possessive, relative, and demonstrative pronouns",
        "count": 35,
    },
    WordlistId.AUXILIARY_VERBS.value: {
        "id": WordlistId.AUXILIARY_VERBS,
        "name": "English Auxiliary Verbs",
        "description": "Helping verbs that support main verbs",
        "count": 25,
    },
    
    # Stop Words
    WordlistId.STOP_WORDS_NLTK.value: {
        "id": WordlistId.STOP_WORDS_NLTK,
        "name": "NLTK Stop Words",
        "description": "Stop words from the Natural Language Toolkit",
        "count": 179,
        "source": "NLTK",
        "url": "https://www.nltk.org/",
    },
    WordlistId.STOP_WORDS_SPACY.value: {
        "id": WordlistId.STOP_WORDS_SPACY,
        "name": "spaCy Stop Words",
        "description": "Stop words from the spaCy NLP library",
        "count": 326,
        "source": "spaCy",
        "url": "https://spacy.io/",
    },
    WordlistId.STOP_WORDS_SMART.value: {
        "id": WordlistId.STOP_WORDS_SMART,
        "name": "SMART Stop Words",
        "description": "Stop words from the SMART Information Retrieval System",
        "count": 571,
        "source": "SMART",
        "year": 1971,
    },
    WordlistId.STOP_WORDS_MINIMAL.value: {
        "id": WordlistId.STOP_WORDS_MINIMAL,
        "name": "Minimal Stop Words",
        "description": "A minimal set of English stop words",
        "count": 35,
    },
}

def get_list_metadata(id: str) -> Optional[WordlistMeta]:
    """Get metadata for a specific wordlist."""
    return registry.get(id)

def get_available_list_ids() -> List[str]:
    """Get IDs of all available wordlists."""
    return list(registry.keys())

def get_all_list_metadata() -> List[WordlistMeta]:
    """Get all wordlist metadata."""
    return list(registry.values()) 