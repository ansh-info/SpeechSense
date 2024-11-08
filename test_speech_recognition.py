from src.speech_recognition import SpeechHandler

# Create instance
handler = SpeechHandler()

# Test recording and transcription
audio_file = handler.record_audio(duration=5)  # Records for 5 seconds
transcription = handler.transcribe_file(audio_file)
print(f"Transcription: {transcription}")