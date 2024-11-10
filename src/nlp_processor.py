from textblob import TextBlob
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import nltk
import os
from datetime import datetime

class NLPProcessor:
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
            nltk.download('averaged_perceptron_tagger')
            nltk.download('stopwords')
    
    def analyze_sentiment(self, text):
        """
        Analyze the sentiment of the text.
        Returns: polarity (-1 to 1) and subjectivity (0 to 1)
        """
        blob = TextBlob(text)
        return {
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity,
            'sentiment': 'positive' if blob.sentiment.polarity > 0 
                        else 'negative' if blob.sentiment.polarity < 0 
                        else 'neutral'
        }
    
    def generate_summary(self, text, sentences_count=3):
        """
        Generate a summary of the text using LSA (Latent Semantic Analysis).
        """
        try:
            # Initialize the summarizer
            parser = PlaintextParser.from_string(text, Tokenizer("english"))
            stemmer = Stemmer("english")
            summarizer = LsaSummarizer(stemmer)
            summarizer.stop_words = get_stop_words("english")

            # Summarize the text
            summary_sentences = summarizer(parser.document, sentences_count)
            summary = " ".join([str(sentence) for sentence in summary_sentences])
            
            return summary
        except Exception as e:
            return f"Could not generate summary: {str(e)}"
    
    def extract_topics(self, text, num_topics=3, num_words=5):
        """
        Extract main topics from the text using LDA.
        """
        try:
            # Create document-term matrix
            vectorizer = CountVectorizer(
                max_df=0.95,
                min_df=2,
                stop_words='english'
            )
            doc_term_matrix = vectorizer.fit_transform([text])
            
            # Create and fit LDA model
            lda_model = LatentDirichletAllocation(
                n_components=num_topics,
                random_state=42
            )
            lda_output = lda_model.fit_transform(doc_term_matrix)
            
            # Get feature names (words)
            feature_names = vectorizer.get_feature_names_out()
            
            # Extract top words for each topic
            topics = []
            for topic_idx, topic in enumerate(lda_model.components_):
                top_words = [feature_names[i] for i in topic.argsort()[:-num_words-1:-1]]
                topics.append({
                    'topic': f'Topic {topic_idx + 1}',
                    'words': top_words
                })
            
            return topics
        except Exception as e:
            return f"Could not extract topics: {str(e)}"
    
    def extract_key_phrases(self, text):
        """
        Extract key phrases using NLTK's part-of-speech tagging.
        """
        blob = TextBlob(text)
        phrases = []
        
        for sentence in blob.sentences:
            tagged_words = sentence.tags
            
            # Extract noun phrases
            current_phrase = []
            for word, tag in tagged_words:
                if tag.startswith(('JJ', 'NN')):  # Adjectives and Nouns
                    current_phrase.append(word)
                else:
                    if current_phrase:
                        phrases.append(' '.join(current_phrase))
                        current_phrase = []
                        
            if current_phrase:
                phrases.append(' '.join(current_phrase))
        
        return list(set(phrases))  # Remove duplicates

    def analyze_text(self, text, output_dir='data/analysis'):
        """
        Perform complete NLP analysis on the text.
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Perform analysis
        analysis = {
            'sentiment': self.analyze_sentiment(text),
            'summary': self.generate_summary(text),
            'topics': self.extract_topics(text),
            'key_phrases': self.extract_key_phrases(text)
        }
        
        # Save analysis to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f'analysis_{timestamp}.txt')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=== Text Analysis Report ===\n\n")
            
            # Write original text
            f.write("Original Text:\n")
            f.write(f"{text}\n\n")
            
            # Write sentiment analysis
            f.write("Sentiment Analysis:\n")
            f.write(f"Polarity: {analysis['sentiment']['polarity']}\n")
            f.write(f"Subjectivity: {analysis['sentiment']['subjectivity']}\n")
            f.write(f"Overall Sentiment: {analysis['sentiment']['sentiment']}\n\n")
            
            # Write summary
            f.write("Summary:\n")
            f.write(f"{analysis['summary']}\n\n")
            
            # Write topics
            f.write("Main Topics:\n")
            for topic in analysis['topics']:
                if isinstance(topic, dict):
                    f.write(f"{topic['topic']}: {', '.join(topic['words'])}\n")
            f.write("\n")
            
            # Write key phrases
            f.write("Key Phrases:\n")
            f.write(", ".join(analysis['key_phrases']))
        
        return analysis, output_file

def analyze_transcription(transcription_file):
    """
    Analyze a transcription file using NLP techniques.
    """
    # Read the transcription
    with open(transcription_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Initialize NLP processor
    nlp = NLPProcessor()
    
    # Analyze the text
    analysis, output_file = nlp.analyze_text(text)
    
    print("\nAnalysis Results:")
    print(f"Sentiment: {analysis['sentiment']['sentiment']}")
    print(f"Polarity: {analysis['sentiment']['polarity']:.2f}")
    print(f"Subjectivity: {analysis['sentiment']['subjectivity']:.2f}")
    print(f"\nSummary:\n{analysis['summary']}")
    print("\nTopics:")
    for topic in analysis['topics']:
        if isinstance(topic, dict):
            print(f"{topic['topic']}: {', '.join(topic['words'])}")
    print("\nKey Phrases:", ", ".join(analysis['key_phrases']))
    print(f"\nDetailed analysis saved to: {output_file}")
    
    return analysis, output_file