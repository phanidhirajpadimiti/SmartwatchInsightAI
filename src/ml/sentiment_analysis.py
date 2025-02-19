import sys
import os

# Add project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pymongo
import pandas as pd
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
from config import MONGO_URI, DATABASE_NAME

# Connect to MongoDB
client = pymongo.MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
cleaned_collection = db["cleaned_comments"]
sentiment_collection = db["sentiment_comments"]  # Store sentiment results

# Load Pretrained RoBERTa Model for Sentiment Analysis
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# Function to analyze sentiment using fine-tuned RoBERTa
def analyze_sentiment(text):
    # Truncate to 512 tokens, ensure no error due to length
    tokens = tokenizer.encode(text, truncation=True, max_length=512, return_tensors="pt")
    
    with torch.no_grad():
        output = model(tokens)

    prediction = torch.argmax(output.logits, dim=1).item()

    # Convert RoBERTa labels to standard sentiment labels
    label_map = {0: "negative", 1: "neutral", 2: "positive"}
    
    return label_map[prediction]  # Returns 'positive', 'negative', or 'neutral'

# Function to process sentiment analysis
def process_sentiment():
    comments = list(cleaned_collection.find({}, {"_id": 1, "clean_text": 1, "published_at": 1}))

    for comment in comments:
        comment["_id"] = str(comment["_id"])  # Convert ObjectId to string
        comment["sentiment"] = analyze_sentiment(comment["clean_text"])  # Perform sentiment analysis

    return pd.DataFrame(comments)

# Function to store sentiment results in MongoDB
def store_sentiment_data(df):
    sentiment_collection.delete_many({})  # Clear old data before inserting new
    sentiment_collection.insert_many(df.to_dict("records"))
    print(f"Stored {len(df)} sentiment-scored comments in MongoDB!")

# Main function
def main():
    df = process_sentiment()
    print("Sentiment Analysis Sample:")
    print(df.head())

    # Store sentiment results
    store_sentiment_data(df)

if __name__ == "__main__":
    main()