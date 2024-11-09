import os
import librosa
import soundfile as sf
from pydub import AudioSegment
from datetime import datetime
from . import config

class AudioFileHandler:
    """Handle different audio file formats and convert them to processable format."""
    
    SUPPORTED_FORMATS = ['.wav', '.mp3', '.m4a', '.flac', '.ogg']
    
    def __init__(self):
        self.sample_rate = config.SAMPLE_RATE
        
    def is_supported_format(self, file_path):
        """Check if the file format is supported."""
        return any(file_path.lower().endswith(fmt) for fmt in self.SUPPORTED_FORMATS)
    
    def convert_to_wav(self, input_file):
        """Convert any supported audio format to WAV."""
        if not self.is_supported_format(input_file):
            raise ValueError(f"Unsupported file format. Supported formats are: {self.SUPPORTED_FORMATS}")
        
        # If already WAV, return the original file path
        if input_file.lower().endswith('.wav'):
            return input_file
            
        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.splitext(os.path.basename(input_file))[0]
        output_path = os.path.join(config.PROCESSED_DATA_DIR, f"{filename}_{timestamp}.wav")
        
        # Convert to WAV
        audio = AudioSegment.from_file(input_file)
        audio.export(output_path, format="wav")
        
        return output_path