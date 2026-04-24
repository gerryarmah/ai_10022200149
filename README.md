# ai_10022200149

# Academic City RAG Assistant

**Student Name:** Gerald Armah  
**Index Number:** 10022200149  
**Course:** CS4241 - Introduction to Artificial Intelligence  
**Lecturer:** Godwin N. Danso  
**Year:** 2026  

## Project Description
A RAG (Retrieval-Augmented Generation) application built from scratch without LangChain or LlamaIndex. Users can chat with Ghana Election Results and the 2025 Ghana Budget data.

## Tech Stack
- Embeddings: sentence-transformers (all-MiniLM-L6-v2)
- Vector Store: FAISS
- LLM: Groq (Llama 3.3 70B)
- UI: Streamlit

## How to Run
1. Install dependencies: `pip install -r requirements.txt`
2. Add your Groq API key to `.streamlit/secrets.toml`
3. Run: `streamlit run app.py`
