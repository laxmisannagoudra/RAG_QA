# Mini RAG Document Q&A Bot

A small Retrieval Augmented Generation (RAG) app. Upload PDF/TXT documents,
ask questions, and get answers grounded in those documents.

## Architecture (ETL + RAG)

```
docs/ (PDF, TXT)
   │  EXTRACT   pypdf / file read
   ▼
clean + chunk text           TRANSFORM
   │
   ├──► ChromaDB (embeddings)  LOAD  ─┐
   └──► SQLite (metadata, logs)       │
                                      ▼
Question ──► retrieve top chunks ──► LLM ──► Answer + sources
```

## Tech stack
Python, ChromaDB, SQLite, pypdf, Streamlit, Anthropic API (optional)

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Optional (for written answers from an LLM):

```bash
export ANTHROPIC_API_KEY="your-key"     # Windows: set ANTHROPIC_API_KEY=your-key
```

## Run

```bash
python ingest.py          # loads docs/sample.txt (and any other files in docs/)
streamlit run app.py      # opens the web UI
```

Or test from the terminal: `python rag.py`

## Project structure

| File | Purpose |
|------|---------|
| ingest.py | ETL pipeline: extract, clean, chunk, load |
| vector_store.py | ChromaDB embeddings and similarity search |
| db.py | SQLite tables: documents, chunks, queries |
| rag.py | Retrieve, build prompt, generate answer |
| app.py | Streamlit UI |

## Possible improvements
- Better chunking (by sentence or paragraph)
- Support DOCX and web pages
- Show similarity scores
- Add unit tests
