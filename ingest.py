"""
ingest.py  -  the ETL pipeline.

  EXTRACT   : read text from PDF / TXT / MD files
  TRANSFORM : clean the text and split it into overlapping chunks
  LOAD      : store chunks in ChromaDB (vectors) and SQLite (metadata)

Run from terminal:   python ingest.py
"""
import os
import re
from pypdf import PdfReader

import db
import vector_store

DOCS_FOLDER = "docs"


# ---------- EXTRACT ----------
def extract_text(path):
    if path.lower().endswith(".pdf"):
        reader = PdfReader(path)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


# ---------- TRANSFORM ----------
def clean_text(text):
    # Replace many spaces/newlines with a single space
    return re.sub(r"\s+", " ", text).strip()


def chunk_text(text, size=800, overlap=150):
    """Split text into pieces of `size` characters.
    Each chunk overlaps the previous one by `overlap` characters
    so we don't cut a sentence's meaning in half."""
    chunks = []
    start = 0
    while start < len(text):
        piece = text[start:start + size].strip()
        if piece:
            chunks.append(piece)
        start += size - overlap
    return chunks


# ---------- LOAD ----------
def ingest_file(path):
    file_name = os.path.basename(path)
    text = clean_text(extract_text(path))
    chunks = chunk_text(text)
    if not chunks:
        print(f"[skip] {file_name}: no text found")
        return 0
    vector_store.add_chunks(file_name, chunks)   # vectors -> ChromaDB
    db.save_document(file_name, chunks)          # metadata -> SQLite
    print(f"[ok]   {file_name}: {len(chunks)} chunks stored")
    return len(chunks)


def ingest_folder(folder=DOCS_FOLDER):
    os.makedirs(folder, exist_ok=True)
    total = 0
    for name in sorted(os.listdir(folder)):
        if name.lower().endswith((".pdf", ".txt", ".md")):
            total += ingest_file(os.path.join(folder, name))
    return total


if __name__ == "__main__":
    count = ingest_folder()
    print(f"\nDone. {count} chunks stored in total.")
