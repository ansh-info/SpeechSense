import speech_recognition as sr
import os
from datetime import datetime
from . import config
from .audio_file_handler import AudioFileHandler

class SpeechHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.audio_handler = AudioFileHandler()
    
    def transcribe_file(self, audio_file_path):
        """Transcribe audio file using Google's Speech Recognition."""
        try:
            with sr.AudioFile(audio_file_path) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data)
                return {"success": True, "text": text}
        except sr.UnknownValueError:
            return {"success": False, "error": "Speech recognition could not understand the audio"}
        except sr.RequestError as e:
            return {"success": False, "error": f"Could not request results from service; {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

    def save_transcription(self, text, original_filename):
        """Save transcribed text to file."""
        try:
            basename = os.path.splitext(os.path.basename(original_filename))[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = os.path.join(
                config.TRANSCRIPTIONS_DIR,
                f"{basename}_transcript_{timestamp}.txt"
            )
            
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(text)
            return {"success": True, "file_path": output_filename}
        except Exception as e:
            return {"success": False, "error": f"Error saving transcription: {str(e)}"}

    def process_audio_file(self, file_path):
        """Process a single audio file and return its transcription."""
        try:
            print(f"\nProcessing file: {file_path}")
            
            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'original_file': file_path,
                    'error': 'File does not exist'
                }

            # Convert to WAV if needed
            print("Converting to WAV format...")
            wav_file = self.audio_handler.convert_to_wav(file_path)
            
            # Transcribe
            print("Transcribing audio...")
            transcription_result = self.transcribe_file(wav_file)
            
            if not transcription_result["success"]:
                return {
                    'success': False,
                    'original_file': file_path,
                    'error': transcription_result["error"]
                }
            
            # Save transcription
            save_result = self.save_transcription(transcription_result["text"], wav_file)
            
            if not save_result["success"]:
                return {
                    'success': False,
                    'original_file': file_path,
                    'error': save_result["error"]
                }
            
            return {
                'success': True,
                'original_file': file_path,
                'wav_file': wav_file,
                'transcription': transcription_result["text"],
                'transcript_file': save_result["file_path"]
            }
            
        except Exception as e:
            return {
                'success': False,
                'original_file': file_path,
                'error': str(e)
            }
    
    def process_directory(self, directory_path):
        """Process all supported audio files in a directory."""
        if not os.path.exists(directory_path):
            print(f"Error: Directory '{directory_path}' does not exist")
            return []

        results = []
        print(f"\nProcessing directory: {directory_path}")
        
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                if self.audio_handler.is_supported_format(file_path):
                    result = self.process_audio_file(file_path)
                    results.append(result)
        
        return results

def process_single_file(file_path):
    handler = SpeechHandler()
    print(f"\nProcessing file: {file_path}")
    
    result = handler.process_audio_file(file_path)
    
    if not result['success']:
        print(f"Error processing file: {result['error']}")
    else:
        print(f"Original file: {result['original_file']}")
        print(f"Transcription: {result['transcription']}")
        print(f"Transcript saved to: {result['transcript_file']}")
    
    return result

def process_directory(directory_path):
    handler = SpeechHandler()
    print(f"\nProcessing directory: {directory_path}")
    
    results = handler.process_directory(directory_path)
    
    print("\nProcessing Results:")
    for result in results:
        if not result['success']:
            print(f"\nError processing {result['original_file']}: {result['error']}")
        else:
            print(f"\nSuccessfully processed: {result['original_file']}")
            print(f"Transcription: {result['transcription']}")
            print(f"Transcript saved to: {result['transcript_file']}")
    
    return results

if __name__ == "__main__":
    # Test single file
    file_path = input("Enter the path to your audio file: ").strip('"')  # Strip quotes if present
    result = process_single_file(file_path)