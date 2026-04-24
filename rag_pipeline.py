# rag_pipeline.py - Gerald 10022200149
import streamlit as st
from groq import Groq
from retrieval import retrieve_with_expansion

def get_groq_client():
    api_key = st.secrets["GROQ_API_KEY"]
    return Groq(api_key=api_key)

def select_context(results, max_chars=3000):
    sorted_results = sorted(results, key=lambda x: x["score"], reverse=True)
    context = ""
    used = []
    for r in sorted_results:
        if len(context) + len(r["text"]) > max_chars:
            break
        context += f"\n[Source: {r['source']}]\n{r['text']}\n"
        used.append(r)
    return context, used

def build_prompt(query, context):
    return f"""You are an AI assistant for Academic City University.
You help users understand Ghana election results and the 2025 Ghana Budget.

Use ONLY the context below to answer the question.
For election questions:
- The data shows regional results with candidates and their votes
- Add up votes for each candidate across all regions shown
- The candidate with the most total votes in the context is likely the winner
- State which candidate had more votes based on the context provided
Do NOT make up facts or figures not in the context.

--- CONTEXT START ---
{context}
--- CONTEXT END ---

Question: {query}

Answer (be decisive, use the vote totals from the context to determine the winner):"""

def build_strict_prompt(query, context):
    return f"""You are a factual assistant. Answer ONLY using the provided context.
Cite specific figures or names from the context in your answer.
If the context does not contain the answer, respond with: "Not found in context."

Context:
{context}

Question: {query}
Answer with evidence:"""

def log_pipeline(stage, data, logs):
    logs.append({"stage": stage, "data": data})

def run_rag(query, index, chunks, top_k=5, strict=False):
    logs = []
    log_pipeline("query", query, logs)

    results = retrieve_with_expansion(query, index, chunks, top_k=top_k)
    log_pipeline("retrieved_chunks", results, logs)

    context, used_chunks = select_context(results)
    log_pipeline("selected_context", used_chunks, logs)

    if strict:
        prompt = build_strict_prompt(query, context)
    else:
        prompt = build_prompt(query, context)
    log_pipeline("prompt", prompt, logs)

    client = get_groq_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=512
    )
    answer = response.choices[0].message.content
    log_pipeline("response", answer, logs)

    return answer, logs, used_chunks

def run_pure_llm(query):
    client = get_groq_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": query}],
        temperature=0.2,
        max_tokens=512
    )
    return response.choices[0].message.content