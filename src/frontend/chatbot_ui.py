import streamlit as st
import requests

# API endpoint
API_URL = "http://localhost:8000/api/chat"

st.set_page_config(page_title="Smartwatch Chatbot", page_icon="⌚")
st.title("⌚ Smartwatch AI Chatbot")

query = st.text_input("Ask me about Smartwatch reviews:")
sentiment_filter = st.selectbox("Filter by sentiment:", ["all", "positive", "negative"])

if st.button("Ask AI"):
    if not query:
        st.warning("Please enter a query.")
    else:
        with st.spinner("Thinking..."):
            try:
                response = requests.post(API_URL, json={"query": query, "sentiment_filter": sentiment_filter})
                response_data = response.json()
                ai_response = response_data.get("response", "No response received.")
                citations = response_data.get("citations", [])

                st.success("AI Response:")
                st.write(ai_response)

                if citations:
                    st.subheader("Citations (Source Comments Used):")
                    for idx, citation in enumerate(citations, 1):
                        st.markdown(f"**{idx}.** {citation['text']}  \n*Sentiment: {citation['sentiment']}, Confidence: {citation['confidence']}*")
            except requests.ConnectionError:
                st.error("Unable to connect to the chatbot API. Please ensure FastAPI is running.")
