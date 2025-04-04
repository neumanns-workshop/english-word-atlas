"""
Wordlist Intersection Example - Find common words across different wordlists

This script demonstrates how to find the intersection between two wordlists
using the WordAtlas and WordlistBuilder classes.
"""

from word_atlas import WordAtlas, WordlistBuilder

def main():
    # Initialize the WordAtlas
    print("Loading the English Word Atlas...")
    atlas = WordAtlas()
    
    # Get the Swadesh extended wordlist
    print("\nRetrieving Swadesh extended wordlist...")
    swadesh_words = atlas.filter_by_attribute("SWADESH_EXTENDED")
    print(f"Swadesh extended list contains {len(swadesh_words)} words")
    print(f"Sample: {sorted(list(swadesh_words))[:10]}")
    
    # Get the GSL (General Service List) wordlist
    print("\nRetrieving GSL original wordlist...")
    gsl_words = atlas.filter_by_attribute("GSL_ORIGINAL")
    print(f"GSL original contains {len(gsl_words)} words")
    print(f"Sample: {sorted(list(gsl_words))[:10]}")
    
    # Find the intersection
    print("\nFinding intersection between Swadesh and GSL...")
    intersection = swadesh_words.intersection(gsl_words)
    print(f"Intersection contains {len(intersection)} words")
    
    # Print all words in the intersection
    if intersection:
        print("\nWords in both Swadesh extended and GSL original:")
        for word in sorted(intersection):
            print(f"  {word}")
    
    # Create a WordlistBuilder with the intersection
    print("\nCreating a WordlistBuilder with the intersection...")
    builder = WordlistBuilder(atlas)
    builder.add_words(list(intersection))
    
    # Set metadata for the intersection wordlist
    builder.set_metadata(
        name="Swadesh-GSL Intersection",
        description="Words that appear in both the Swadesh extended list and the GSL original",
        creator="Word Atlas Demo",
        tags=["intersection", "core vocabulary", "basic english"]
    )
    
    # Save the intersection wordlist
    output_file = "swadesh_gsl_intersection.json"
    builder.save(output_file)
    print(f"Intersection wordlist saved to {output_file}")
    
    # Export as text file
    text_file = "swadesh_gsl_intersection.txt"
    builder.export_text(text_file)
    print(f"Intersection wordlist exported as text to {text_file}")

if __name__ == "__main__":
    main() 