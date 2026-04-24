# retrieval.py - Gerald 10022200149
import numpy as np
import faiss
from embedder import get_model, load_index

def retrieve(query, index, chunks, top_k=5):
    m = get_model()
    query_vec = m.encode([query]).astype(np.float32)
    faiss.normalize_L2(query_vec)
    scores, indices = index.search(query_vec, top_k)
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        chunk = chunks[idx]
        results.append({
            "text": chunk["text"],
            "source": chunk["source"],
            "chunk_index": chunk["chunk_index"],
            "score": float(score)
        })
    return results

def query_expansion(query):
    expansions = {
        "election": "election voting results constituency winner candidate party votes Ghana presidential",
        "2020": "2020 year election presidential Ghana results NPP NDC candidate votes",
        "2016": "2016 year election presidential Ghana results NPP NDC candidate votes",
        "2012": "2012 year election presidential Ghana results NPP NDC candidate votes",
        "2008": "2008 year election presidential Ghana results NPP NDC candidate votes",
        "winner": "winner votes candidate results party NPP NDC election Ghana",
        "president": "president presidential election Ghana winner votes candidate NPP NDC",
        "accra": "accra greater accra region constituency election votes candidate",
        "votes": "votes election candidate party results constituency Ghana",
        "npp": "NPP new patriotic party election votes candidate Ghana results",
        "ndc": "NDC national democratic congress election votes candidate Ghana results",
        "akufo": "Nana Akufo Addo NPP presidential candidate election votes Ghana",
        "mahama": "John Dramani Mahama NDC presidential candidate election votes Ghana",
        "budget": "budget expenditure revenue fiscal policy Ghana 2025",
        "economy": "economy GDP growth fiscal monetary policy Ghana 2025",
        "education": "education schools funding policy budget Ghana 2025",
        "health": "health hospitals funding policy budget Ghana 2025",
        "revenue": "revenue income tax fiscal budget Ghana 2025",
    }
    extra = []
    for keyword, expansion in expansions.items():
        if keyword.lower() in query.lower():
            extra.append(expansion)
    expanded = query + " " + " ".join(extra)
    return expanded.strip()

def retrieve_with_expansion(query, index, chunks, top_k=5):
    expanded_query = query_expansion(query)
    print(f"[RETRIEVAL] Original: {query}")
    print(f"[RETRIEVAL] Expanded: {expanded_query}")
    
    # Get more results then filter by source if needed
    raw_results = retrieve(expanded_query, index, chunks, top_k=top_k * 3)
    
    # Check if query is election or budget related
    election_keywords = ["election", "vote", "votes", "party", "candidate", "npp", "ndc", 
                        "winner", "president", "constituency", "mahama", "akufo",
                        "2020", "2016", "2012", "2008", "2004", "2000", "1996", "1992"]
    budget_keywords = ["budget", "economy", "revenue", "expenditure", "fiscal", 
                      "gdp", "policy", "spending", "allocation", "ministry"]
    
    query_lower = query.lower()
    is_election = any(k in query_lower for k in election_keywords)
    is_budget = any(k in query_lower for k in budget_keywords)
    
    # If clearly election query, prioritise election chunks
    if is_election and not is_budget:
        election_results = [r for r in raw_results if r["source"] == "Ghana_Election_Result.csv"]
        other_results = [r for r in raw_results if r["source"] != "Ghana_Election_Result.csv"]
        filtered = (election_results + other_results)[:top_k]
        print(f"[RETRIEVAL] Election query detected - prioritising CSV chunks")
        return filtered
    
    # If clearly budget query, prioritise budget chunks
    elif is_budget and not is_election:
        budget_results = [r for r in raw_results if r["source"] == "budget_2025.pdf"]
        other_results = [r for r in raw_results if r["source"] != "budget_2025.pdf"]
        filtered = (budget_results + other_results)[:top_k]
        print(f"[RETRIEVAL] Budget query detected - prioritising PDF chunks")
        return filtered
    
    # Mixed or unclear - return top_k as normal
    return raw_results[:top_k]

if __name__ == "__main__":
    index, chunks, _ = load_index()
    test_query = "Who won the 2020 presidential election in Ghana?"
    print(f"\n--- Testing: '{test_query}' ---\n")
    results = retrieve_with_expansion(test_query, index, chunks, top_k=5)
    for i, r in enumerate(results):
        print(f"Result {i+1} | Score: {r['score']:.4f} | Source: {r['source']}")
        print(f"  {r['text'][:200]}\n")