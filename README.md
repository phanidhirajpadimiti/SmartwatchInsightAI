# 🏆 SmartwatchInsightAI  
### **A Competitor Intelligence Tool for Smartwatches**  

## 📌 Project Overview  
SmartwatchInsightAI is an **AI-powered competitor intelligence tool** that helps both **brands (Apple, Samsung, Fitbit, etc.) and consumers** analyze smartwatch reviews.  

### **What Problem Are We Solving?**  
In the smartwatch industry, brands struggle to understand:  
🔹 **Why users prefer one brand over another**  
🔹 **What features drive user satisfaction or dissatisfaction**  
🔹 **How consumer sentiment shifts over time**  

📢 **This tool provides real-time insights into smartwatch preferences by analyzing 50K+ user reviews, helping brands refine their product strategy and consumers make informed choices.**  

---

## 🚀 Key Features  
✅ **Feature-Based Comparison:** See which smartwatch features (battery, design, price, UI, etc.) users love or dislike.  
✅ **Sentiment Analysis:** Understand how users feel about different smartwatch brands.  
✅ **Competitor Insights:** Find out **why** users prefer Samsung over Apple, or vice versa.  
✅ **Text-Based Summaries:** AI-generated insights to simplify large-scale review data.  
✅ **Transparent AI Responses:** Includes citations from real user reviews.  

---

## 🤖 Why Use Retrieval-Augmented Generation (RAG)?  
### **Challenges with Traditional LLM Fine-Tuning**  
❌ Fine-tuning an LLM requires **huge datasets and computational power**.  
❌ A static LLM cannot **adapt to new smartwatch reviews dynamically**.  

### **Why RAG is the Better Choice for This Project**  
✔ **Real-time, updated insights** without retraining  
✔ **Fact-grounded responses** using real user reviews  
✔ **Efficient and scalable** for new smartwatch data sources  

---

## 🛠️ Technologies Used & Why  
| **Technology** | **Purpose** | **Why Used?** |
|--------------|------------|------------|
| **FastAPI** | Backend API | Lightweight, high-performance API for data retrieval. |
| **Streamlit** | Frontend UI | Simple, interactive chatbot interface for queries. |
| **MongoDB** | Database | Storing and structuring smartwatch reviews efficiently. |
| **Pinecone** | Vector Database | Fast similarity search for retrieving relevant reviews. |
| **MiniLM** | Embeddings | Compact, efficient NLP model for sentence embeddings. |
| **RoBERTa (Cardiff NLP)** | Sentiment Analysis | Accurately classifies user sentiment. |
| **Perplexity API (Sonar-Pro)** | AI Response Generation | Generates concise summaries from retrieved reviews. |
| **YouTube API** | Data Collection | Fetching smartwatch review comments for analysis. |

---

## 🛠️ Future Enhancements  
🔹 **Aspect-Based Sentiment Analysis:** Categorize user opinions into feature-specific insights (e.g., battery, display, software).  
🔹 **Competitor Ranking System:** Introduce **quantitative analysis** (score-based comparison).  
🔹 **Trend Tracking Over Time:** Identify shifts in user perception of smartwatches.  
🔹 **Expand Data Sources:** Add reviews from **Reddit, Trustpilot, Amazon** for broader insights.  
🔹 **Deploy Online:** Make the tool publicly accessible via **Hugging Face Spaces, AWS, or Render**.  

---

## 📜 Installation & Setup  
### **1️⃣ Clone the Repository**  
```bash
git clone https://github.com/phanidhirajpadimiti/SmartwatchInsightAI.git
cd SmartwatchInsightAI
