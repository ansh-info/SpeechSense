import streamlit as st
import os
from datetime import datetime
import time
from src.speech_recognition import SpeechHandler
from src.nlp_processor import analyze_transcription
from src.realtime_transcription import RealtimeTranscriber
from src import config

def init_session_state():
    """Initialize session state variables"""
    if 'recording' not in st.session_state:
        st.session_state.recording = False
    if 'transcriber' not in st.session_state:
        st.session_state.transcriber = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'transcripts' not in st.session_state:
        st.session_state.transcripts = []

def display_analysis_results(analysis):
    """Display analysis results in a formatted way"""
    if not analysis:
        return

    # Display sentiment with color coding
    sentiment = analysis['sentiment']['sentiment']
    polarity = analysis['sentiment']['polarity']
    
    sentiment_color = {
        'positive': 'green',
        'negative': 'red',
        'neutral': 'blue'
    }.get(sentiment, 'black')
    
    st.markdown(f"**Sentiment:** :{sentiment_color}[{sentiment}]")
    st.markdown(f"**Polarity Score:** :{sentiment_color}[{polarity:.2f}]")
    
    # Display summary
    st.markdown("**Summary:**")
    summary = analysis.get('summary', '')
    if isinstance(summary, str) and len(summary) > 50:  # Check if it's a valid summary
        st.markdown(f">{summary}")
    else:
        st.markdown("Summary not available for short texts")
    
    # Display topics if available
    st.markdown("**Topics:**")
    topics = analysis.get('topics', [])
    if isinstance(topics, list) and topics and isinstance(topics[0], dict):
        for topic in topics:
            if 'Error' not in topic['topic']:
                st.markdown(f"- {topic['topic']}: {', '.join(topic['words'])}")
    else:
        st.markdown("Topics not available for short texts")
    
    # Display key phrases
    st.markdown("**Key Phrases:**")
    key_phrases = analysis.get('key_phrases', [])
    if isinstance(key_phrases, list) and key_phrases:
        st.markdown(", ".join(key_phrases))
    else:
        st.markdown("Key phrases not available")

def process_uploaded_file(uploaded_file):
    """Process an uploaded audio file"""
    with st.spinner("Processing audio file..."):
        # Save uploaded file temporarily
        temp_path = os.path.join(config.RAW_DATA_DIR, uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Process the file
        handler = SpeechHandler()
        result = handler.process_audio_file(temp_path)
        
        if result['success']:
            st.success("Audio processed successfully!")
            
            # Create tabs for results
            transcript_tab, analysis_tab = st.tabs(["Transcription", "Analysis"])
            
            with transcript_tab:
                st.markdown("**Full Transcription:**")
                st.markdown(f">{result['transcription']}")
            
            with analysis_tab:
                # Perform and display analysis
                analysis, _ = analyze_transcription(result['transcript_file'])
                display_analysis_results(analysis)
        else:
            st.error(f"Error processing audio: {result['error']}")

def start_recording():
    """Start real-time recording"""
    st.session_state.recording = True
    st.session_state.transcriber = RealtimeTranscriber(analysis_interval=10)
    st.session_state.transcriber.start_recording()
    st.session_state.transcripts = []

def stop_recording():
    """Stop real-time recording"""
    if st.session_state.transcriber:
        st.session_state.recording = False
        analysis = st.session_state.transcriber.stop_recording()
        st.session_state.analysis_results = analysis

def main():
    st.title("Speech Recognition & NLP Analysis")
    
    # Initialize session state
    init_session_state()
    
    # Sidebar for mode selection
    mode = st.sidebar.radio(
        "Select Mode",
        ["File Upload", "Real-time Recording"]
    )
    
    if mode == "File Upload":
        st.header("Upload Audio File")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose an audio file",
            type=["wav", "mp3", "m4a", "ogg", "flac"]
        )
        
        if uploaded_file:
            st.audio(uploaded_file)
            
            if st.button("Process Audio"):
                process_uploaded_file(uploaded_file)
    
    else:  # Real-time Recording mode
        st.header("Real-time Recording")
        
        # Recording controls
        col1, col2 = st.columns(2)
        
        with col1:
            if not st.session_state.recording:
                if st.button("🎙️ Start Recording"):
                    start_recording()
        
        with col2:
            if st.session_state.recording:
                if st.button("⏹️ Stop Recording"):
                    stop_recording()
        
        # Display recording status and transcripts
        if st.session_state.recording:
            st.markdown("🔴 **Recording in progress...**")
            
            # Create placeholder for real-time updates
            transcript_container = st.container()
            
            while st.session_state.recording:
                if (st.session_state.transcriber and 
                    st.session_state.transcriber.full_transcript):
                    latest = st.session_state.transcriber.full_transcript[-1]
                    if latest not in st.session_state.transcripts:
                        st.session_state.transcripts.append(latest)
                    
                    with transcript_container:
                        st.markdown("**Latest Transcriptions:**")
                        for transcript in st.session_state.transcripts[-5:]:
                            st.markdown(f">{transcript}")
                time.sleep(1)
        
        # Display analysis results after recording
        if not st.session_state.recording and st.session_state.analysis_results:
            st.markdown("---")
            st.markdown("### Recording Analysis")
            display_analysis_results(st.session_state.analysis_results)

if __name__ == "__main__":
    main()