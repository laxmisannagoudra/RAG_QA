"""
rag.py  -  the question answering part.

RAG = Retrieval Augmented Generation
  1. RETRIEVE the most relevant chunks for the question
  2. AUGMENT a prompt with those chunks as context
  3. GENERATE an answer with an LLM

If no ANTHROPIC_API_KEY is set, the app still works: it just shows the
retrieved chunks instead of a written answer.
"""
import os

import db
import vector_store


def build_prompt(question, chunks):
    context = "\n\n".join(
        f"[Source: {c['file_name']}, chunk {c['chunk_index']}]\n{c['text']}" for c in chunks
    )
    return (
        "Answer the question using ONLY the context below. "
        "If the answer is not in the context, say you don't know.\n\n"
        f"Context:\n{context}\n\nQuestion: {question}"
    )


def generate_answer(question, chunks):
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        top = chunks[0]["text"]
        return ("(No API key set, showing the best matching passage instead)\n\n" + top)

    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": build_prompt(question, chunks)}],
    )
    return response.content[0].text


def ask(question, k=3):
    chunks = vector_store.search(question, k)
    if not chunks:
        return "No documents found. Please ingest some documents first.", []
    answer = generate_answer(question, chunks)
    db.log_query(question, answer)
    return answer, chunks


if __name__ == "__main__":
    # Quick command-line test:  python rag.py
    q = input("Ask a question: ")
    ans, sources = ask(q)
    print("\nANSWER:\n", ans)
    print("\nSOURCES:")
    for s in sources:
        print(f" - {s['file_name']} (chunk {s['chunk_index']})")
