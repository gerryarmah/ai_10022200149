# app.py - Gerald 10022200149
import streamlit as st
from embedder import load_index, build_and_save
from chunker import prepare_all_chunks
from rag_pipeline import run_rag, run_pure_llm
import os

st.set_page_config(page_title="ACity RAG Assistant", page_icon="🎓", layout="wide")

st.title("🎓 Academic City RAG Assistant")
st.markdown("Chat with Ghana Election Results & 2025 Budget data")

@st.cache_resource
def load_or_build():
    index_path = os.path.join("embeddings", "index.faiss")
    if os.path.exists(index_path):
        return load_index()
    else:
        st.info("Building index for first time, please wait...")
        chunks = prepare_all_chunks()
        return build_and_save(chunks)

index, chunks, _ = load_or_build()

with st.sidebar:
    st.header("⚙️ Settings")
    top_k = st.slider("Top-K chunks to retrieve", 3, 10, 5)
    show_chunks = st.checkbox("Show retrieved chunks", value=True)
    show_scores = st.checkbox("Show similarity scores", value=True)
    show_prompt = st.checkbox("Show final prompt", value=False)
    compare_llm = st.checkbox("Compare with pure LLM", value=False)
    strict_mode = st.checkbox("Strict prompt mode", value=False)
    st.markdown("---")
    st.markdown("**Gerald Armah**")
    st.markdown("**Index: 10022200149**")
    st.markdown("CS4241 - Intro to AI - 2026")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

query = st.chat_input("Ask about Ghana elections or the 2025 budget...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving and generating answer..."):
            answer, logs, used_chunks = run_rag(
                query, index, chunks,
                top_k=top_k, strict=strict_mode
            )

        st.markdown(answer)

        if show_chunks:
            with st.expander("📄 Retrieved Chunks"):
                for i, chunk in enumerate(used_chunks):
                    score_str = f" | Score: {chunk['score']:.4f}" if show_scores else ""
                    st.markdown(f"**Chunk {i+1}** | Source: `{chunk['source']}`{score_str}")
                    st.text(chunk["text"][:300])
                    st.divider()

        if show_prompt:
            with st.expander("🧠 Final Prompt Sent to LLM"):
                st.code(logs[-2]["data"], language="text")

        if compare_llm:
            with st.expander("🤖 Pure LLM Response (No Retrieval)"):
                pure = run_pure_llm(query)
                st.markdown(pure)

    st.session_state.messages.append({"role": "assistant", "content": answer})