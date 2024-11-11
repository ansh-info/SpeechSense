import os
import time
from src.speech_recognition import SpeechHandler
from src.nlp_processor import analyze_transcription
from src.realtime_transcription import RealtimeTranscriber

def test_file_transcription():
    """Test transcription of audio files"""
    print("\n=== Testing File Transcription ===")
    handler = SpeechHandler()
    
    # Test with sample audio file
    test_file = "data/raw/test_audio.mp3"  # Replace with your test file
    if os.path.exists(test_file):
        result = handler.process_audio_file(test_file)
        if result['success']:
            print(f"Transcription successful:\n{result['transcription']}")
        else:
            print(f"Transcription failed: {result['error']}")
    else:
        print(f"Please place a test audio file at: {test_file}")

def test_nlp_analysis():
    """Test NLP analysis on a sample text"""
    print("\n=== Testing NLP Analysis ===")
    
    # Sample text for testing
    test_text = """
    This is a test transcript. It contains multiple sentences for analysis.
    We need to ensure that all NLP features are working correctly.
    The sentiment should be positive, and we should see relevant topics.
    """
    
    # Save test text to file
    test_file = "data/transcriptions/test_transcript.txt"
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    with open(test_file, 'w') as f:
        f.write(test_text)
    
    # Perform analysis
    analysis, output_file = analyze_transcription(test_file)
    
    # Print results
    print("\nAnalysis Results:")
    print(f"Sentiment: {analysis['sentiment']['sentiment']}")
    print(f"Summary: {analysis['summary']}")
    print("Topics:", [topic['words'] for topic in analysis['topics'] if isinstance(topic, dict)])
    print(f"Key Phrases: {analysis['key_phrases']}")

def test_realtime():
    """Test real-time transcription"""
    print("\n=== Testing Real-time Transcription ===")
    print("Recording for 10 seconds...")
    
    transcriber = RealtimeTranscriber(analysis_interval=5)
    transcriber.start_recording()
    
    try:
        time.sleep(10)
    finally:
        analysis = transcriber.stop_recording()
        if analysis:
            print("\nReal-time Analysis Results:")
            print(f"Sentiment: {analysis['sentiment']['sentiment']}")
            print(f"Summary: {analysis['summary']}")

def main():
    """Run all tests"""
    print("Starting comprehensive testing...")
    
    # Run each test
    try:
        test_file_transcription()
    except Exception as e:
        print(f"File transcription test failed: {e}")
    
    try:
        test_nlp_analysis()
    except Exception as e:
        print(f"NLP analysis test failed: {e}")
    
    try:
        test_realtime()
    except Exception as e:
        print(f"Real-time transcription test failed: {e}")
    
    print("\nTesting complete!")

if __name__ == "__main__":
    main()