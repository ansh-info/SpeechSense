import nltk
import subprocess
import sys
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

import nltk

def setup_nltk_and_textblob():
    """Download required NLTK data and TextBlob corpora."""
    print("Downloading NLTK data...")
    nltk_packages = ['punkt', 'averaged_perceptron_tagger', 'stopwords']
    
    for package in nltk_packages:
        print(f"Downloading {package}...")
        nltk.download(package)
    
    print("\nDownloading TextBlob corpora...")
    try:
        subprocess.check_call([sys.executable, '-m', 'textblob.download_corpora'])
        print("TextBlob corpora downloaded successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading TextBlob corpora: {e}")
    
    print("\nSetup complete!")

if __name__ == "__main__":
    setup_nltk_and_textblob()