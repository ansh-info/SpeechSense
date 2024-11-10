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

def process_uploaded_file(uploaded_file):
    """Process an uploaded audio file"""
    # Save uploaded file temporarily
    temp_path = os.path.join(config.RAW_DATA_DIR, uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Process the file
    handler = SpeechHandler()
    result = handler.process_audio_file(temp_path)
    
    return result

def start_recording():
    """Start real-time recording"""
    st.session_state.recording = True
    st.session_state.transcriber = RealtimeTranscriber(analysis_interval=10)
    st.session_state.transcriber.start_recording()

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
                with st.spinner("Processing audio file..."):
                    result = process_uploaded_file(uploaded_file)
                    
                    if result['success']:
                        st.success("Audio processed successfully!")
                        
                        # Display transcription
                        st.subheader("Transcription")
                        st.write(result['transcription'])
                        
                        # Perform and display analysis
                        st.subheader("Analysis")
                        analysis, _ = analyze_transcription(result['transcript_file'])
                        
                        # Display sentiment
                        sentiment = analysis['sentiment']
                        st.write(f"**Sentiment:** {sentiment['sentiment']}")
                        st.write(f"**Polarity:** {sentiment['polarity']:.2f}")
                        
                        # Display summary
                        st.write("**Summary:**")
                        st.write(analysis['summary'])
                        
                        # Display topics
                        st.write("**Topics:**")
                        for topic in analysis['topics']:
                            if isinstance(topic, dict):
                                st.write(f"- {topic['topic']}: {', '.join(topic['words'])}")
                        
                        # Display key phrases
                        st.write("**Key Phrases:**")
                        st.write(", ".join(analysis['key_phrases']))
                    else:
                        st.error(f"Error: {result['error']}")
    
    else:  # Real-time Recording mode
        st.header("Real-time Recording")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if not st.session_state.recording:
                if st.button("Start Recording"):
                    start_recording()
        
        with col2:
            if st.session_state.recording:
                if st.button("Stop Recording"):
                    stop_recording()
        
        # Display recording status
        if st.session_state.recording:
            st.write("🔴 Recording in progress...")
            
            # Create a placeholder for real-time updates
            status_placeholder = st.empty()
            
            # Update status every second
            while st.session_state.recording:
                if st.session_state.transcriber and st.session_state.transcriber.full_transcript:
                    status_placeholder.write("Latest transcription:")
                    status_placeholder.write(st.session_state.transcriber.full_transcript[-1])
                time.sleep(1)
                
        # Display analysis results after recording
        if not st.session_state.recording and st.session_state.analysis_results:
            st.subheader("Recording Analysis")
            
            analysis = st.session_state.analysis_results
            
            # Display sentiment
            st.write(f"**Sentiment:** {analysis['sentiment']['sentiment']}")
            st.write(f"**Polarity:** {analysis['sentiment']['polarity']:.2f}")
            
            # Display summary
            st.write("**Summary:**")
            st.write(analysis['summary'])
            
            # Display topics
            st.write("**Topics:**")
            for topic in analysis['topics']:
                if isinstance(topic, dict):
                    st.write(f"- {topic['topic']}: {', '.join(topic['words'])}")
            
            # Display key phrases
            st.write("**Key Phrases:**")
            st.write(", '.join(analysis['key_phrases'])")

if __name__ == "__main__":
    main()