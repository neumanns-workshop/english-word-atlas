"""
Coverage Analysis - Compare wordlist coverage against SUBTLEX-US frequency data

This script analyzes how different wordlists cover the most frequent words
in American English according to the SUBTLEX-US corpus.
"""

import os
from pathlib import Path
from collections import defaultdict
import matplotlib.pyplot as plt
from word_atlas import WordAtlas

def load_subtlex_us(filepath):
    """Load the SUBTLEX-US frequency list.
    
    Args:
        filepath: Path to the SUBTLEX-US file
        
    Returns:
        Dictionary mapping words to their frequency rank
    """
    print(f"Loading SUBTLEX-US data from {filepath}...")
    subtlex_words = {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        # Skip header
        next(f)
        
        # Parse each line
        for i, line in enumerate(f, 1):
            parts = line.strip().split()
            if len(parts) >= 2:
                word = parts[0].lower()
                # Use the FREQcount as frequency metric
                freq = float(parts[1]) if len(parts) > 1 else 0
                subtlex_words[word] = {'rank': i, 'freq': freq}
    
    print(f"Loaded {len(subtlex_words)} words from SUBTLEX-US")
    return subtlex_words

def analyze_coverage(wordlist, subtlex_data, top_n_values):
    """Analyze wordlist coverage against SUBTLEX-US.
    
    Args:
        wordlist: Set of words to analyze
        subtlex_data: Dictionary mapping words to frequency data
        top_n_values: List of N values to analyze coverage for (e.g., [100, 1000, 5000])
        
    Returns:
        Dictionary with coverage statistics
    """
    # Convert wordlist to lowercase for comparison
    wordlist_lower = {w.lower() for w in wordlist}
    
    # Sort SUBTLEX words by rank
    subtlex_sorted = sorted(
        [(word, data['rank'], data['freq']) for word, data in subtlex_data.items()],
        key=lambda x: x[1]  # Sort by rank
    )
    
    # Analyze coverage for different top-N values
    coverage_stats = {}
    for n in top_n_values:
        if n > len(subtlex_sorted):
            continue
            
        top_n_words = {word for word, _, _ in subtlex_sorted[:n]}
        intersection = wordlist_lower.intersection(top_n_words)
        
        coverage_stats[n] = {
            'wordlist_size': len(wordlist),
            'subtlex_size': n,
            'overlap': len(intersection),
            'coverage_pct': round(len(intersection) / n * 100, 2),
            'inclusion_pct': round(len(intersection) / len(wordlist) * 100, 2) if wordlist else 0
        }
    
    return coverage_stats

def calculate_cumulative_coverage(wordlist, subtlex_data, max_n=10000, step=1000):
    """Calculate cumulative coverage of a wordlist against SUBTLEX-US.
    
    Args:
        wordlist: Set of words to analyze
        subtlex_data: Dictionary mapping words to frequency data
        max_n: Maximum top-N value to analyze
        step: Step size for N values
        
    Returns:
        Tuple of (n_values, coverage_values)
    """
    # Convert wordlist to lowercase for comparison
    wordlist_lower = {w.lower() for w in wordlist}
    
    # Sort SUBTLEX words by rank
    subtlex_sorted = sorted(
        [(word, data['rank'], data['freq']) for word, data in subtlex_data.items()],
        key=lambda x: x[1]  # Sort by rank
    )
    
    # Calculate coverage at different N values
    n_values = list(range(step, min(max_n, len(subtlex_sorted)) + 1, step))
    coverage_values = []
    
    for n in n_values:
        top_n_words = {word for word, _, _ in subtlex_sorted[:n]}
        intersection = wordlist_lower.intersection(top_n_words)
        coverage_pct = len(intersection) / n * 100
        coverage_values.append(coverage_pct)
    
    return n_values, coverage_values

def main():
    """Main function for analyzing wordlist coverage."""
    # Initialize the WordAtlas
    print("Loading the English Word Atlas...")
    atlas = WordAtlas()
    
    # Load SUBTLEX-US data
    subtlex_path = Path("../data/frequencies/subtlex_us.txt")
    if not subtlex_path.exists():
        print(f"SUBTLEX-US file not found at {subtlex_path}")
        print("Checking current directory...")
        subtlex_path = Path("./data/frequencies/subtlex_us.txt")
        if not subtlex_path.exists():
            print(f"SUBTLEX-US file not found at {subtlex_path}")
            print("Checking absolute path...")
            subtlex_path = Path("/Users/jneumann/Repos/wordlists/data/frequencies/subtlex_us.txt")
            if not subtlex_path.exists():
                print(f"ERROR: SUBTLEX-US file not found at any location")
                return
    
    subtlex_data = load_subtlex_us(subtlex_path)
    
    # Define wordlists to analyze
    wordlists = {
        # Core wordlists
        "GSL_ORIGINAL": atlas.filter_by_attribute("GSL_ORIGINAL"),
        "GSL_NEW": atlas.filter_by_attribute("GSL_NEW"),
        "SWADESH_CORE": atlas.filter_by_attribute("SWADESH_CORE"),
        "SWADESH_EXTENDED": atlas.filter_by_attribute("SWADESH_EXTENDED"),
        
        # Ogden Basic English categories
        "OGDEN_BASIC_ACTION": atlas.filter_by_attribute("OGDEN_BASIC_ACTION"),
        "OGDEN_BASIC_CONCEPT": atlas.filter_by_attribute("OGDEN_BASIC_CONCEPT"),
        "OGDEN_BASIC_CONCRETE": atlas.filter_by_attribute("OGDEN_BASIC_CONCRETE"),
        "OGDEN_BASIC_CONTRAST": atlas.filter_by_attribute("OGDEN_BASIC_CONTRAST"),
        "OGDEN_BASIC_QUALITY": atlas.filter_by_attribute("OGDEN_BASIC_QUALITY"),
        
        # Ogden Field-specific categories
        "OGDEN_FIELD_ANIMAL": atlas.filter_by_attribute("OGDEN_FIELD_ANIMAL"),
        "OGDEN_FIELD_BIZ": atlas.filter_by_attribute("OGDEN_FIELD_BIZ"),
        "OGDEN_FIELD_BODY": atlas.filter_by_attribute("OGDEN_FIELD_BODY"),
        "OGDEN_FIELD_BUILD": atlas.filter_by_attribute("OGDEN_FIELD_BUILD"),
        "OGDEN_FIELD_CLOTH": atlas.filter_by_attribute("OGDEN_FIELD_CLOTH"),
        "OGDEN_FIELD_COLOR": atlas.filter_by_attribute("OGDEN_FIELD_COLOR"),
        "OGDEN_FIELD_DIR": atlas.filter_by_attribute("OGDEN_FIELD_DIR"),
        "OGDEN_FIELD_EDU": atlas.filter_by_attribute("OGDEN_FIELD_EDU"),
        "OGDEN_FIELD_FARM": atlas.filter_by_attribute("OGDEN_FIELD_FARM"),
        "OGDEN_FIELD_FOOD": atlas.filter_by_attribute("OGDEN_FIELD_FOOD"),
        "OGDEN_FIELD_HOME": atlas.filter_by_attribute("OGDEN_FIELD_HOME"),
        "OGDEN_FIELD_MATH": atlas.filter_by_attribute("OGDEN_FIELD_MATH"),
        "OGDEN_FIELD_MATTER": atlas.filter_by_attribute("OGDEN_FIELD_MATTER"),
        "OGDEN_FIELD_MOVE": atlas.filter_by_attribute("OGDEN_FIELD_MOVE"),
        "OGDEN_FIELD_PERSON": atlas.filter_by_attribute("OGDEN_FIELD_PERSON"),
        "OGDEN_FIELD_POLITIC": atlas.filter_by_attribute("OGDEN_FIELD_POLITIC"),
        "OGDEN_FIELD_TIME": atlas.filter_by_attribute("OGDEN_FIELD_TIME"),
        "OGDEN_FIELD_TOOL": atlas.filter_by_attribute("OGDEN_FIELD_TOOL"),
        "OGDEN_FIELD_WAR": atlas.filter_by_attribute("OGDEN_FIELD_WAR"),
        
        # Ogden Supplementary lists
        "OGDEN_SUPP_ADD": atlas.filter_by_attribute("OGDEN_SUPP_ADD"),
        "OGDEN_SUPP_BIO": atlas.filter_by_attribute("OGDEN_SUPP_BIO"),
        "OGDEN_SUPP_CERT": atlas.filter_by_attribute("OGDEN_SUPP_CERT"),
        "OGDEN_SUPP_EXTRA": atlas.filter_by_attribute("OGDEN_SUPP_EXTRA"),
        "OGDEN_SUPP_GEO": atlas.filter_by_attribute("OGDEN_SUPP_GEO"),
        "OGDEN_SUPP_INTL": atlas.filter_by_attribute("OGDEN_SUPP_INTL"),
        "OGDEN_SUPP_ISCI": atlas.filter_by_attribute("OGDEN_SUPP_ISCI"),
        "OGDEN_SUPP_MATH": atlas.filter_by_attribute("OGDEN_SUPP_MATH"),
        "OGDEN_SUPP_MODERN": atlas.filter_by_attribute("OGDEN_SUPP_MODERN"),
        "OGDEN_SUPP_PHYSCHEM": atlas.filter_by_attribute("OGDEN_SUPP_PHYSCHEM"),
        "OGDEN_SUPP_QUANT": atlas.filter_by_attribute("OGDEN_SUPP_QUANT"),
        "OGDEN_SUPP_RADIO": atlas.filter_by_attribute("OGDEN_SUPP_RADIO"),
        "OGDEN_SUPP_SCI": atlas.filter_by_attribute("OGDEN_SUPP_SCI"),
        "OGDEN_SUPP_SCIENCES": atlas.filter_by_attribute("OGDEN_SUPP_SCIENCES"),
        "OGDEN_SUPP_SOCIAL": atlas.filter_by_attribute("OGDEN_SUPP_SOCIAL"),
        "OGDEN_SUPP_SOUND": atlas.filter_by_attribute("OGDEN_SUPP_SOUND"),
        "OGDEN_SUPP_TITLE": atlas.filter_by_attribute("OGDEN_SUPP_TITLE"),
        "OGDEN_SUPP_TRADE": atlas.filter_by_attribute("OGDEN_SUPP_TRADE"),
        "OGDEN_SUPP_UNCERT": atlas.filter_by_attribute("OGDEN_SUPP_UNCERT"),
        "OGDEN_SUPP_UTIL": atlas.filter_by_attribute("OGDEN_SUPP_UTIL"),
        
        # Roget Categories (all)
        "ROGET_ABSTRACT": atlas.filter_by_attribute("ROGET_ABSTRACT"),
        "ROGET_AUTHORITY": atlas.filter_by_attribute("ROGET_AUTHORITY"),
        "ROGET_CAUSATION": atlas.filter_by_attribute("ROGET_CAUSATION"),
        "ROGET_CHANGE": atlas.filter_by_attribute("ROGET_CHANGE"),
        "ROGET_COMMERCE": atlas.filter_by_attribute("ROGET_COMMERCE"),
        "ROGET_COMMUNICATION": atlas.filter_by_attribute("ROGET_COMMUNICATION"),
        "ROGET_CONFLICT": atlas.filter_by_attribute("ROGET_CONFLICT"),
        "ROGET_DIMENSION": atlas.filter_by_attribute("ROGET_DIMENSION"),
        "ROGET_EFFORT": atlas.filter_by_attribute("ROGET_EFFORT"),
        "ROGET_EMOTION": atlas.filter_by_attribute("ROGET_EMOTION"),
        "ROGET_EXISTENCE": atlas.filter_by_attribute("ROGET_EXISTENCE"),
        "ROGET_INTERSOCIAL": atlas.filter_by_attribute("ROGET_INTERSOCIAL"),
        "ROGET_KNOWLEDGE": atlas.filter_by_attribute("ROGET_KNOWLEDGE"),
        "ROGET_LOCATION": atlas.filter_by_attribute("ROGET_LOCATION"),
        "ROGET_MATTER": atlas.filter_by_attribute("ROGET_MATTER"),
        "ROGET_MEMORY": atlas.filter_by_attribute("ROGET_MEMORY"),
        "ROGET_MORALITY": atlas.filter_by_attribute("ROGET_MORALITY"),
        "ROGET_MOTION": atlas.filter_by_attribute("ROGET_MOTION"),
        "ROGET_NUMBERS": atlas.filter_by_attribute("ROGET_NUMBERS"),
        "ROGET_ORDER": atlas.filter_by_attribute("ROGET_ORDER"),
        "ROGET_PERCEPTION": atlas.filter_by_attribute("ROGET_PERCEPTION"),
        "ROGET_PHYSICAL": atlas.filter_by_attribute("ROGET_PHYSICAL"),
        "ROGET_POSITION": atlas.filter_by_attribute("ROGET_POSITION"),
        "ROGET_QUALITY": atlas.filter_by_attribute("ROGET_QUALITY"),
        "ROGET_QUANTITY": atlas.filter_by_attribute("ROGET_QUANTITY"),
        "ROGET_SAFETY": atlas.filter_by_attribute("ROGET_SAFETY"),
        "ROGET_SENSATION": atlas.filter_by_attribute("ROGET_SENSATION"),
        "ROGET_SENTIMENT": atlas.filter_by_attribute("ROGET_SENTIMENT"),
        "ROGET_SHAPE": atlas.filter_by_attribute("ROGET_SHAPE"),
        "ROGET_SIMILARITY": atlas.filter_by_attribute("ROGET_SIMILARITY"),
        "ROGET_TEMPORAL": atlas.filter_by_attribute("ROGET_TEMPORAL"),
        "ROGET_TIME": atlas.filter_by_attribute("ROGET_TIME"),
        "ROGET_VOLITION": atlas.filter_by_attribute("ROGET_VOLITION"),
        
        # Stopword lists (all)
        "STOP_FOX": atlas.filter_by_attribute("STOP_FOX"),
        "STOP_LEARN": atlas.filter_by_attribute("STOP_LEARN"),
        "STOP_NLTK": atlas.filter_by_attribute("STOP_NLTK"),
        "STOP_SPACY": atlas.filter_by_attribute("STOP_SPACY"),
        
        # Complete dataset
        "FULL_DATASET": set(atlas.get_all_words()),
    }
    
    # Define combined Ogden categories
    ogden_basic = set()
    for attr in ["OGDEN_BASIC_ACTION", "OGDEN_BASIC_CONCEPT", "OGDEN_BASIC_CONCRETE", 
                "OGDEN_BASIC_CONTRAST", "OGDEN_BASIC_QUALITY"]:
        ogden_basic = ogden_basic.union(wordlists[attr])
    wordlists["OGDEN_BASIC_ALL"] = ogden_basic
    
    # Combine all Ogden field-specific categories
    ogden_fields = set()
    ogden_field_attrs = [attr for attr in wordlists.keys() if attr.startswith("OGDEN_FIELD_")]
    for attr in ogden_field_attrs:
        ogden_fields = ogden_fields.union(wordlists[attr])
    wordlists["OGDEN_FIELDS_ALL"] = ogden_fields
    
    # Combine all Ogden supplementary categories
    ogden_supps = set()
    ogden_supp_attrs = [attr for attr in wordlists.keys() if attr.startswith("OGDEN_SUPP_")]
    for attr in ogden_supp_attrs:
        ogden_supps = ogden_supps.union(wordlists[attr])
    wordlists["OGDEN_SUPPS_ALL"] = ogden_supps
    
    # Add Ogden combined (complete Ogden wordlist)
    wordlists["OGDEN_COMBINED"] = ogden_basic.union(ogden_fields).union(ogden_supps)
    
    # Combine all Roget categories
    roget_all = set()
    roget_attrs = [attr for attr in wordlists.keys() if attr.startswith("ROGET_")]
    for attr in roget_attrs:
        roget_all = roget_all.union(wordlists[attr])
    wordlists["ROGET_ALL"] = roget_all
    
    # Combine all stopword lists
    stops_all = set()
    stop_attrs = [attr for attr in wordlists.keys() if attr.startswith("STOP_")]
    for attr in stop_attrs:
        stops_all = stops_all.union(wordlists[attr])
    wordlists["STOP_ALL"] = stops_all
    
    # Create overall union and intersection wordlists as baselines
    # Union of all wordlists (excluding FULL_DATASET and aggregate lists)
    all_union = set()
    
    # Get all base wordlists (excluding aggregates and FULL_DATASET)
    base_wordlists = [name for name in wordlists.keys() 
                     if not name in ["FULL_DATASET", "OGDEN_BASIC_ALL", "OGDEN_FIELDS_ALL", 
                                     "OGDEN_SUPPS_ALL", "OGDEN_COMBINED", "ROGET_ALL", "STOP_ALL",
                                     "ALL_UNION", "ALL_INTERSECTION"]]
    
    # Process union across all base wordlists
    for name in base_wordlists:
        all_union = all_union.union(wordlists[name])
    
    # For intersection, use only the major category groups
    major_categories = [
        "GSL_ORIGINAL",
        "GSL_NEW", 
        "OGDEN_COMBINED",
        "ROGET_ALL",
        "STOP_ALL",
        "SWADESH_EXTENDED"
    ]
    
    # Start with the first major category
    all_intersection = wordlists[major_categories[0]].copy()
    
    # Intersect with remaining major categories
    for name in major_categories[1:]:
        all_intersection = all_intersection.intersection(wordlists[name])
    
    wordlists["ALL_UNION"] = all_union
    wordlists["ALL_INTERSECTION"] = all_intersection
    
    # Analyze coverage for different top-N values
    top_n_values = [100, 500, 1000, 5000, 10000, 20000, 50000]
    
    print(f"\nAnalyzing wordlist coverage against SUBTLEX-US top-{top_n_values} words...")
    coverage_results = {}
    
    for name, wordlist in wordlists.items():
        coverage_results[name] = analyze_coverage(wordlist, subtlex_data, top_n_values)
    
    # Print results in a table format
    print("\nWordlist Coverage Analysis")
    print("=" * 100)
    print(f"{'Wordlist':<30} {'Size':<8} {'Top-100':<10} {'Top-1000':<10} {'Top-5000':<10} {'Top-10000':<10}")
    print("-" * 100)
    
    for name, results in coverage_results.items():
        size = results.get(1000, {}).get('wordlist_size', 0)
        top_100 = f"{results.get(100, {}).get('coverage_pct', 0)}%" if 100 in results else "N/A"
        top_1000 = f"{results.get(1000, {}).get('coverage_pct', 0)}%" if 1000 in results else "N/A"
        top_5000 = f"{results.get(5000, {}).get('coverage_pct', 0)}%" if 5000 in results else "N/A"
        top_10000 = f"{results.get(10000, {}).get('coverage_pct', 0)}%" if 10000 in results else "N/A"
        
        print(f"{name:<30} {size:<8} {top_100:<10} {top_1000:<10} {top_5000:<10} {top_10000:<10}")
    
    # Identify uncategorized words (in FULL_DATASET but not in ALL_UNION)
    uncategorized = wordlists["FULL_DATASET"] - wordlists["ALL_UNION"]
    print(f"\nUncategorized words: {len(uncategorized)}")
    if uncategorized:
        print(f"Sample of uncategorized words: {sorted(list(uncategorized))[:20]}")
        
        # Save all uncategorized words to a file
        with open('uncategorized_words.txt', 'w', encoding='utf-8') as f:
            f.write(f"# {len(uncategorized)} uncategorized words\n")
            for word in sorted(list(uncategorized)):
                f.write(f"{word}\n")
        print(f"Saved all {len(uncategorized)} uncategorized words to 'uncategorized_words.txt'")
        
        # Examine attributes of uncategorized words
        print("\nExamining attributes of uncategorized words:")
        sample_words = sorted(list(uncategorized))[:10]  # Take first 10 words
        
        for word in sample_words:
            word_attrs = atlas.word_data.get(word, {})
            # Filter out embeddings and other non-categorization attributes
            category_attrs = {k: v for k, v in word_attrs.items() 
                             if not k.startswith('EMBEDDINGS') and not k in ['ARPABET', 'SYLLABLE_COUNT', 'FREQ_GRADE', 'POS', 'FREQ_COUNT']}
            
            print(f"\n{word}: {category_attrs}")
    
    # Calculate cumulative coverage for selected wordlists
    selected_wordlists = [
        "GSL_ORIGINAL", 
        "GSL_NEW",
        "OGDEN_BASIC_ALL",
        "OGDEN_FIELDS_ALL",
        "OGDEN_SUPPS_ALL",
        "OGDEN_COMBINED",
        "ROGET_ALL",
        "STOP_ALL",
        "SWADESH_EXTENDED", 
        "SWADESH_CORE",
        "ALL_UNION",
        "ALL_INTERSECTION",
        "FULL_DATASET"
    ]
    selected_wordlists = [wl for wl in selected_wordlists if wl]
    
    plt.figure(figsize=(12, 8))
    
    for name in selected_wordlists:
        if name in wordlists:
            n_values, coverage_values = calculate_cumulative_coverage(
                wordlists[name], subtlex_data, max_n=10000
            )
            plt.plot(n_values, coverage_values, label=f"{name} ({len(wordlists[name])} words)")
    
    plt.xlabel('Top-N SUBTLEX-US Words')
    plt.ylabel('Coverage (%)')
    plt.title('Wordlist Coverage of Most Frequent English Words')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('wordlist_coverage.png')
    print("\nCoverage plot saved to 'wordlist_coverage.png'")
    
    # Save detailed coverage data to CSV
    with open('wordlist_coverage.csv', 'w', encoding='utf-8') as f:
        # Write header
        f.write("Wordlist,Size")
        for n in top_n_values:
            f.write(f",Top-{n} Coverage,Top-{n} Inclusion")
        f.write("\n")
        
        # Write data for each wordlist
        for name, results in coverage_results.items():
            size = results.get(top_n_values[0], {}).get('wordlist_size', 0)
            f.write(f"{name},{size}")
            
            for n in top_n_values:
                coverage = results.get(n, {}).get('coverage_pct', "")
                inclusion = results.get(n, {}).get('inclusion_pct', "")
                f.write(f",{coverage},{inclusion}")
            
            f.write("\n")
    
    print("Detailed coverage data saved to 'wordlist_coverage.csv'")

if __name__ == "__main__":
    main() 