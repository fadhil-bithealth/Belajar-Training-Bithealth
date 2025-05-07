from qdrant_client import QdrantClient
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
import re
import os

LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT")

GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")

embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key = GOOGLE_API_KEY)


client = QdrantClient(host='localhost', port=6333)

def search_items_from_query(query: str, top_k: int = 20):
    # Step 1: Ubah query jadi embedding
    query_vector = embedding_model.embed_query(query)

    # Step 2: Cari ke Qdrant dengan vector tersebut
    search_result = client.search(
        collection_name="item_collection",
        query_vector=query_vector,
        limit=top_k
    )
    
    # Step 3: Ambil item_name dan item_code
    results = []
    for hit in search_result:
        payload = hit.payload
        item_name = payload.get("item_name", "Unknown")
        item_code = payload.get("item_code", "Unknown")
        results.append({"item_name": item_name, "item_code": item_code})
    
    return results

def extract_med_info(query: str):
    words = query.strip().split()

    # Variabel A: First word
    A = words[0] if words else None

    # Variabel B: Last word
    B = words[-1] if words else None

    # Variabel C: First two words
    C = ' '.join(words[:2]) if len(words) >= 2 else None

    # Variabel D: Dosage pattern (menangkap format umum dosis obat)
    dosage_pattern = r'\b\d+(?:\.\d+)?\s?(mg|mcg|g|ml)\b(?:\s*/\s*\d+(?:\.\d+)?\s?(mg|mcg|g|ml)\b)?'
    match = re.search(dosage_pattern, query.lower())
    D = match.group(0) if match else ""

    return {
        "A": A,
        "B": B,
        "C": C,
        "D": D
    }

def upper(text:str):
    query = text.upper()
    return query

def merge_unique_results(*results_lists):
    total_result = []
    seen_codes = set()

    for result_list in results_lists:
        for item in result_list:
            code = item.get("item_code")
            if code not in seen_codes:
                seen_codes.add(code)
                total_result.append(item)

    return total_result
