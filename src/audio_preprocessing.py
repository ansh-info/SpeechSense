import numpy as np
import librosa
import soundfile as sf
import os
from datetime import datetime
from . import config

class AudioPreprocessor:
    def __init__(self):
        self.sample_rate = config.SAMPLE_RATE
    
    def load_audio(self, file_path):
        """Load audio file and return signal array and sample rate."""
        audio_data, sr = librosa.load(file_path, sr=self.sample_rate)
        return audio_data, sr
    
    def reduce_noise(self, audio_data):
        """Basic noise reduction using librosa."""
        return librosa.effects.preemphasis(audio_data)
    
    def normalize_audio(self, audio_data):
        """Normalize audio to -1 to 1 range."""
        return librosa.util.normalize(audio_data)
    
    def process_audio(self, file_path):
        """Complete audio preprocessing pipeline."""
        # Load audio
        audio_data, sr = self.load_audio(file_path)
        
        # Apply preprocessing steps
        audio_data = self.reduce_noise(audio_data)
        audio_data = self.normalize_audio(audio_data)
        
        # Generate output filename
        filename = os.path.basename(file_path)
        output_path = os.path.join(
            config.PROCESSED_DATA_DIR,
            f'processed_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{filename}'
        )
        
        # Save processed audio
        sf.write(output_path, audio_data, sr)
        return output_path