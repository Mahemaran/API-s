# Import necessary libraries
import googleapiclient.discovery
import pandas as pd
import streamlit as st
import pandas as pd
from datetime import datetime
import logging
from googletrans import Translator
from langdetect import detect
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Function to get YouTube comments
def get_youtube_comments(video_id, api_key):
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=api_key)
    comments = []
    next_page_token = None
    while True:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            textFormat="plainText",
            pageToken=next_page_token,
            maxResults=100)  # Max number of comments per request
        response = request.execute()
        for item in response["items"]:
            comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(comment)
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break
    return comments
api_key = "AIzaSyCbwvV9RgIX0B5vpe_0ki9SiHFwmi2a_9Y"  # Replace with your API key
video_id = "xBwfbsv3WjU"  # Replace with your YouTube video ID
comments = get_youtube_comments(video_id, api_key)
# Convert comments to DataFrame
df = pd.DataFrame(comments, columns=["Comment"])

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(message)s')

# Function to split text into batches with language detection
from googletrans import Translator
import logging
import re

# Function to detect if a text contains only emojis or numbers
def should_skip_translation(text):
    if not isinstance(text, str):  # Skip non-string inputs
        return True
    # Check if the text contains only numbers or emojis
    contains_only_numbers = text.strip().isdigit()
    contains_only_emojis = all(char in re.findall(r'[^\w\s,.!?]', text) for char in text)
    return contains_only_numbers or contains_only_emojis

# Function to translate texts in batches
def batch_translate(texts, batch_size=1000):
    translator = Translator()
    translations = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]  # Create a batch
        try:
            batch_translations = []
            for text in batch:
                if should_skip_translation(text):  # If text is a number or emoji, keep it as-is
                    batch_translations.append(text)
                else:
                    try:
                        translated_text = translator.translate(text, dest='en').text
                        batch_translations.append(translated_text)
                    except Exception as e:
                        logging.error(f"Error translating text: {text}, Error: {e}")
                        batch_translations.append("Translation Error")
            translations.extend(batch_translations)
        except Exception as e:
            logging.error(f"Error processing batch: {e}")
            translations.extend(["Batch Error" for _ in batch])
    return translations
df["translate"] = batch_translate(df["Comment"].tolist(), batch_size=300)
# Initialize VADER Sentiment Analyzer
analyzer = SentimentIntensityAnalyzer()
def get_sentiment(comment):
    sentiment_scores = analyzer.polarity_scores(comment)
    compound_score = sentiment_scores['compound']
    # Categorize based on compound score
    if compound_score >= 0.05:
        return 'positive'
    elif compound_score <= -0.05:
        return 'negative'
    else:
        return 'neutral'
df['Sentiment'] = df["translate"].apply(get_sentiment)
df1 = df["translate"].to_frame().merge(df['Sentiment'].to_frame(), left_index=True, right_index=True, how="left")
print(df1)