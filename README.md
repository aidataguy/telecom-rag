# 🛰️ TelecomOps RAG — Local AI Knowledge Assistant

> A fully local, GPU-powered Retrieval-Augmented Generation (RAG) system for Telecom Network Operations — built on Ollama, ChromaDB, and FastAPI. No cloud. No API keys. No data leaving your network.

---

## 😤 The Problem This Solves

If you work in telecom network operations, you already know this pain:

### 🔥 During a P1 Incident at 2AM
- You're staring at an alarm you've seen before — but **where is that runbook?**
- You search SharePoint, Confluence, email threads, old tickets
- You ask colleagues who are half-asleep
- **Every minute of downtime costs money** — thousands of subscribers affected
- By the time you find the resolution steps, 45 minutes have passed

### 📚 The Knowledge Silo Problem
- Experienced engineers leave → **institutional knowledge walks out the door**
- Runbooks exist but are **scattered across 6 different systems**
- Incident reports are written but **never referenced again**
- New engineers take **months to ramp up** on network-specific procedures
- Every team reinvents the wheel on the same recurring issues

### 🔒 The Cloud AI Problem
- You can't paste sensitive network configs into ChatGPT
- Vendor names, topology details, subscriber data — **all confidential**
- Your company's security policy **blocks cloud AI tools**
- Even if allowed, cloud AI **doesn't know your specific network**

### ✅ What TelecomOps RAG Does Instead

| Old Way | With TelecomOps RAG |
|---|---|
| Search 6 tools during an incident | Ask one question, get the answer in seconds |
| Knowledge locked in senior engineers' heads | Captured in a searchable, queryable knowledge base |
| Copy-paste configs into ChatGPT (security risk) | Runs 100% locally, data never leaves your network |
| New engineer ramp-up: 3-6 months | Self-serve answers from day one |
| Post-incident reports filed and forgotten | Every incident becomes searchable institutional memory |
| Vendor runbooks buried in PDFs | Instantly retrievable by natural language query |

### 💰 Who Should Use This

- **Telecom NOC teams** — faster incident resolution, consistent procedures
- **Network engineers** — instant access to relevant runbooks during changes
- **AI/ML architects** — reference implementation for enterprise RAG on private infra
- **Telecom vendors & SIs** — deployable knowledge base for client engagements
- **Anyone** who has confidential operational data they can't send to the cloud

> 🎯 **Bottom line:** If your team has ever spent more than 10 minutes searching for how to fix something that was already fixed before — this tool pays for itself in the first incident.

---

## 🧠 What Is This?

**TelecomOps RAG** is an intelligent assistant that answers questions about telecom network operations using your own internal knowledge base — incident reports, runbooks, capacity plans, and more.

Ask it things like:
- *"How do I resolve a BGP session down alarm on eNodeB?"*
- *"What are the steps for Nokia 5G NR site commissioning?"*
- *"What caused the P1 incident on the North region last quarter?"*

And it answers using **your data**, running entirely on **your local hardware**.

---

## 🏗️ Architecture

```
Your Question
     │
     ▼
[Mac — FastAPI]          [Windows Machine]
  RAG Engine     ──────►   Ollama Server
  ChromaDB                  mistral:7b
  (Vector Store)            nomic-embed-text
                            RTX 3050 GPU
```

| Component | Role |
|---|---|
| **Ollama** | Local LLM inference (Windows, RTX 3050) |
| **mistral:7b-instruct-q4_0** | Chat / RAG response generation |
| **nomic-embed-text** | Text embeddings for semantic search |
| **ChromaDB** | Vector database (persisted to disk) |
| **FastAPI** | REST API for querying the RAG system |
| **Python scripts** | Synthetic data generation + ingestion |

---

## 📁 Project Structure

```
telecom-rag/
├── app/
│   ├── api/
│   │   └── routes.py               # FastAPI endpoints
│   ├── core/
│   │   └── rag.py                  # RAG logic (retrieve + generate)
│   └── models/                     # Pydantic schemas
├── data/
│   ├── raw/                        # Synthetic JSONL files
│   │   └── huggingface/            # HuggingFace dataset JSONL files
│   ├── processed/                  # Chunked documents
│   └── vectorstore/                # ChromaDB persistence
├── scripts/
│   ├── generate_data.py            # Synthetic telecom data generator
│   ├── ingest_huggingface.py       # HuggingFace dataset fetcher
│   └── ingest.py                   # Chunk + embed + store pipeline
├── main.py                         # App entrypoint
├── .env                            # Config (never commit this)
└── requirements.txt
```

---

## ⚙️ Prerequisites

