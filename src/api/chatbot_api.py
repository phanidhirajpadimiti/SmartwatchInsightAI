import sys
import os

# Add project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import FastAPI
from pydantic import BaseModel
from src.rag.retrieval import retrieve_comments
from src.rag.generate_response import generate_ai_response

# Initialize FastAPI app
app = FastAPI()

# Request model for chat input
class ChatRequest(BaseModel):
    query: str
    sentiment_filter: str = "all"

@app.post("/chat")
def chat(request: ChatRequest):
    """
    API endpoint for chatbot queries.
    
    - Retrieves relevant YouTube comments from Pinecone
    - Generates an AI response using Perplexity AI
    - Returns citations (original comments used for response)
    """
    sentiment_filter = None if request.sentiment_filter.lower() == "all" else request.sentiment_filter.lower()

    # Retrieve relevant comments
    retrieved_comments = retrieve_comments(request.query, top_k=5, sentiment_filter=sentiment_filter)

    # Generate AI response
    result = generate_ai_response(request.query, retrieved_comments)

    return {
        "response": result["response"],
        "citations": result["citations"]
    }
