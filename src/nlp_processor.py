import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import os
from datetime import datetime

class NLPProcessor:
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('vader_lexicon', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
        except Exception as e:
            print(f"Warning: Could not download some NLTK data: {e}")
        
        self.sia = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('english'))
    
    def analyze_sentiment(self, text):
        """Analyze the sentiment of the text using NLTK's VADER sentiment analyzer."""
        try:
            scores = self.sia.polarity_scores(text)
            
            # Determine overall sentiment
            compound = scores['compound']
            if compound >= 0.05:
                sentiment = 'positive'
            elif compound <= -0.05:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
                
            return {
                'sentiment': sentiment,
                'polarity': compound,
                'subjectivity': abs(compound),
                'scores': scores
            }
        except Exception as e:
            return {
                'sentiment': 'neutral',
                'polarity': 0.0,
                'subjectivity': 0.0,
                'scores': {'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0},
                'error': str(e)
            }
    
    def generate_summary(self, text, num_sentences=3):
        """Generate a summary using sentence scoring based on word frequency."""
        try:
            # Tokenize the text into sentences using nltk's sent_tokenize
            sentences = [sent.strip() for sent in text.split('.') if sent.strip()]
            
            # If text is short, return it as is
            if len(sentences) <= num_sentences:
                return text
            
            # Tokenize words and remove stopwords
            words = word_tokenize(text.lower())
            word_freq = {}
            
            for word in words:
                if word.isalnum() and word not in self.stop_words:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Score sentences based on word frequency
            sentence_scores = {}
            for sentence in sentences:
                score = sum(word_freq.get(word.lower(), 0) 
                          for word in word_tokenize(sentence)
                          if word.lower() in word_freq)
                sentence_scores[sentence] = score
            
            # Get top sentences
            summary_sentences = sorted(sentence_scores.items(), 
                                    key=lambda x: x[1], 
                                    reverse=True)[:num_sentences]
            
            # Sort sentences by their original order
            summary_sentences.sort(key=lambda x: sentences.index(x[0]))
            
            return '. '.join(sent for sent, _ in summary_sentences) + '.'
            
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def extract_topics(self, text, num_topics=3, num_words=5):
        """Extract main topics using LDA."""
        try:
            # Create document-term matrix
            vectorizer = CountVectorizer(
                max_df=0.95,
                min_df=1,
                stop_words='english'
            )
            doc_term_matrix = vectorizer.fit_transform([text])
            
            # Create and fit LDA model
            lda_model = LatentDirichletAllocation(
                n_components=min(num_topics, len(text.split())),
                random_state=42
            )
            lda_output = lda_model.fit_transform(doc_term_matrix)
            
            # Get feature names
            feature_names = vectorizer.get_feature_names_out()
            
            # Extract top words for each topic
            topics = []
            for topic_idx, topic in enumerate(lda_model.components_):
                top_words_idx = topic.argsort()[:-num_words-1:-1]
                top_words = [feature_names[i] for i in top_words_idx]
                topics.append({
                    'topic': f'Topic {topic_idx + 1}',
                    'words': top_words
                })
            
            return topics
        except Exception as e:
            return [{'topic': 'Error', 'words': [str(e)]}]
    
    def extract_key_phrases(self, text):
        """Extract key phrases using frequency-based approach."""
        try:
            # Split text into words
            words = text.lower().split()
            
            # Remove stopwords and non-alphanumeric words
            words = [word for word in words 
                    if word.isalnum() and word not in self.stop_words]
            
            # Get word frequency
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get top words as key phrases
            key_words = sorted(word_freq.items(), 
                             key=lambda x: x[1], 
                             reverse=True)[:10]
            
            return [word for word, _ in key_words]
            
        except Exception as e:
            return [f"Error extracting key phrases: {str(e)}"]

    def analyze_text(self, text, output_dir='data/analysis'):
        """Perform complete NLP analysis on the text."""
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
            f.write(f"Original Text:\n{text}\n\n")
            f.write(f"Sentiment Analysis:\n")
            f.write(f"Overall Sentiment: {analysis['sentiment']['sentiment']}\n")
            f.write(f"Polarity: {analysis['sentiment']['polarity']}\n")
            f.write(f"Detailed Scores: {analysis['sentiment']['scores']}\n\n")
            f.write(f"Summary:\n{analysis['summary']}\n\n")
            f.write("Main Topics:\n")
            for topic in analysis['topics']:
                f.write(f"{topic['topic']}: {', '.join(topic['words'])}\n")
            f.write("\nKey Phrases:\n")
            f.write(", ".join(analysis['key_phrases']))
        
        return analysis, output_file

def analyze_transcription(transcription_file):
    """Analyze a transcription file using NLP techniques."""
    try:
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
        print(f"\nSummary:\n{analysis['summary']}")
        print("\nTopics:")
        for topic in analysis['topics']:
            if isinstance(topic, dict):
                print(f"{topic['topic']}: {', '.join(topic['words'])}")
        print("\nKey Phrases:", ", ".join(analysis['key_phrases']))
        print(f"\nDetailed analysis saved to: {output_file}")
        
        return analysis, output_file
        
    except Exception as e:
        print(f"Error analyzing transcription: {e}")
        return None, None