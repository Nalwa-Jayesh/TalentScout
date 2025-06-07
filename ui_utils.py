import streamlit as st
from streamlit_option_menu import option_menu
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional
import json
from pathlib import Path
import pandas as pd

def init_page_config():
    """Initialize Streamlit page configuration with custom styling."""
    st.set_page_config(
        page_title="TalentScout AI Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def apply_custom_styling():
    """Apply custom CSS styling to the Streamlit app."""
    st.markdown("""
        <style>
        .main {
            background-color: #f5f5f5;
        }
        .stChatMessage {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            border: 1px solid #e0e0e0;
        }
        .stChatMessage[data-testid="stChatMessage"] {
            background-color: white;
        }
        .stChatMessage[data-testid="stChatMessage"][data-role="user"] {
            background-color: #e3f2fd;
        }
        .stChatMessage[data-testid="stChatMessage"][data-role="assistant"] {
            background-color: #f5f5f5;
        }
        .stButton>button {
            width: 100%;
            border-radius: 0.5rem;
            height: 3rem;
            background-color: #2196f3;
            color: white;
        }
        .stButton>button:hover {
            background-color: #1976d2;
        }
        </style>
    """, unsafe_allow_html=True)

def create_sidebar_menu():
    """Create a sidebar menu with navigation options."""
    with st.sidebar:
        st.image("https://via.placeholder.com/150", width=100)
        st.title("TalentScout")
        
        selected = option_menu(
            menu_title="Navigation",
            options=["Chat", "Analysis", "Settings"],
            icons=["chat", "graph-up", "gear"],
            menu_icon="cast",
            default_index=0,
        )
    return selected

def display_sentiment_analysis(sentiment_summary: Dict):
    """Display sentiment analysis results in a visually appealing way."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Positive", sentiment_summary.get("positive", 0))
    with col2:
        st.metric("Neutral", sentiment_summary.get("neutral", 0))
    with col3:
        st.metric("Negative", sentiment_summary.get("negative", 0))

def display_language_stats(language_distribution: Dict):
    """Display language distribution statistics."""
    if language_distribution:
        st.subheader("Language Distribution")
        df = pd.DataFrame(list(language_distribution.items()), 
                         columns=['Language', 'Count'])
        fig = go.Figure(data=[go.Pie(
            labels=df['Language'],
            values=df['Count'],
            hole=.3
        )])
        fig.update_layout(title='Languages Used in Conversation')
        st.plotly_chart(fig)

def create_chat_interface():
    """Create a modern chat interface."""
    st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <h1>Welcome to TalentScout AI Assistant</h1>
            <p>I'm here to help with your initial screening process.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Create a container for chat messages
    chat_container = st.container()
    
    # Create a container for the input area
    input_container = st.container()
    
    return chat_container, input_container

def display_progress(candidate_info: Dict):
    """Display candidate information collection progress."""
    st.sidebar.markdown("### Progress")
    
    # Create progress indicators for each field
    fields = [
        "Full Name", "Email", "Phone", "Years of Experience",
        "Desired Position", "Current Location", "Tech Stack"
    ]
    
    for field in fields:
        field_key = field.lower().replace(" ", "_")
        if candidate_info.get(field_key):
            st.sidebar.markdown(f"✅ {field}")
        else:
            st.sidebar.markdown(f"⭕ {field}")

def display_analysis_dashboard(analyzer):
    """Display the analysis dashboard with charts and statistics."""
    st.title("Conversation Analysis")
    
    # Display sentiment analysis
    st.subheader("Sentiment Analysis")
    sentiment_summary = analyzer.get_sentiment_summary()
    display_sentiment_analysis(sentiment_summary)
    
    # Display sentiment trend
    sentiment_trend = analyzer.plot_sentiment_trend()
    if sentiment_trend:
        st.plotly_chart(sentiment_trend)
    
    # Display language distribution
    language_dist = analyzer.get_language_distribution()
    display_language_stats(language_dist) 