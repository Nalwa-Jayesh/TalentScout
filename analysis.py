from textblob import TextBlob
from langdetect import detect, LangDetectException
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Tuple, List, Optional, Union
import json
from pathlib import Path

class ConversationAnalyzer:
    def __init__(self):
        self.sentiment_history = []
        self.language_history = []
        self.candidate_dir = Path("candidates")
        self.candidate_dir.mkdir(exist_ok=True)

    def analyze_sentiment(self, text: str) -> Tuple[float, str]:
        """
        Analyze the sentiment of a text using TextBlob.
        Returns a tuple of (polarity, sentiment_label)
        """
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity
        
        # Categorize sentiment
        if polarity > 0.1:
            sentiment = "positive"
        elif polarity < -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"
            
        return polarity, sentiment

    def detect_language(self, text: str) -> str:
        """
        Detect the language of the text.
        Returns the language code or 'unknown' if detection fails.
        """
        try:
            return detect(text)
        except LangDetectException:
            return "unknown"

    def update_history(self, text: str, role: str):
        """
        Update the conversation history with sentiment and language analysis.
        """
        if role == "user":  # Only analyze user messages
            polarity, sentiment = self.analyze_sentiment(text)
            language = self.detect_language(text)
            
            self.sentiment_history.append({
                "text": text,
                "polarity": polarity,
                "sentiment": sentiment,
                "language": language
            })

    def get_sentiment_summary(self) -> Dict:
        """
        Generate a summary of sentiment analysis.
        """
        if not self.sentiment_history:
            return {"positive": 0, "neutral": 0, "negative": 0}
            
        sentiments = [entry["sentiment"] for entry in self.sentiment_history]
        return {
            "positive": sentiments.count("positive"),
            "neutral": sentiments.count("neutral"),
            "negative": sentiments.count("negative")
        }

    def get_language_distribution(self) -> Dict:
        """
        Generate a summary of language distribution.
        """
        if not self.sentiment_history:
            return {}
            
        languages = [entry["language"] for entry in self.sentiment_history]
        return pd.Series(languages).value_counts().to_dict()

    def save_analysis(self, candidate_name: str):
        """
        Save the analysis results to a JSON file.
        """
        analysis_data = {
            "sentiment_history": self.sentiment_history,
            "sentiment_summary": self.get_sentiment_summary(),
            "language_distribution": self.get_language_distribution()
        }
        
        file_path = self.candidate_dir / f"{candidate_name}_analysis.json"
        with open(file_path, "w") as f:
            json.dump(analysis_data, f, indent=2)

    def plot_sentiment_trend(self) -> Optional[go.Figure]:
        """
        Create a plotly figure showing sentiment trend over time.
        """
        if not self.sentiment_history:
            return None
            
        df = pd.DataFrame(self.sentiment_history)
        df['index'] = range(len(df))
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['index'],
            y=df['polarity'],
            mode='lines+markers',
            name='Sentiment'
        ))
        
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        fig.update_layout(
            title='Sentiment Trend During Conversation',
            xaxis_title='Message Number',
            yaxis_title='Sentiment Polarity'
        )
        return fig

    def plot_language_distribution(self) -> Optional[go.Figure]:
        """
        Create a plotly figure showing language distribution.
        """
        if not self.sentiment_history:
            return None
            
        lang_dist = self.get_language_distribution()
        df = pd.DataFrame(list(lang_dist.items()), columns=['Language', 'Count'])
        
        fig = go.Figure(data=[go.Pie(
            labels=df['Language'],
            values=df['Count'],
            hole=.3
        )])
        
        fig.update_layout(
            title='Language Distribution in Conversation'
        )
        return fig 