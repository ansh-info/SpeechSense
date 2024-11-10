import speech_recognition as sr
import threading
import queue
import time
from datetime import datetime
import os
from .nlp_processor import NLPProcessor
from . import config

class RealtimeTranscriber:
    def __init__(self, analysis_interval=30):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.nlp_processor = NLPProcessor()
        self.transcript_queue = queue.Queue()
        self.is_recording = False
        self.analysis_interval = analysis_interval  # Seconds between NLP analysis
        self.full_transcript = []
        
    def start_recording(self):
        """Start real-time recording and transcription."""
        with self.microphone as source:
            print("Calibrating for ambient noise... Please wait.")
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        
        self.is_recording = True
        self.recording_thread = threading.Thread(target=self._record_audio)
        self.processing_thread = threading.Thread(target=self._process_queue)
        self.analysis_thread = threading.Thread(target=self._periodic_analysis)
        
        self.recording_thread.start()
        self.processing_thread.start()
        self.analysis_thread.start()
        
    def stop_recording(self):
        """Stop recording and perform final analysis."""
        self.is_recording = False
        
        # Wait for threads to complete
        self.recording_thread.join()
        self.processing_thread.join()
        self.analysis_thread.join()
        
        # Perform final analysis
        self._save_final_transcript()
        return self._perform_analysis()
    
    def _record_audio(self):
        """Continuously record audio in chunks."""
        with self.microphone as source:
            while self.is_recording:
                try:
                    audio = self.recognizer.listen(source, timeout=10)
                    self.transcript_queue.put(audio)
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    print(f"Error recording audio: {e}")
                    break
    
    def _process_queue(self):
        """Process audio chunks from queue."""
        while self.is_recording or not self.transcript_queue.empty():
            try:
                if not self.transcript_queue.empty():
                    audio = self.transcript_queue.get()
                    text = self.recognizer.recognize_google(audio)
                    self.full_transcript.append(text)
                    print(f"Transcribed: {text}")
                else:
                    time.sleep(0.1)
            except sr.UnknownValueError:
                continue
            except Exception as e:
                print(f"Error processing audio: {e}")
    
    def _periodic_analysis(self):
        """Perform periodic NLP analysis on accumulated transcript."""
        last_analysis_time = time.time()
        
        while self.is_recording:
            current_time = time.time()
            if current_time - last_analysis_time >= self.analysis_interval:
                self._perform_analysis()
                last_analysis_time = current_time
            time.sleep(1)
    
    def _perform_analysis(self):
        """Perform NLP analysis on current transcript."""
        if not self.full_transcript:
            return None
            
        full_text = " ".join(self.full_transcript)
        analysis_result, _ = self.nlp_processor.analyze_text(
            full_text,
            output_dir=os.path.join(config.PROCESSED_DATA_DIR, 'realtime_analysis')
        )
        
        return analysis_result
    
    def _save_final_transcript(self):
        """Save the complete transcript to a file."""
        if not self.full_transcript:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"realtime_transcript_{timestamp}.txt"
        filepath = os.path.join(config.TRANSCRIPTIONS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(self.full_transcript))
        
        print(f"Full transcript saved to: {filepath}")