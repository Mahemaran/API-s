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
