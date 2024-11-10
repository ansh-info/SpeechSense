import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

def download_nltk_data():
    """Download all required NLTK data"""
    resources = [
        'punkt',
        'vader_lexicon',
        'stopwords',
        'averaged_perceptron_tagger'
    ]
    
    for resource in resources:
        print(f"Downloading {resource}...")
        try:
            nltk.download(resource)
            print(f"Successfully downloaded {resource}")
        except Exception as e:
            print(f"Error downloading {resource}: {e}")

if __name__ == "__main__":
    print("Starting NLTK data download...")
    download_nltk_data()
    print("Download complete!")