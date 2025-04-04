import json
import os
import subprocess
import sys

def setup_package(package_name):
    """Install a package if not already installed"""
    try:
        __import__(package_name)
    except ImportError:
        print(f"Installing {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

def save_stop_words(words, source_name, description, version=None, output_dir='data/wordlists/stop_words'):
    """Save stop words to a JSON file"""
    os.makedirs(output_dir, exist_ok=True)
    
    data = {
        "type": "stop_words",
        "source": source_name,
        "description": description,
        "words": sorted(list(words)),
        "total_words": len(words)
    }
    
    if version:
        data["version"] = version
    
    filepath = os.path.join(output_dir, f'{source_name}_stop_words.json')
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
    
    print(f"Created {source_name} stop words file with {len(words)} words") 