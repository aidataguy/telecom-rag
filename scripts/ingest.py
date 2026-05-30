import os
import json
import glob
import time
from tqdm import tqdm
from dotenv import load_dotenv
import chromadb
import ollama
import argparse

print(f"Working directory: {os.getcwd()}")
print(f".env exists: {os.path.exists('.env')}")

load_dotenv(override=True)

OLLAMA_URL    = os.getenv("OLLAMA_BASE_URL")
if not OLLAMA_URL:
    raise ValueError("❌ OLLAMA_BASE_URL not set in .env file")
EMBED_MODEL   = os.getenv("EMBED_MODEL", "nomic-embed-text")
PERSIST_DIR   = os.getenv("CHROMA_PERSIST_DIR", "./data/vectorstore")
COLLECTION    = os.getenv("COLLECTION_NAME", "telecom_ops")
CHUNK_SIZE    = int(os.getenv("CHUNK_SIZE", 512))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 64))

print(f"Connecting to Ollama at: {OLLAMA_URL}")
try:
    _ollama_client = ollama.Client(host=OLLAMA_URL, timeout=120.0)
    _ollama_client.list()
    print("✅ Ollama connection successful")
except Exception as e:
    print(f"❌ Ollama connection failed: {e}")
    exit(1)


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + size
        chunks.append(" ".join(words[start:end]))
        start += size - overlap
    return chunks


def embed(text: str, retries: int = 3) -> list[float]:
    for attempt in range(retries):
        try:
            resp = _ollama_client.embed(model=EMBED_MODEL, input=text)
            return resp.embeddings[0]
        except Exception as e:
            if attempt < retries - 1:
                print(f"\n⚠️  Embed failed (attempt {attempt+1}), retrying in 3s... {e}")
                time.sleep(3)
            else:
                raise


def ingest(raw_dir: str = "data/raw"):
    chroma = chromadb.PersistentClient(path=PERSIST_DIR)
    collection = chroma.get_or_create_collection(
        name=COLLECTION,
        metadata={"hnsw:space": "cosine"}
    )

    files = glob.glob(os.path.join(raw_dir, "*.jsonl"))
    print(f"Found {len(files)} batch files to ingest")

    total_chunks = 0

    for fpath in tqdm(files, desc="Files"):
        with open(fpath) as f:
            docs = [json.loads(line) for line in f]

        for doc in tqdm(docs, desc="Docs", leave=False):
            chunks = chunk_text(doc["content"])

            for idx, chunk in enumerate(chunks):
                chunk_id = f"{doc['doc_id']}_{idx}"
                vector = embed(chunk)

                collection.add(
                    ids=[chunk_id],
                    embeddings=[vector],
                    documents=[chunk],
                    metadatas=[{
                        **doc["metadata"],
                        "doc_id": doc["doc_id"],
                        "doc_type": doc["doc_type"],
                        "title": doc["title"],
                        "chunk_index": idx
                    }]
                )
                total_chunks += 1

    print(f"\nIngestion complete. Total chunks stored: {total_chunks:,}")


if __name__ == "__main__":
    import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=str, default="data/raw")
    args = parser.parse_args()
    ingest(raw_dir=args.raw_dir)
