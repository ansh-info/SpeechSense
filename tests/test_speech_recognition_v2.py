import os
import sounddevice as sd
import soundfile as sf
import numpy as np
from datetime import datetime
from src.speech_recognition import SpeechHandler
from src import config

class SpeechTester:
    def __init__(self):
        self.handler = SpeechHandler()
        self.sample_rate = config.SAMPLE_RATE
        
    def record_audio(self, duration=5):
        """
        Record audio for specified duration.
        
        Args:
            duration (int): Duration in seconds to record
            
        Returns:
            str: Path to the recorded audio file
        """
        print(f"\nRecording for {duration} seconds...")
        
        # Record audio
        recording = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1
        )
        sd.wait()  # Wait until recording is finished
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.wav"
        filepath = os.path.join(config.RAW_DATA_DIR, filename)
        
        # Ensure directory exists
        os.makedirs(config.RAW_DATA_DIR, exist_ok=True)
        
        # Save the recording
        sf.write(filepath, recording, self.sample_rate)
        print(f"Recording saved to: {filepath}")
        
        return filepath

    def test_recording_and_transcription(self, duration=5):
        """
        Test recording and transcription pipeline.
        
        Args:
            duration (int): Duration in seconds to record
        """
        try:
            # Record audio
            audio_file = self.record_audio(duration)
            
            # Process the audio file
            print("\nTranscribing audio...")
            result = self.handler.process_audio_file(audio_file)
            
            if result['success']:
                print("\nTranscription Result:")
                print(result['transcription'])
                print(f"\nTranscript saved to: {result['transcript_file']}")
            else:
                print(f"\nError during transcription: {result['error']}")
                
            return result
            
        except Exception as e:
            print(f"\nError during testing: {e}")
            return None

def main():
    """Main test function"""
    print("Starting Speech Recognition Test")
    
    tester = SpeechTester()
    
    # Test recording and transcription
    print("\nTesting audio recording and transcription...")
    result = tester.test_recording_and_transcription(duration=5)
    
    if result and result['success']:
        print("\nTest completed successfully!")
    else:
        print("\nTest completed with errors.")

if __name__ == "__main__":
    main()