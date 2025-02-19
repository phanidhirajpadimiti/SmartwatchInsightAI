import os
import subprocess
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
from src.api.chatbot_api import app as fastapi_app

# Load environment variables
load_dotenv()

# Initialize FastAPI application
app = FastAPI(title="SmartwatchInsightAI", description="A Competitor Intelligence Chatbot for Smartwatches")

# Mount FastAPI's app inside `main.py`
app.mount("/api", fastapi_app)

@app.get("/")
def home():
    return {"message": "Welcome to SmartwatchInsightAI! Use /api/docs for API documentation."}

# Function to start Streamlit UI
def run_streamlit():
    """Starts Streamlit UI in a separate process."""
    print("Starting Streamlit UI...")
    subprocess.Popen(["streamlit", "run", "src/frontend/chatbot_ui.py"])

# Function to start FastAPI backend
def run_fastapi():
    """Starts FastAPI backend using Uvicorn."""
    print("Starting FastAPI Backend...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    # Start Streamlit UI in a separate process
    run_streamlit()

    # Run FastAPI backend
    run_fastapi()
