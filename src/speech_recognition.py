# Updated speech_recognition.py
import speech_recognition as sr
from . import config
from .audio_file_handler import AudioFileHandler

class SpeechHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.audio_handler = AudioFileHandler()
    
    def process_audio_file(self, file_path):
        """Process a single audio file and return its transcription."""
        try:
            # Convert to WAV if needed
            wav_file = self.audio_handler.convert_to_wav(file_path)
            
            # Transcribe
            transcription = self.transcribe_file(wav_file)
            
            # Save transcription
            transcript_file = self.save_transcription(transcription, wav_file)
            
            return {
                'original_file': file_path,
                'wav_file': wav_file,
                'transcription': transcription,
                'transcript_file': transcript_file
            }
            
        except Exception as e:
            return {
                'original_file': file_path,
                'error': str(e)
            }
    
    def process_directory(self, directory_path):
        """Process all supported audio files in a directory."""
        results = []
        
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                if self.audio_handler.is_supported_format(file_path):
                    result = self.process_audio_file(file_path)
                    results.append(result)
        
        return results

def process_single_file():
    handler = SpeechHandler()
    
    # Replace with your audio file path
    file_path = "file.mp3"
    
    result = handler.process_audio_file(file_path)
    
    if 'error' in result:
        print(f"Error processing file: {result['error']}")
    else:
        print(f"Original file: {result['original_file']}")
        print(f"Transcription: {result['transcription']}")
        print(f"Transcript saved to: {result['transcript_file']}")

def process_directory():
    handler = SpeechHandler()
    
    # Replace with your directory path containing audio files
    directory_path = "files"
    
    results = handler.process_directory(directory_path)
    
    for result in results:
        if 'error' in result:
            print(f"Error processing {result['original_file']}: {result['error']}")
        else:
            print(f"\nProcessed: {result['original_file']}")
            print(f"Transcription: {result['transcription']}")
            print(f"Transcript saved to: {result['transcript_file']}")

if __name__ == "__main__":
    # Test single file
    print("Processing single file:")
    process_single_file()
    
    # Test directory
    print("\nProcessing directory:")
    process_directory()