### Windows Machine (Ollama Server)
- Windows 10/11
- NVIDIA RTX 3050 (4GB VRAM) or better
- NVIDIA drivers installed (`nvidia-smi` must work)
- [Ollama](https://ollama.com/download/windows) installed

### Mac / Dev Machine
- Python 3.10+
- pip
- Same local network as the Windows machine

---

## 🚀 Setup Guide

### Step 1 — Start Ollama on Windows

Open PowerShell and run:

```powershell
$env:OLLAMA_HOST = "0.0.0.0:11434"
$env:OLLAMA_KEEP_ALIVE = "-1"
ollama serve
```

> 💡 Keep this window open while working. The `0.0.0.0` binding makes Ollama accessible from your Mac over the network.

### Step 2 — Pull Models on Windows

Open a second PowerShell window:

```powershell
$env:OLLAMA_HOST = "0.0.0.0:11434"
ollama pull mistral:7b-instruct-q4_0
ollama pull nomic-embed-text
ollama list   # verify both appear
```

### Step 3 — Verify Connection from Mac

```bash
# Replace with your Windows machine's LAN IP
curl http://192.168.0.x:11434/api/tags
```

✅ You should see a JSON response with your models listed.

### Step 4 — Clone & Setup on Mac

```bash
git clone <your-repo-url> telecom-rag
cd telecom-rag
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 5 — Configure `.env`

Create a `.env` file in the project root:

```env
OLLAMA_BASE_URL=http://192.168.0.x:11434
EMBED_MODEL=nomic-embed-text
CHAT_MODEL=mistral:7b-instruct-q4_0
CHROMA_PERSIST_DIR=./data/vectorstore
COLLECTION_NAME=telecom_ops
CHUNK_SIZE=512
CHUNK_OVERLAP=64
```

> ⚠️ Replace `192.168.0.x` with your actual Windows machine IP (`ipconfig` on Windows to find it).

### Step 6 — Generate Synthetic Training Data

```bash
# Generate 100,000 telecom documents (incidents, runbooks, capacity reports)
python scripts/generate_data.py --records 100000 --output data/raw

# Scale up to 1 million when ready
python scripts/generate_data.py --records 1000000 --output data/raw
```

### Step 7 — Fetch Public Telecom Datasets (HuggingFace)

In addition to synthetic data, pull real telecom domain knowledge from HuggingFace:

```bash
pip install datasets
python scripts/ingest_huggingface.py
```

This downloads and converts three datasets into JSONL format:

| Dataset | Content | Records |
|---|---|---|
| `TeleQnA` | Real telecom Q&A pairs | ~10K |
| `telecom-llm-dataset` | Instruction-response pairs | ~5K |
| `3gpp-qa` | 3GPP specification Q&A | ~3K |

Files are saved to `data/raw/huggingface/`.

### Step 8 — Ingest Everything into Vector Store

```bash
# Ingest synthetic data
python scripts/ingest.py

# Ingest HuggingFace datasets
python scripts/ingest.py --raw-dir data/raw/huggingface
```

Each ingest run will:
1. Read all `.jsonl` files from the target folder
2. Chunk each document into 512-word overlapping chunks
3. Embed each chunk using `nomic-embed-text` via Ollama
4. Store embeddings in ChromaDB

> ⏳ For 100K records expect ~30-60 mins. For 1M records, run overnight.

### Step 8a — Verify Vector Store

After ingestion, confirm everything made it in:

```bash
python3 -c "
import chromadb
client = chromadb.PersistentClient(path='./data/vectorstore')
col = client.get_collection('telecom_ops')
print(f'Total chunks in vector store: {col.count():,}')
"
```

You should see a large number confirming all chunks are stored.

### Step 9 — Start the API

```bash
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Started reloader process
```

---

---

## 🔍 Usage

### Health Check

```bash
curl http://localhost:8000/health
```

### Query the RAG System

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I resolve high CPU utilization on a Nokia eNodeB?",
    "top_k": 5
  }'
```

### Sample Response

```json
{
  "query": "How do I resolve high CPU utilization on a Nokia eNodeB?",
  "answer": "Based on the incident reports, high CPU utilization on Nokia eNodeB is typically resolved by: 1) Restarting the affected process, 2) Checking for runaway threads using diagnostic scripts, 3) Applying the vendor hotfix if a known software bug is identified...",
  "sources": [
    {
      "doc_type": "incident_report",
      "title": "P1 Incident: High CPU utilization on NodeB [North]",
      "severity": "P1",
      "region": "North",
      "vendor": "Nokia"
    }
  ]
}
```

---

## 📊 Data Sources & Schema

### Synthetic Data (Generated Locally)

The synthetic data generator produces three document types:

| Type | Description | Share |
|---|---|---|
| `incident_report` | P1–P4 network incidents with RCA and resolution | 50% |
| `runbook` | Step-by-step operational procedures | 30% |
| `capacity_report` | Regional network capacity analysis | 20% |

Each document includes rich metadata: severity, region, vendor, technology (2G/3G/4G/5G), network element type, and timestamps.

### Public Datasets (HuggingFace)

| Dataset | Type | Content | Size |
|---|---|---|---|
| `netop-team/TeleQnA` | `telecom_qa` | Real telecom Q&A pairs | ~10K |
| `Vibashan/telecom-llm-dataset` | `telecom_instruction` | Instruction-response pairs | ~5K |
| `ShengbingZhang/3gpp-qa` | `3gpp_specification` | 3GPP spec-based Q&A | ~3K |

### Combined Knowledge Base

| Source | Records | Purpose |
|---|---|---|
| Synthetic generator | 100K–1M | Breadth — covers all scenarios |
| HuggingFace datasets | ~18K | Accuracy — real domain knowledge |
| **Total** | **100K–1M+** | **Production-grade RAG** |

---

## 🎛️ Configuration Reference

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | — | Ollama server URL (required) |
| `EMBED_MODEL` | `nomic-embed-text` | Embedding model |
| `CHAT_MODEL` | `mistral:7b-instruct-q4_0` | Chat/generation model |
| `CHROMA_PERSIST_DIR` | `./data/vectorstore` | ChromaDB storage path |
| `COLLECTION_NAME` | `telecom_ops` | ChromaDB collection name |
| `CHUNK_SIZE` | `512` | Words per chunk |
| `CHUNK_OVERLAP` | `64` | Overlap between chunks |

---

## 🤖 Supported Models (tested on RTX 3050 4GB)

| Model | VRAM | Quality | Use For |
|---|---|---|---|
| `mistral:7b-instruct-q4_0` | ~3.8GB | ⭐⭐⭐⭐⭐ | Primary RAG |
| `qwen3:4b` | ~3.5GB | ⭐⭐⭐⭐ | Alternative |
| `llama3.2:3b` | ~2.0GB | ⭐⭐⭐ | Fast fallback |
| `phi4-mini` | ~3.2GB | ⭐⭐⭐⭐ | Structured output |
| `nomic-embed-text` | ~274MB | ⭐⭐⭐⭐⭐ | Embeddings only |

---

## 🛠️ Troubleshooting

### Ollama not reachable from Mac
```bash
# Check Ollama is bound to 0.0.0.0 (not 127.0.0.1)
# On Windows:
netstat -ano | findstr 11434
# Must show 0.0.0.0:11434, not 127.0.0.1:11434

# Add Windows Firewall rule if curl times out:
netsh advfirewall firewall add rule name="Ollama API" dir=in action=allow protocol=TCP localport=11434
```

### Ollama stops after inactivity
```powershell
# Always start with KEEP_ALIVE=-1
$env:OLLAMA_KEEP_ALIVE = "-1"
ollama serve
```

### `.env` values not loading
```bash
# Check for typos in variable names
cat -A .env

# Verify Python sees the values
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(override=True); print(os.getenv('OLLAMA_BASE_URL'))"
```

### Embedding timeout during ingest
- Increase `timeout` in `ingest.py` embed function to `120.0`
- Ensure Ollama has `nomic-embed-text` pulled: `ollama list`
- Check Windows machine didn't go to sleep

### Out of VRAM during inference
- Switch to a smaller model: `llama3.2:3b` or `qwen3:1.7b`
- Never run batch_size > 1 during fine-tuning on 4GB GPU

---

## 🗺️ Roadmap

- [x] Synthetic data generation (incidents, runbooks, capacity reports)
- [x] HuggingFace public telecom datasets (TeleQnA, 3GPP QA, Telecom LLM)
- [x] Embedding + ChromaDB ingestion pipeline
- [x] FastAPI RAG query endpoint
- [ ] Streaming responses
- [ ] Web UI (React frontend)
- [ ] QLoRA fine-tuning on telecom domain data
- [ ] Multi-collection support (per client/project)
- [ ] Evaluation harness (RAGAS metrics)
- [ ] Docker Compose setup

---

## 👨‍💻 Author

Built by **Himanshu Patel** — AI/ML Architect  
Pune, India 🇮🇳  
Domain: Telecom • Healthcare • Enterprise AI

---

## 📄 License

MIT License — use freely, build something great.
