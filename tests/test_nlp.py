from src.nlp_processor import analyze_transcription
import os

def main():
    # Specify the transcription file path
    transcription_file = "data/transcriptions/old-radio-227880_transcript_20241108_145845.txt"
    
    # Check if file exists
    if not os.path.exists(transcription_file):
        print(f"Error: File not found: {transcription_file}")
        return
    
    try:
        # Process the file
        print(f"Processing file: {transcription_file}")
        analysis, output_file = analyze_transcription(transcription_file)
        
        # Print results
        print("\nAnalysis complete!")
        print(f"Results saved to: {output_file}")
        
    except Exception as e:
        print(f"Error during analysis: {e}")

if __name__ == "__main__":
    main()