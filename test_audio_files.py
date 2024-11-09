# test_audio_files.py
from src.speech_recognition import SpeechHandler
import os
from datetime import datetime

def process_audio_file(file_path):
    handler = SpeechHandler()
    print(f"\nProcessing file: {file_path}")
    
    # Process the audio file
    result = handler.process_audio_file(file_path)
    
    if result['success']:
        # Get the transcription
        transcription = result['transcription']
        
        # Create filename for transcription
        base_filename = os.path.splitext(os.path.basename(file_path))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        transcript_filename = f"{base_filename}_transcript_{timestamp}.txt"
        
        # Ensure the transcriptions directory exists
        transcriptions_dir = 'data/transcriptions'
        os.makedirs(transcriptions_dir, exist_ok=True)
        
        # Save transcription to file
        transcript_path = os.path.join(transcriptions_dir, transcript_filename)
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(transcription)
        
        print(f"\nTranscription: {transcription}")
        print(f"Transcription saved to: {transcript_path}")
        return result
    else:
        print(f"\nError processing file: {result['error']}")
        return result

if __name__ == "__main__":
    # Process the audio file
    result = process_audio_file("data/raw/old-radio-227880.mp3")