import os
import json
import uuid
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv
from datasets import load_dataset

load_dotenv(override=True)

OUTPUT_DIR = "data/raw/huggingface"
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


def save_jsonl(records: list, filename: str):
    out_path = os.path.join(OUTPUT_DIR, filename)
    with open(out_path, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    print(f"✅ Saved {len(records):,} records → {out_path}")



# ── Dataset 2: GSMA ot-full — TeleLogs (5G Root Cause Analysis) ──────────────
def fetch_telelogs():
    print("\n📡 Fetching TeleLogs (5G Root Cause Analysis)...")
    try:
        ds = load_dataset("GSMA/ot-full", "telelogs", split="test")
        records = []
        for row in tqdm(ds, desc="TeleLogs"):
            records.append({
                "doc_id": str(uuid.uuid4()),
                "doc_type": "root_cause_analysis",
                "title": f"5G RCA: {str(row.get('question', ''))[:80]}",
                "content": f"ROOT CAUSE ANALYSIS\n\nQUESTION:\n{row.get('question', '')}\n\nANSWER:\n{row.get('answer', '')}\n\nCONTEXT:\n{row.get('context', '')}",
                "metadata": {
                    "source": "GSMA-TeleLogs",
                    "created_at": "2024-01-01T00:00:00"
                }
            })
        save_jsonl(records, "telelogs.jsonl")
    except Exception as e:
        print(f"❌ TeleLogs failed: {e}")


# ── Dataset 3: GSMA ot-full — TeleQnA subset (Standards Q&A) ─────────────────
def fetch_gsma_teleqna():
    print("\n📡 Fetching GSMA TeleQnA (Standards & Specs)...")
    try:
        ds = load_dataset("GSMA/ot-full", "teleqna", split="test")
        records = []
        for row in tqdm(ds, desc="GSMA TeleQnA"):
            records.append({
                "doc_id": str(uuid.uuid4()),
                "doc_type": "telecom_standards_qa",
                "title": f"Standards QA: {str(row.get('question', ''))[:80]}",
                "content": f"STANDARDS QUESTION:\n{row.get('question', '')}\n\nANSWER:\n{row.get('answer', '')}",
                "metadata": {
                    "source": "GSMA-TeleQnA",
                    "created_at": "2024-01-01T00:00:00"
                }
            })
        save_jsonl(records, "gsma_teleqna.jsonl")
    except Exception as e:
        print(f"❌ GSMA TeleQnA failed: {e}")


# ── Dataset 4: GSMA ot-full — O-RAN Bench ────────────────────────────────────
def fetch_oranbench():
    print("\n📡 Fetching O-RAN Benchmark dataset...")
    try:
        ds = load_dataset("GSMA/ot-full", "oranbench", split="test")
        records = []
        for row in tqdm(ds, desc="ORANBench"):
            records.append({
                "doc_id": str(uuid.uuid4()),
                "doc_type": "oran_qa",
                "title": f"O-RAN: {str(row.get('question', ''))[:80]}",
                "content": f"O-RAN QUESTION:\n{row.get('question', '')}\n\nANSWER:\n{row.get('answer', '')}",
                "metadata": {
                    "source": "GSMA-ORANBench",
                    "created_at": "2024-01-01T00:00:00"
                }
            })
        save_jsonl(records, "oranbench.jsonl")
    except Exception as e:
        print(f"❌ ORANBench failed: {e}")


# ── Dataset 5: ymoslem/TeleQnA-processed (clean version) ─────────────────────
def fetch_teleqna_processed():
    print("\n📡 Fetching TeleQnA Processed dataset...")
    try:
        ds = load_dataset("ymoslem/TeleQnA-processed", split="train")
        records = []
        for row in tqdm(ds, desc="TeleQnA-processed"):
            records.append({
                "doc_id": str(uuid.uuid4()),
                "doc_type": "telecom_qa_processed",
                "title": f"TeleQnA: {str(row.get('question', ''))[:80]}",
                "content": f"QUESTION:\n{row.get('question', '')}\n\nANSWER:\n{row.get('answer', '')}",
                "metadata": {
                    "source": "TeleQnA-processed",
                    "created_at": "2024-01-01T00:00:00"
                }
            })
        save_jsonl(records, "teleqna_processed.jsonl")
    except Exception as e:
        print(f"❌ TeleQnA-processed failed: {e}")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 Fetching telecom datasets from HuggingFace...\n")
    fetch_telelogs()
    fetch_gsma_teleqna()
    fetch_oranbench()
    fetch_teleqna_processed()

    print("\n🎉 Done! Files saved to data/raw/huggingface/")
    print("📂 Contents:")
    for f in Path(OUTPUT_DIR).glob("*.jsonl"):
        lines = sum(1 for _ in open(f))
        print(f"   {f.name}: {lines:,} records")
    print("\n👉 Next: uv run scripts/ingest.py --raw-dir data/raw/huggingface")
