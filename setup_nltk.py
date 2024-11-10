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
        'averaged_perceptron_tagger',
        'brown',  # Additional corpus for better summarization
        'wordnet'  # For better text processing
    ]
    
    print("Starting NLTK data download...")
    for resource in resources:
        print(f"Downloading {resource}...")
        try:
            nltk.download(resource, quiet=True)
            print(f"Successfully downloaded {resource}")
        except Exception as e:
            print(f"Error downloading {resource}: {e}")
    
    # Verify downloads
    try:
        from nltk.tokenize import sent_tokenize, word_tokenize
        from nltk.corpus import stopwords
        from nltk.sentiment.vader import SentimentIntensityAnalyzer
        print("\nTesting NLTK functionality...")
        # Test tokenization
        test_text = "This is a test sentence. This is another test sentence."
        sent_tokenize(test_text)
        word_tokenize(test_text)
        # Test stopwords
        stopwords.words('english')
        # Test sentiment analyzer
        sid = SentimentIntensityAnalyzer()
        print("All NLTK components are working correctly!")
    except Exception as e:
        print(f"Error testing NLTK functionality: {e}")

if __name__ == "__main__":
    print("Setting up NLTK resources...")
    download_nltk_data()