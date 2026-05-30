import os
import ollama
import chromadb
from dotenv import load_dotenv
from typing import Generator

load_dotenv()

OLLAMA_URL  = os.getenv("OLLAMA_BASE_URL")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
CHAT_MODEL  = os.getenv("CHAT_MODEL", "llama3.2:3b")
PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/vectorstore")
COLLECTION  = os.getenv("COLLECTION_NAME", "telecom_ops")

_client     = ollama.Client(host=OLLAMA_URL)
_chroma     = chromadb.PersistentClient(path=PERSIST_DIR)
_collection = _chroma.get_collection(COLLECTION)


def retrieve(query: str, top_k: int = 10) -> list[dict]:
    vec = _client.embed(model=EMBED_MODEL, input=query).embeddings[0]

    # First try: operational docs only (incidents + runbooks)
    results = _collection.query(
        query_embeddings=[vec],
        n_results=top_k,
        where={"doc_type": {"$in": [
            "incident_report",
            "runbook",
            "root_cause_analysis",
        ]}}
    )

    docs = []
    for i in range(len(results["ids"][0])):
        distance = results["distances"][0][i]
        if distance < 0.7:
            docs.append({
                "chunk": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": round(distance, 4)
            })

    # Fallback: if not enough results, broaden to standards docs
    if len(docs) < 2:
        results = _collection.query(
            query_embeddings=[vec],
        n_results=top_k,
            where={"doc_type": {"$in": [
                "telecom_standards_qa",
                "oran_qa",
                "network_troubleshooting_qa"
            ]}}
        )
        for i in range(len(results["ids"][0])):
            distance = results["distances"][0][i]
            if distance < 0.5:
                docs.append({
                    "chunk": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": round(distance, 4)
                })

    return docs[:5]

def build_prompt(query: str, context_docs: list[dict]) -> str:
    context = "\n\n---\n\n".join([
        f"[{d['metadata'].get('doc_type', 'doc').upper()}] {d['metadata'].get('title', '')}\n{d['chunk']}"
        for d in context_docs
    ])
    return f"""You are TelecomOps Assistant, an expert in telecom network operations.
Use ONLY the context below to answer the question. If the answer is not in the context, say so.

CONTEXT:
{context}

QUESTION: {query}

ANSWER:"""


def rag_query(query: str, top_k: int = 5) -> dict:
    docs = retrieve(query, top_k)
    prompt = build_prompt(query, docs)
    response = _client.generate(model=CHAT_MODEL, prompt=prompt, stream=False)
    return {
        "answer": response["response"],
        "sources": [d["metadata"] for d in docs],
        "query": query
    }

def rag_streamer(query:str, top_k: int = 5)-> Generator[str, None, None]:
    """Stream my RAGGGGG response, ofcourse by token 😂 """
    docs = retrieve(query, top_k)
    prompt = build_prompt(query, docs)

    for chunk in _client.generate(
        model = CHAT_MODEL,
        prompt = prompt,
        stream = True
    ):
        token=chunk.get("response", "")
        if token:
            yield token


