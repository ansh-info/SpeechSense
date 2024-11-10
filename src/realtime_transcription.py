import speech_recognition as sr
import threading
import queue
import time
from datetime import datetime
import os
from .nlp_processor import NLPProcessor
from . import config

class RealtimeTranscriber:
    def __init__(self, device_index=None, analysis_interval=30):
        """
        Initialize the transcriber with specific device settings.
        
        Args:
            device_index (int): Index of the microphone device to use
            analysis_interval (int): Seconds between NLP analyses
        """
        self.recognizer = sr.Recognizer()
        try:
            self.microphone = sr.Microphone(device_index=device_index)
            # Test microphone initialization
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
        except Exception as e:
            raise Exception(f"Error initializing microphone: {e}")
            
        self.nlp_processor = NLPProcessor()
        self.transcript_queue = queue.Queue()
        self.is_recording = False
        self.analysis_interval = analysis_interval
        self.full_transcript = []
        self.threads = []
    
    def start_recording(self):
        """Start real-time recording and transcription."""
        print("Initializing recording...")
        
        try:
            with self.microphone as source:
                print("Calibrating for ambient noise... Please wait.")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                print("Calibration complete.")
        except Exception as e:
            raise Exception(f"Error during calibration: {e}")
        
        self.is_recording = True
        
        # Create and start threads
        self.threads = [
            threading.Thread(target=self._record_audio, name="RecordingThread"),
            threading.Thread(target=self._process_queue, name="ProcessingThread"),
            threading.Thread(target=self._periodic_analysis, name="AnalysisThread")
        ]
        
        for thread in self.threads:
            thread.daemon = True  # Make threads daemon so they exit when main program exits
            thread.start()
        
        print("Recording started successfully.")
    
    def stop_recording(self):
        """Stop recording and perform final analysis."""
        print("Stopping recording...")
        self.is_recording = False
        
        # Wait for threads to complete with timeout
        for thread in self.threads:
            thread.join(timeout=5.0)
        
        # Perform final analysis
        self._save_final_transcript()
        return self._perform_analysis()
    
    def _record_audio(self):
        """Continuously record audio in chunks."""
        print("Starting audio recording...")
        
        with self.microphone as source:
            while self.is_recording:
                try:
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=30)
                    self.transcript_queue.put(audio)
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    print(f"Error recording audio: {e}")
                    if self.is_recording:  # Only break if we're supposed to be recording
                        break
    
    def _process_queue(self):
        """Process audio chunks from queue."""
        while self.is_recording or not self.transcript_queue.empty():
            try:
                if not self.transcript_queue.empty():
                    audio = self.transcript_queue.get(timeout=1)  # 1 second timeout
                    try:
                        text = self.recognizer.recognize_google(audio)
                        if text.strip():  # Only add non-empty transcriptions
                            self.full_transcript.append(text)
                            print(f"Transcribed: {text}")
                    except sr.UnknownValueError:
                        pass  # Ignore unrecognized audio
                    except sr.RequestError as e:
                        print(f"Speech recognition service error: {e}")
                else:
                    time.sleep(0.1)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing audio: {e}")
    
    def _periodic_analysis(self):
        """Perform periodic NLP analysis on accumulated transcript."""
        last_analysis_time = time.time()
        
        while self.is_recording:
            current_time = time.time()
            if current_time - last_analysis_time >= self.analysis_interval:
                analysis = self._perform_analysis()
                if analysis:
                    print("\nInterim Analysis:")
                    print(f"Sentiment: {analysis['sentiment']['sentiment']}")
                last_analysis_time = current_time
            time.sleep(1)
    
    def _perform_analysis(self):
        """Perform NLP analysis on current transcript."""
        if not self.full_transcript:
            return None
            
        full_text = " ".join(self.full_transcript)
        try:
            analysis_result, _ = self.nlp_processor.analyze_text(
                full_text,
                output_dir=os.path.join(config.PROCESSED_DATA_DIR, 'realtime_analysis')
            )
            return analysis_result
        except Exception as e:
            print(f"Error performing analysis: {e}")
            return None
    
    def _save_final_transcript(self):
        """Save the complete transcript to a file."""
        if not self.full_transcript:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"realtime_transcript_{timestamp}.txt"
        filepath = os.path.join(config.TRANSCRIPTIONS_DIR, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("\n".join(self.full_transcript))
            print(f"Full transcript saved to: {filepath}")
        except Exception as e:
            print(f"Error saving transcript: {e}")