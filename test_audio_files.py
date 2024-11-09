# Run it with a single file
from src.speech_recognition import process_single_file

# Process a single file
result = process_single_file("data/raw/old-radio-227880.mp3")

# Check result
if result['success']:
    print(f"Transcription: {result['transcription']}")
else:
    print(f"Error: {result['error']}")

# Or process a directory
from src.speech_recognition import process_directory

# Process all files in a directory
results = process_directory("data/raw")

# Check results
for result in results:
    if result['success']:
        print(f"File: {result['original_file']}")
        print(f"Transcription: {result['transcription']}")
    else:
        print(f"Error with {result['original_file']}: {result['error']}")