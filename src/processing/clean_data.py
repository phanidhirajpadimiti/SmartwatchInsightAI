import sys
import os

# Add project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pymongo
import re
import pandas as pd
from datetime import datetime
from config import MONGO_URI, DATABASE_NAME, COMMENT_COLLECTION

# Connect to MongoDB
client = pymongo.MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
comments_collection = db[COMMENT_COLLECTION]
cleaned_comments_collection = db["cleaned_comments"]  # New collection for cleaned data


# Function to clean text (lowercase, remove special characters)
def clean_text(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)  # Remove URLs
    text = re.sub(r"\W", " ", text)  # Remove special characters
    text = re.sub(r"\s+", " ", text).strip()  # Remove extra spaces
    return text

# Function to preprocess comments
def preprocess_comments():
    comments = list(comments_collection.find({}, {"_id": 1, "comment_text": 1, "published_at": 1}))
    
    for comment in comments:
        comment["_id"] = str(comment["_id"])  # Convert ObjectId to string
        comment["clean_text"] = clean_text(comment["comment_text"])  # Clean text
        comment["published_at"] = datetime.strptime(comment["published_at"], "%Y-%m-%dT%H:%M:%SZ")  # Convert timestamp
    
    return pd.DataFrame(comments)

# Function to store cleaned data in MongoDB
def store_cleaned_data(df):
    cleaned_comments_collection.delete_many({})  # Clear old data before inserting new
    cleaned_comments_collection.insert_many(df.to_dict("records"))  # Insert cleaned data
    print(f"Stored {len(df)} cleaned comments in MongoDB!")

# Main function
def main():
    df = preprocess_comments()
    print("Cleaned Data Sample:")
    print(df.head())
    print("Data shape:", df.shape)
    print("Data columns:", df.columns)

    # Store cleaned data
    store_cleaned_data(df)

if __name__ == "__main__":
    main()
