# RAG Engine — Multi-Source Retrieval Augmented Generation

A **Retrieval-Augmented Generation (RAG)** engine that ingests data from **PDFs, images, and URLs**, stores embeddings in **ChromaDB**, and answers questions using **Groq LLMs**.

## Features

- **Multi-source ingestion**: PDF files (text + embedded images), images (via Groq vision model), and web URLs
- **Vector search**: Local embeddings via `sentence-transformers` (`all-MiniLM-L6-v2`) stored in ChromaDB
- **LLM-powered Q&A**: Uses Groq's Llama models to answer questions from retrieved context
- **Source tracking**: Answers include references to source documents with relevance scores

## Architecture

```
User Question → Embed → ChromaDB Search → Retrieved Chunks → Context Building → Groq LLM → Answer
```

**Data flow:**
1. **Ingestion** — `ingest.py` processes files in `documents/` or URLs
   - PDFs → text extraction (PyMuPDF) + image description (Groq vision) → chunking
   - Images → base64 → Groq vision model → text description
   - URLs → HTTP fetch → BeautifulSoup parsing → text extraction → chunking
2. **Embedding** — `sentence-transformers` converts chunks into 384-dim vectors
3. **Storage** — ChromaDB (persistent, local) stores vectors + metadata
4. **Retrieval** — User question → embed → cosine similarity search → top-k chunks
5. **Generation** — Retrieved context + question → Groq Llama → final answer

## Setup

### Prerequisites
- Python 3.12+
- [Groq API key](https://console.groq.com)

### Installation

```bash
git clone <repo-url>
cd RAG-final
python -m venv venv

# Windows
.\venv\Scripts\Activate

# Linux/macOS
# source venv/bin/activate

pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```
GROQ_API_KEY=gsk_your_key_here
```

Key settings in `config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `GROQ_TEXT_MODEL` | `llama-3.3-70b-versatile` | LLM for answering |
| `GROQ_VISION_MODEL` | `meta-llama/llama-4-scout-17b-16e-instruct` | Vision model for images |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Local embedding model |
| `CHROMA_DIR` | `./chroma_db` | Vector store location |
| `TOP_K` | `3` | Chunks retrieved per query |
| `CHUNK_SIZE` | `400` | Characters per chunk |

## Usage

### 1. Ingest documents

Place PDFs and images (`.jpg`, `.jpeg`, `.png`, `.webp`) in the `documents/` folder, then:

```bash
python ingest.py
```

Or ingest a URL:

```bash
python ingest.py url "https://example.com"
```

### 2. Ask questions

Start interactive mode:

```bash
python ask.py
```

Or ask a single question:

```bash
python ask.py "What are the sales trends shown in the image?"
```

Example output:

```
============================================================
ANSWER
============================================================
Based on the chart, revenue increased by 15% in Q3 2024...

------------------------------------------------------------
SOURCES (2 chunks used)
------------------------------------------------------------
1. sales-report.pdf - page 3 [score: 0.921]
2. Image: sales-trend-losses.png [score: 0.876]
```

### Utility

```python
from vectorstore.chroma_store import count, clear

count()   # returns total chunks in DB
clear()   # wipes the database
```

## Project Structure

```
├── ingest.py                  # Ingestion entry point
├── ask.py                     # Q&A entry point (interactive + single-query)
├── config.py                  # Configuration & environment
├── requirements.txt           # Dependencies
├── .env                       # API keys (not tracked)
├── documents/                 # Place PDFs & images here
├── chroma_db/                 # Persistent vector store (auto-created)
│
├── ingestion/
│   ├── pdf_processor.py       # PDF text + embedded image extraction
│   ├── image_processor.py     # Image → Groq vision → description
│   └── url_processor.py       # URL → fetch → parse → clean → chunk
│
├── embeddings/
│   └── embedder.py            # sentence-transformers wrapper
│
├── vectorstore/
│   └── chroma_store.py        # ChromaDB CRUD operations
│
├── retreival/
│   └── retreiver.py           # Search + context building logic
│
└── generation/
    └── generator.py           # Groq LLM call for final answer
```

## Dependencies

| Package | Purpose |
|---------|---------|
| `groq` | Groq API client for LLM & vision |
| `chromadb` | Local vector database |
| `sentence-transformers` | Text → embedding model |
| `pymupdf` | PDF text & image extraction |
| `Pillow` | Image loading & preprocessing |
| `requests` | HTTP client for URLs |
| `beautifulsoup4` | HTML parsing for URL ingestion |
| `lxml` | Fast HTML/XML parser for BeautifulSoup |
| `python-dotenv` | `.env` file loading |

## UI (Coming Soon)

A Streamlit-based user interface is planned to provide a web GUI for document upload, URL ingestion, and interactive Q&A.
