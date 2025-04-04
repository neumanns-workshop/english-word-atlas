import csv
import json
from pathlib import Path

def convert_ngsl_to_json():
    # Input and output paths
    input_file = Path("NGSL_1.2_stats.csv")
    output_file = Path("data/wordlists/historical/ngsl.json")
    
    # Create output directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    wordlist_data = {
        "words": []
    }
    
    # Read CSV and extract just the words
    with open(input_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            wordlist_data["words"].append(row["Lemma"])
    
    # Write JSON output
    with open(output_file, 'w', encoding='utf-8') as jsonfile:
        json.dump(wordlist_data, jsonfile, indent=2)
        
if __name__ == "__main__":
    convert_ngsl_to_json() 