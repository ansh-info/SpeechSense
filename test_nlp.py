from src.nlp_processor import analyze_transcription
import glob
import os

# Get the most recent transcription file
transcription_files = glob.glob("data/transcriptions/*.txt")
if transcription_files:
    latest_transcription = max(transcription_files, key=os.path.getctime)
    print(f"Processing file: {latest_transcription}")
    analysis, output_file = analyze_transcription(latest_transcription)
else:
    print("No transcription files found in data/transcriptions/")