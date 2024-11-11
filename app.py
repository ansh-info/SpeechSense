import numpy as np
import pandas as pd
import streamlit as st
import os
from datetime import datetime
import time
from src.speech_recognition import SpeechHandler
from src.nlp_processor import analyze_transcription
from src.realtime_transcription import RealtimeTranscriber
from src.visualization import StreamlitVisualizer, init_visualization
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
    if 'metrics_history' not in st.session_state:
        st.session_state.metrics_history = []
    init_visualization()

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
                st.markdown("### Full Transcription")
                st.markdown(f">{result['transcription']}")
                
                # Display audio visualizations
                st.session_state.visualizer.display_audio_waveform(temp_path)
                st.session_state.visualizer.display_spectrogram(temp_path)
            
            with analysis_tab:
                # Perform and display analysis
                analysis, _ = analyze_transcription(result['transcript_file'])
                st.session_state.visualizer.create_analysis_dashboard(
                    analysis,
                    audio_file=temp_path
                )
        else:
            st.error(f"Error processing audio: {result['error']}")

def update_metrics_history(text=None, analysis=None):
    """Update metrics history for real-time visualization"""
    timestamp = datetime.now()
    
    if analysis and 'sentiment' in analysis:
        st.session_state.metrics_history.append({
            'timestamp': timestamp,
            'metric': 'sentiment',
            'value': analysis['sentiment']['polarity']
        })
    
    if text:
        st.session_state.metrics_history.append({
            'timestamp': timestamp,
            'metric': 'word_count',
            'value': len(text.split())
        })

def main():
    st.title("Speech Recognition & NLP Analysis")
    
    # Initialize session state
    init_session_state()
    
    # Sidebar for mode selection
    with st.sidebar:
        mode = st.radio(
            "Select Mode",
            ["File Upload", "Real-time Recording"]
        )
        
        st.markdown("---")
        st.markdown("### Settings")
        
        # Add visualization settings
        st.checkbox("Show Audio Waveform", value=True, key="show_waveform")
        st.checkbox("Show Spectrogram", value=True, key="show_spectrogram")
        st.checkbox("Show Word Cloud", value=True, key="show_wordcloud")
        
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
                    st.session_state.recording = True
                    st.session_state.transcriber = RealtimeTranscriber(analysis_interval=10)
                    st.session_state.transcriber.start_recording()
                    st.session_state.transcripts = []
                    st.session_state.metrics_history = []
        
        with col2:
            if st.session_state.recording:
                if st.button("⏹️ Stop Recording"):
                    if st.session_state.transcriber:
                        st.session_state.recording = False
                        analysis = st.session_state.transcriber.stop_recording()
                        st.session_state.analysis_results = analysis
        
        # Display recording status and transcripts
        if st.session_state.recording:
            st.markdown("🔴 **Recording in progress...**")
            
            # Create containers for real-time updates
            metrics_container = st.container()
            transcript_container = st.container()
            
            while st.session_state.recording:
                if st.session_state.transcriber and st.session_state.transcriber.full_transcript:
                    latest = st.session_state.transcriber.full_transcript[-1]
                    if latest not in st.session_state.transcripts:
                        st.session_state.transcripts.append(latest)
                        update_metrics_history(text=latest)
                    
                    with metrics_container:
                        st.session_state.visualizer.display_realtime_metrics(
                            st.session_state.metrics_history
                        )
                    
                    with transcript_container:
                        st.markdown("**Latest Transcriptions:**")
                        for transcript in st.session_state.transcripts[-5:]:
                            st.markdown(f">{transcript}")
                time.sleep(1)
        
        # Display analysis results after recording
            if not st.session_state.recording and st.session_state.analysis_results:
                st.markdown("---")
                st.markdown("### Analysis Results")
                
                # Create analysis dashboard
                st.session_state.visualizer.create_analysis_dashboard(
                    st.session_state.analysis_results
                )
                
                # Display final metrics
                st.markdown("### Recording Summary")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total_duration = len(st.session_state.transcripts) * 10  # Approximate
                    st.metric(
                        "Recording Duration",
                        f"{total_duration} seconds",
                        help="Approximate duration based on transcript segments"
                    )
                
                with col2:
                    total_words = sum(len(t.split()) for t in st.session_state.transcripts)
                    st.metric(
                        "Total Words",
                        total_words,
                        help="Total number of words transcribed"
                    )
                
                with col3:
                    # Calculate average sentiment if metrics history exists
                    sentiment_metrics = [
                        m['value'] for m in st.session_state.metrics_history 
                        if m['metric'] == 'sentiment'
                    ]
                    if sentiment_metrics:
                        avg_sentiment = np.mean(sentiment_metrics)
                        st.metric(
                            "Average Sentiment",
                            f"{avg_sentiment:.2f}",
                            help="Average sentiment score throughout the recording"
                        )
                    else:
                        st.metric(
                            "Average Sentiment",
                            "N/A",
                            help="No sentiment data available"
                        )
                
                # Additional summary metrics
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                with col1:
                    # Display transcription confidence if available
                    if hasattr(st.session_state.transcriber, 'confidence_scores'):
                        avg_confidence = np.mean(st.session_state.transcriber.confidence_scores)
                        st.metric(
                            "Average Transcription Confidence",
                            f"{avg_confidence:.1%}",
                            help="Average confidence score of speech recognition"
                        )
                
                with col2:
                    # Display speaking rate
                    if total_duration > 0:
                        speaking_rate = total_words / (total_duration / 60)  # words per minute
                        st.metric(
                            "Speaking Rate",
                            f"{speaking_rate:.1f} WPM",
                            help="Words per minute"
                        )
                
                # Download buttons for results
                st.markdown("### Export Results")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("Download Transcript"):
                        transcript_text = "\n".join(st.session_state.transcripts)
                        st.download_button(
                            "Download Transcript",
                            transcript_text,
                            file_name=f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
                
                with col2:
                    if st.button("Download Analysis"):
                        analysis_text = str(st.session_state.analysis_results)
                        st.download_button(
                            "Download Analysis",
                            analysis_text,
                            file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
                
                with col3:
                    if st.button("Download Metrics"):
                        metrics_df = pd.DataFrame(st.session_state.metrics_history)
                        csv = metrics_df.to_csv(index=False)
                        st.download_button(
                            "Download Metrics",
                            csv,
                            file_name=f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )

if __name__ == "__main__":
    main()