"""
Local, free embeddings via sentence-transformers — Groq doesn't serve an
embeddings endpoint, so this fills that gap without adding another paid API.
"""
import chromadb
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path="./chroma_data")


def get_or_create_collection(session_id: str):
    return chroma_client.get_or_create_collection(name=f"research_{session_id}")


def index_research_chunks(session_id: str, chunks: list[dict]):
    """chunks: [{title, url, content}] from tools/search.py"""
    collection = get_or_create_collection(session_id)
    texts = [c["content"] for c in chunks if c["content"]]
    if not texts:
        return
    embeddings = embedder.encode(texts).tolist()
    collection.add(
        documents=texts,
        embeddings=embeddings,
        metadatas=[{"title": c["title"], "url": c["url"]} for c in chunks if c["content"]],
        ids=[f"{session_id}_{i}" for i in range(len(texts))],
    )


def query_research(session_id: str, query: str, n_results: int = 5) -> list[str]:
    collection = get_or_create_collection(session_id)
    query_embedding = embedder.encode([query]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=n_results)
    return results["documents"][0] if results["documents"] else []
