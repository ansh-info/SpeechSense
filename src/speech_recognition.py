import speech_recognition as sr
import pyaudio
import wave
import os
from datetime import datetime
from . import config

class SpeechHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
    def record_audio(self, duration=None):
        """Record audio from microphone."""
        if duration is None:
            duration = config.RECORD_SECONDS
            
        # Initialize PyAudio
        audio = pyaudio.PyAudio()
        
        # Open stream
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=config.CHANNELS,
            rate=config.SAMPLE_RATE,
            input=True,
            frames_per_buffer=config.CHUNK_SIZE
        )
        
        print("Recording...")
        frames = []
        
        for _ in range(0, int(config.SAMPLE_RATE / config.CHUNK_SIZE * duration)):
            data = stream.read(config.CHUNK_SIZE)
            frames.append(data)
            
        print("Recording finished.")
        
        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        # Save the recorded audio
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(config.RAW_DATA_DIR, f"recording_{timestamp}.wav")
        
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(config.CHANNELS)
            wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(config.SAMPLE_RATE)
            wf.writeframes(b''.join(frames))
            
        return filename
    
    def transcribe_file(self, audio_file_path):
        """Transcribe audio file using Google's Speech Recognition."""
        try:
            with sr.AudioFile(audio_file_path) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data)
                return text
        except sr.UnknownValueError:
            return "Speech recognition could not understand the audio"
        except sr.RequestError as e:
            return f"Could not request results from service; {str(e)}"
    
    def save_transcription(self, text, original_filename):
        """Save transcribed text to file."""
        basename = os.path.splitext(os.path.basename(original_filename))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = os.path.join(
            config.TRANSCRIPTIONS_DIR,
            f"{basename}_transcript_{timestamp}.txt"
        )
        
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(text)
        return output_filename

# Create a test script: test_speech_recognition.py
def main():
    # Initialize the speech handler
    speech_handler = SpeechHandler()
    
    # Record audio
    print("Starting audio recording...")
    audio_file = speech_handler.record_audio(duration=5)  # 5 seconds recording
    print(f"Audio saved to: {audio_file}")
    
    # Transcribe the recorded audio
    print("Transcribing audio...")
    transcription = speech_handler.transcribe_file(audio_file)
    print(f"Transcription: {transcription}")
    
    # Save transcription
    transcript_file = speech_handler.save_transcription(transcription, audio_file)
    print(f"Transcription saved to: {transcript_file}")

if __name__ == "__main__":
    main()