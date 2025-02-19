import sys
import os

# Add project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from openai import OpenAI
from config import PERPLEXITY_API_KEY, PERPLEXITY_BASE_URL
from src.rag.retrieval import retrieve_comments  # Import the retrieval function

# Initialize Perplexity API client
client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url=PERPLEXITY_BASE_URL)

def generate_ai_response(query, retrieved_comments):
    """
    Generates an AI response using Perplexity API based on retrieved comments.
    
    Params:
    - query (str): User's query
    - retrieved_comments (list): List of retrieved comments from Pinecone

    Returns:
    - AI-generated response string with citations
    """
    if not retrieved_comments:
        return {"response": "No relevant comments found.", "citations": []}

    # Prepare context for AI
    comment_snippets = "\n".join([f"- {c['comment']}" for c in retrieved_comments[:5]])  # Limit to 5 citations

    messages = [
        {
            "role": "system",
            "content": "You are an AI assistant providing insights from user-generated content."
        },
        {
            "role": "user",
            "content": f"""
            Based on the following YouTube comments, answer the query in a well-structured way:

            **User Query:** {query}

            **Relevant Comments:**
            {comment_snippets}

            **Your Answer:**
            """
        }
    ]

    response = client.chat.completions.create(
        model="sonar-pro",
        messages=messages,
    )

    ai_response = response.choices[0].message.content

    # Extract citations from the retrieved comments
    citations = [{"text": c["comment"], "sentiment": c["sentiment"], "confidence": c["confidence"]} for c in retrieved_comments[:5]]

    return {"response": ai_response, "citations": citations}

# Main function for testing
def main():
    query = input("\nEnter a search query: ")
    sentiment_filter = input("Filter by sentiment? (positive/negative/neutral/all): ").lower()

    if sentiment_filter == "all":
        sentiment_filter = None  # No filtering

    # Retrieve relevant comments from Pinecone
    retrieved_comments = retrieve_comments(query, top_k=5, sentiment_filter=sentiment_filter)

    # Generate AI response using Perplexity API with citations
    result = generate_ai_response(query, retrieved_comments)

    print("\n**AI Response:**")
    print(result["response"])

    print("\n**Citations (Source Comments Used):**")
    for idx, citation in enumerate(result["citations"], 1):
        print(f"{idx}. {citation['text']} (Sentiment: {citation['sentiment']}, Confidence: {citation['confidence']})")

if __name__ == "__main__":
    main()
