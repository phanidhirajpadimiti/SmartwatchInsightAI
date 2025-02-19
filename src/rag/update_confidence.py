import sys
import os

# Add project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pymongo
import pinecone
from config import MONGO_URI, DATABASE_NAME



# Connect to MongoDB
client = pymongo.MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
sentiment_collection = db["sentiment_comments"]

# Initialize Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

# Function to update confidence scores in batches
def update_pinecone_confidence(batch_size=100):
    # Fetch all comments with confidence scores
    comments = list(sentiment_collection.find({}, {"_id": 1, "confidence": 1}))

    if not comments:
        print("No records found in MongoDB with confidence scores.")
        return

    total_records = len(comments)
    print(f"Updating {total_records} records in batches of {batch_size}...")

    updates = []
    updated_count = 0

    for comment in comments:
        comment_id = str(comment["_id"])
        confidence = round(comment.get("confidence", 0.5), 4)  # Default 0.5 if missing

        # Fetch the existing record from Pinecone
        result = index.fetch(ids=[comment_id])

        if comment_id in result["vectors"]:
            # Retrieve existing metadata
            metadata = result["vectors"][comment_id]["metadata"]
            metadata["confidence"] = confidence  # Add confidence score

            # Prepare batch update
            updates.append((comment_id, result["vectors"][comment_id]["values"], metadata))
            updated_count += 1

        # Send batch updates every `batch_size` records
        if len(updates) >= batch_size:
            index.upsert(updates)
            updates = []  # Reset batch buffer

    # Final batch update (if remaining records exist)
    if updates:
        index.upsert(updates)

    print(f"Successfully updated {updated_count} records in Pinecone!")

# Main function
def main():
    update_pinecone_confidence(batch_size=200)  # Adjust batch size as needed

if __name__ == "__main__":
    main()