# chunker.py - Gerald 10022200149
import pandas as pd
import fitz
import os

def load_csv(filepath):
    df = pd.read_csv(filepath)
    df.dropna(how="all", inplace=True)
    df.fillna("", inplace=True)
    print(f"[CSV] Loaded {len(df)} rows, {len(df.columns)} columns")
    return df

def chunk_csv(df, chunk_size=2, overlap=0):
    chunks = []
    rows = df.to_dict(orient="records")
    step = chunk_size
    for i in range(0, len(rows), step):
        batch = rows[i: i + chunk_size]
        text = " | ".join(
            ", ".join(f"{k}: {v}" for k, v in row.items() if v != "")
            for row in batch
        )
        chunks.append({
            "text": text,
            "source": "Ghana_Election_Result.csv",
            "chunk_index": len(chunks)
        })
    print(f"[CSV] Created {len(chunks)} chunks")
    return chunks

def load_pdf(filepath):
    doc = fitz.open(filepath)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text().strip()
        if text:
            pages.append({"page": i + 1, "text": text})
    print(f"[PDF] Extracted {len(pages)} pages")
    return pages

def chunk_pdf(pages, chunk_size=800, overlap=100):
    chunks = []
    full_text = ""
    page_map = []
    for p in pages:
        start = len(full_text)
        full_text += p["text"] + " "
        page_map.append((start, len(full_text), p["page"]))

    def get_page_num(char_index):
        for start, end, page in page_map:
            if start <= char_index < end:
                return page
        return -1

    step = chunk_size - overlap
    for i in range(0, len(full_text), step):
        chunk_text = full_text[i: i + chunk_size].strip()
        if len(chunk_text) < 50:
            continue
        chunks.append({
            "text": chunk_text,
            "source": "budget_2025.pdf",
            "page": get_page_num(i),
            "chunk_index": len(chunks)
        })
    print(f"[PDF] Created {len(chunks)} chunks")
    return chunks

def prepare_all_chunks():
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    df = load_csv(os.path.join(base, "Ghana_Election_Result.csv"))
    csv_chunks = chunk_csv(df)
    pages = load_pdf(os.path.join(base, "budget_2025.pdf"))
    pdf_chunks = chunk_pdf(pages)
    all_chunks = csv_chunks + pdf_chunks
    print(f"[TOTAL] {len(all_chunks)} chunks ready for embedding")
    return all_chunks

if __name__ == "__main__":
    prepare_all_chunks()