# embedder.py - Gerald 10022200149
import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDINGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "embeddings")

model = None

def get_model():
    global model
    if model is None:
        print("[EMBEDDER] Loading sentence transformer model...")
        model = SentenceTransformer(MODEL_NAME)
        print("[EMBEDDER] Model loaded!")
    return model

def embed_chunks(chunks):
    m = get_model()
    texts = [c["text"] for c in chunks]
    print(f"[EMBEDDER] Embedding {len(texts)} chunks...")
    embeddings = m.encode(texts, show_progress_bar=True, batch_size=32)
    print(f"[EMBEDDER] Done! Shape: {embeddings.shape}")
    return embeddings

def build_faiss_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    print(f"[FAISS] Index built with {index.ntotal} vectors")
    return index

def save_index(index, chunks, embeddings):
    os.makedirs(EMBEDDINGS_DIR, exist_ok=True)
    faiss.write_index(index, os.path.join(EMBEDDINGS_DIR, "index.faiss"))
    with open(os.path.join(EMBEDDINGS_DIR, "chunks.json"), "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    np.save(os.path.join(EMBEDDINGS_DIR, "embeddings.npy"), embeddings)
    print("[EMBEDDER] Index, chunks and embeddings saved!")

def load_index():
    index = faiss.read_index(os.path.join(EMBEDDINGS_DIR, "index.faiss"))
    with open(os.path.join(EMBEDDINGS_DIR, "chunks.json"), "r", encoding="utf-8") as f:
        chunks = json.load(f)
    embeddings = np.load(os.path.join(EMBEDDINGS_DIR, "embeddings.npy"))
    print(f"[EMBEDDER] Loaded index with {index.ntotal} vectors")
    return index, chunks, embeddings

def build_and_save(chunks):
    embeddings = embed_chunks(chunks)
    embeddings = embeddings.astype(np.float32)
    index = build_faiss_index(embeddings.copy())
    save_index(index, chunks, embeddings)
    return index, chunks, embeddings

if __name__ == "__main__":
    from chunker import prepare_all_chunks
    chunks = prepare_all_chunks()
    build_and_save(chunks)