import sys
import os

# Add project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pymongo
import pinecone
import pandas as pd
from sentence_transformers import SentenceTransformer
from config import MONGO_URI, DATABASE_NAME

# Connect to MongoDB
client = pymongo.MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
sentiment_collection = db["sentiment_comments"]

# Initialize Pinecone using the new API
pc = pinecone.Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# Create Pinecone index if it doesn't exist
if PINECONE_INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=384,  # Embedding size of MiniLM
        metric="cosine",
        spec=pinecone.ServerlessSpec(cloud=os.getenv("PINECONE_CLOUD"), region=os.getenv("PINECONE_REGION"))
    )

# Connect to Pinecone index
index = pc.Index(PINECONE_INDEX_NAME)

# Load Sentence Embedding Model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Function to process & store embeddings in Pinecone
def store_embeddings():
    comments = list(sentiment_collection.find({}, {"_id": 1, "clean_text": 1, "sentiment": 1}))

    for comment in comments:
        comment_id = str(comment["_id"])
        text = comment["clean_text"]
        sentiment = comment.get("sentiment", "neutral")  # Default to neutral if missing

        # Generate embedding for the comment
        embedding = model.encode(text).tolist()

        # Store in Pinecone with metadata (sentiment & original text)
        index.upsert([(comment_id, embedding, {"sentiment": sentiment, "text": text})])

    print(f"Stored {len(comments)} comments in Pinecone with embeddings & sentiment!")

# Main function
def main():
    store_embeddings()

if __name__ == "__main__":
    main()