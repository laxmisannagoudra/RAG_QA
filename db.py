"""
db.py  -  SQLite part of the project (your "SQL" story).

Three tables:
  documents : one row per ingested file
  chunks    : one row per text chunk (metadata + text)
  queries   : log of every question asked
"""
import os
import sqlite3
from datetime import datetime

DB_PATH = "data/metadata.db"


def get_conn():
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT UNIQUE,
            num_chunks INTEGER,
            ingested_at TEXT
        )""")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            chunk_id TEXT PRIMARY KEY,
            file_name TEXT,
            chunk_index INTEGER,
            text TEXT
        )""")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            answer TEXT,
            asked_at TEXT
        )""")
    conn.commit()
    conn.close()


def save_document(file_name, chunks):
    """Replace any old data for this file with the new chunks."""
    init_db()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM chunks WHERE file_name = ?", (file_name,))
    cur.execute("DELETE FROM documents WHERE file_name = ?", (file_name,))
    cur.execute(
        "INSERT INTO documents (file_name, num_chunks, ingested_at) VALUES (?, ?, ?)",
        (file_name, len(chunks), datetime.now().isoformat(timespec="seconds")),
    )
    for i, text in enumerate(chunks):
        cur.execute(
            "INSERT INTO chunks (chunk_id, file_name, chunk_index, text) VALUES (?, ?, ?, ?)",
            (f"{file_name}::{i}", file_name, i, text),
        )
    conn.commit()
    conn.close()


def list_documents():
    init_db()
    conn = get_conn()
    rows = conn.execute(
        "SELECT file_name, num_chunks, ingested_at FROM documents ORDER BY ingested_at DESC"
    ).fetchall()
    conn.close()
    return rows


def log_query(question, answer):
    init_db()
    conn = get_conn()
    conn.execute(
        "INSERT INTO queries (question, answer, asked_at) VALUES (?, ?, ?)",
        (question, answer, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()


def recent_queries(limit=10):
    init_db()
    conn = get_conn()
    rows = conn.execute(
        "SELECT question, asked_at FROM queries ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return rows


def chunks_per_file():
    """A small GROUP BY query - good to mention in interviews."""
    init_db()
    conn = get_conn()
    rows = conn.execute(
        "SELECT file_name, COUNT(*) AS total_chunks FROM chunks GROUP BY file_name"
    ).fetchall()
    conn.close()
    return rows
