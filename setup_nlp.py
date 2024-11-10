import nltk
from textblob import download_corpora

def setup_nltk_and_textblob():
    """Download required NLTK data and TextBlob corpora."""
    print("Downloading NLTK data...")
    nltk_packages = ['punkt', 'averaged_perceptron_tagger', 'stopwords']
    
    for package in nltk_packages:
        print(f"Downloading {package}...")
        nltk.download(package)
    
    print("\nDownloading TextBlob corpora...")
    download_corpora()
    
    print("\nSetup complete!")

if __name__ == "__main__":
    setup_nltk_and_textblob()