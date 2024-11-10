import time
import signal
import sys
from src.realtime_transcription import RealtimeTranscriber
import speech_recognition as sr

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nGracefully shutting down...")
    sys.exit(0)

def list_microphones():
    """List all available microphones"""
    print("\nAvailable microphones:")
    mic_list = sr.Microphone.list_microphone_names()
    for i, microphone_name in enumerate(mic_list):
        print(f"{i}: {microphone_name}")
    return mic_list

def test_realtime_transcription():
    """
    Test the real-time transcription functionality.
    Press Ctrl+C to stop recording and exit.
    """
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # List available microphones
        mic_list = list_microphones()
        
        # Ask user to select microphone
        if len(mic_list) > 1:
            mic_index = int(input("\nSelect microphone index (0 to {}): ".format(len(mic_list)-1)))
        else:
            mic_index = 0
        
        print("\nInitializing transcriber...")
        print("Press Ctrl+C to stop recording")
        
        # Create transcriber instance with specific device index
        transcriber = RealtimeTranscriber(device_index=mic_index, analysis_interval=30)
        
        # Start recording
        transcriber.start_recording()
        
        # Keep the main thread alive
        while True:
            time.sleep(0.1)
            
    except ValueError as e:
        print(f"\nError with microphone selection: {e}")
    except sr.RequestError as e:
        print(f"\nCould not request results from speech recognition service: {e}")
    except KeyboardInterrupt:
        print("\nStopping recording...")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        try:
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
        except Exception as e:
            print(f"\nError during cleanup: {e}")

if __name__ == "__main__":
    test_realtime_transcription()