# Example usage for single file
from src.speech_recognition import SpeechHandler

handler = SpeechHandler()

# Process single file
result = handler.process_audio_file("path/to/your/audio.mp3")
print(f"Transcription: {result['transcription']}")

# # Process all audio files in a directory
# results = handler.process_directory("path/to/audio/files")
# for result in results:
#     if 'error' not in result:
#         print(f"File: {result['original_file']}")
#         print(f"Transcription: {result['transcription']}\n")