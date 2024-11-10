import time
from src.realtime_transcription import RealtimeTranscriber
import keyboard  # for better control

def test_realtime_transcription():
    """
    Test the real-time transcription functionality.
    Press 'q' to stop recording and exit.
    """
    print("Starting real-time transcription test...")
    print("Press 'q' to stop recording and exit")
    
    # Create transcriber instance
    transcriber = RealtimeTranscriber(analysis_interval=30)  # Analysis every 30 seconds
    
    try:
        # Start recording
        transcriber.start_recording()
        
        # Wait for 'q' key press or maximum duration
        max_duration = 300  # 5 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_duration:
            if keyboard.is_pressed('q'):
                print("\nStopping recording...")
                break
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nRecording interrupted by user")
    except Exception as e:
        print(f"\nError during recording: {e}")
    finally:
        # Stop recording and get final analysis
        final_analysis = transcriber.stop_recording()
        
        # Print analysis results
        if final_analysis:
            print("\nFinal Analysis Results:")
            print(f"Sentiment: {final_analysis['sentiment']['sentiment']}")
            print(f"Polarity: {final_analysis['sentiment']['polarity']:.2f}")
            print(f"\nSummary:\n{final_analysis['summary']}")
            print("\nTopics:")
            for topic in final_analysis['topics']:
                if isinstance(topic, dict):
                    print(f"{topic['topic']}: {', '.join(topic['words'])}")
            print("\nKey Phrases:", ", ".join(final_analysis['key_phrases']))

if __name__ == "__main__":
    test_realtime_transcription()