import sys
import os

# Add project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pinecone
import numpy as np
from sentence_transformers import SentenceTransformer
from config import PINECONE_API_KEY, PINECONE_INDEX_NAME

# Initialize Pinecone
pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

# Load Sentence Embedding Model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def retrieve_comments(query, top_k=5, sentiment_filter=None):
    """
    Retrieves relevant comments from Pinecone based on query embedding.

    Params:
    - query (str): User's search query
    - top_k (int): Number of top results to retrieve
    - sentiment_filter (str or None): Filter by sentiment (e.g., "positive", "negative", or None for all)

    Returns:
    - List of dictionaries containing retrieved comments and metadata
    """
    # Convert query into embedding
    query_embedding = model.encode(query).tolist()

    # Search Pinecone for the most relevant comments
    search_results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )

    # Extract and process results
    retrieved_comments = []
    for match in search_results["matches"]:
        metadata = match["metadata"]
        comment_text = metadata["text"]
        sentiment = metadata.get("sentiment", "neutral")
        confidence = metadata.get("confidence", 0.5)  # Default confidence if missing

        # Apply sentiment filtering (if specified)
        if sentiment_filter and sentiment != sentiment_filter:
            continue

        retrieved_comments.append({
            "comment": comment_text,
            "sentiment": sentiment,
            "confidence": confidence,
            "score": match["score"]
        })

    return retrieved_comments
