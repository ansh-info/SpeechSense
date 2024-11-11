import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from datetime import datetime
import librosa
import librosa.display
import matplotlib.pyplot as plt
import io
import altair as alt
from wordcloud import WordCloud
import soundfile as sf

class StreamlitVisualizer:
    """Handle all visualization components for the Streamlit interface"""
    
    def __init__(self):
        self.color_scheme = {
            'positive': '#28a745',
            'negative': '#dc3545',
            'neutral': '#17a2b8',
            'background': '#f8f9fa'
        }
    
    def display_audio_waveform(self, audio_file):
        """Display audio waveform visualization."""
        try:
            # Load audio file
            y, sr = librosa.load(audio_file)
            
            # Create time array
            times = np.arange(len(y))/sr
            
            # Create figure
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=times,
                y=y,
                line=dict(color='#1f77b4', width=1),
                name='Waveform'
            ))
            
            fig.update_layout(
                title='Audio Waveform',
                xaxis_title='Time (s)',
                yaxis_title='Amplitude',
                template='plotly_white',
                height=200,
                margin=dict(l=0, r=0, t=30, b=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error displaying waveform: {str(e)}")
    
    def display_spectrogram(self, audio_file):
        """Display audio spectrogram."""
        try:
            # Load audio file
            y, sr = librosa.load(audio_file)
            
            # Create spectrogram
            D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 4))
            img = librosa.display.specshow(D, x_axis='time', y_axis='log', ax=ax)
            plt.colorbar(img, ax=ax, format="%+2.f dB")
            plt.title('Spectrogram')
            
            # Convert to streamlit
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            st.image(buf)
            
        except Exception as e:
            st.error(f"Error displaying spectrogram: {str(e)}")
    
    def display_sentiment_gauge(self, sentiment_score):
        """Display sentiment score as a gauge chart."""
        try:
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = (sentiment_score + 1) * 50,  # Convert from [-1,1] to [0,100]
                title = {'text': "Sentiment Score"},
                gauge = {
                    'axis': {'range': [0, 100]},
                    'bar': {'color': self.color_scheme['neutral']},
                    'steps': [
                        {'range': [0, 40], 'color': self.color_scheme['negative']},
                        {'range': [40, 60], 'color': self.color_scheme['neutral']},
                        {'range': [60, 100], 'color': self.color_scheme['positive']}
                    ]
                }
            ))
            
            fig.update_layout(
                height=200,
                margin=dict(l=0, r=0, t=30, b=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error displaying sentiment gauge: {str(e)}")
    
    def display_word_cloud(self, text):
        """Generate and display word cloud."""
        try:
            wordcloud = WordCloud(
                width=800,
                height=400,
                background_color=self.color_scheme['background'],
                colormap='viridis'
            ).generate(text)
            
            # Convert to image
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            
            # Convert to streamlit
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            st.image(buf)
            
        except Exception as e:
            st.error(f"Error displaying word cloud: {str(e)}")
    
    def display_topic_visualization(self, topics):
        """Display interactive topic visualization."""
        try:
            # Prepare data
            topic_data = []
            for topic in topics:
                if isinstance(topic, dict):
                    for word in topic['words']:
                        topic_data.append({
                            'Topic': topic['topic'],
                            'Word': word,
                            'Size': 1
                        })
            
            if not topic_data:
                return
            
            df = pd.DataFrame(topic_data)
            
            # Create bubble chart
            chart = alt.Chart(df).mark_circle().encode(
                x=alt.X('Topic:N', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('Word:N'),
                size='Size:Q',
                color='Topic:N',
                tooltip=['Topic', 'Word']
            ).properties(
                width=600,
                height=400,
                title='Topic Distribution'
            ).interactive()
            
            st.altair_chart(chart, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error displaying topic visualization: {str(e)}")
    
    def display_realtime_metrics(self, metrics_history):
        """Display real-time metrics visualization."""
        try:
            df = pd.DataFrame(metrics_history)
            
            # Create line chart
            chart = alt.Chart(df).mark_line().encode(
                x='timestamp:T',
                y='value:Q',
                color='metric:N',
                tooltip=['metric', 'value', 'timestamp']
            ).properties(
                width=600,
                height=300,
                title='Real-time Metrics'
            ).interactive()
            
            st.altair_chart(chart, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error displaying real-time metrics: {str(e)}")
    
    def create_analysis_dashboard(self, analysis_results, audio_file=None):
        """Create a complete analysis dashboard."""
        try:
            st.markdown("## Analysis Dashboard")
            
            # Create tabs for different visualizations
            tabs = st.tabs([
                "Overview",
                "Audio Analysis",
                "Sentiment",
                "Topics",
                "Word Cloud"
            ])
            
            # Overview Tab
            with tabs[0]:
                st.markdown("### Key Metrics")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Sentiment", analysis_results['sentiment']['sentiment'])
                with col2:
                    st.metric("Polarity", f"{analysis_results['sentiment']['polarity']:.2f}")
                with col3:
                    st.metric("Key Phrases", len(analysis_results['key_phrases']))
            
            # Audio Analysis Tab
            with tabs[1]:
                if audio_file:
                    st.markdown("### Audio Visualization")
                    self.display_audio_waveform(audio_file)
                    self.display_spectrogram(audio_file)
            
            # Sentiment Tab
            with tabs[2]:
                st.markdown("### Sentiment Analysis")
                self.display_sentiment_gauge(analysis_results['sentiment']['polarity'])
            
            # Topics Tab
            with tabs[3]:
                st.markdown("### Topic Analysis")
                self.display_topic_visualization(analysis_results['topics'])
            
            # Word Cloud Tab
            with tabs[4]:
                st.markdown("### Word Cloud")
                if 'summary' in analysis_results:
                    self.display_word_cloud(analysis_results['summary'])
            
        except Exception as e:
            st.error(f"Error creating analysis dashboard: {str(e)}")

def init_visualization():
    """Initialize visualization settings in session state"""
    if 'visualizer' not in st.session_state:
        st.session_state.visualizer = StreamlitVisualizer()
    if 'metrics_history' not in st.session_state:
        st.session_state.metrics_history = []