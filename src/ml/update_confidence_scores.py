import sys
import os

# Add project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pymongo
import pandas as pd
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from config import MONGO_URI, DATABASE_NAME

# Connect to MongoDB
client = pymongo.MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
sentiment_collection = db["sentiment_comments"]  # Already stored sentiments

# Load Pretrained RoBERTa Model for Sentiment Analysis
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

# Ensure model runs on CPU only
device = torch.device("cpu")
model.to(device)

# Function to recompute confidence scores only for missing values
def update_confidence_scores():
    # Count documents that already have `confidence`
    with_confidence_count = sentiment_collection.count_documents({"confidence": {"$exists": True}})
    print(f"Number of documents WITH `confidence`: {with_confidence_count}")

    # Fetch only documents that are missing `confidence`
    comments = list(sentiment_collection.find({"confidence": {"$exists": False}}, {"_id": 1, "clean_text": 1, "sentiment": 1}))

    print(f"Number of documents MISSING `confidence`: {len(comments)}")

    if len(comments) == 0:
        print("All documents already have confidence scores. No update needed.")
        return

    # Process and update only missing confidence scores
    updated_count = 0
    for comment in comments:
        comment["_id"] = str(comment["_id"])  # Convert ObjectId to string
        
        # Encode text and get model probabilities
        tokens = tokenizer.encode(comment["clean_text"], truncation=True, max_length=512, return_tensors="pt").to(device)
        with torch.no_grad():
            output = model(tokens)
        
        probabilities = torch.nn.functional.softmax(output.logits, dim=1)  # Convert logits to probabilities
        confidence = max(probabilities[0]).item()  # Get highest confidence score

        # Update MongoDB with confidence score
        sentiment_collection.update_one(
            {"_id": comment["_id"]},
            {"$set": {"confidence": round(confidence, 4)}}
        )
        updated_count += 1

    print(f"Updated confidence scores for {updated_count} new records in MongoDB!")

# Run update
if __name__ == "__main__":
    update_confidence_scores()
