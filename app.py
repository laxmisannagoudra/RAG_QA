"""
app.py  -  simple web UI using Streamlit.
Run with:   streamlit run app.py
"""
import os
import streamlit as st

import db
import ingest
import rag

st.set_page_config(page_title="Mini RAG Q&A Bot", page_icon="📄")
st.title("📄 Mini RAG Document Q&A Bot")

# ---------- Sidebar: upload + ingest ----------
with st.sidebar:
    st.header("1. Add documents")
    uploaded = st.file_uploader("Upload PDF / TXT / MD", type=["pdf", "txt", "md"],
                                accept_multiple_files=True)
    if st.button("Ingest uploaded files") and uploaded:
        os.makedirs(ingest.DOCS_FOLDER, exist_ok=True)
        for f in uploaded:
            path = os.path.join(ingest.DOCS_FOLDER, f.name)
            with open(path, "wb") as out:
                out.write(f.getbuffer())
            n = ingest.ingest_file(path)
            st.success(f"{f.name}: {n} chunks stored")

    if st.button("Ingest everything in docs/ folder"):
        total = ingest.ingest_folder()
        st.success(f"{total} chunks stored")

    st.header("Stored documents (from SQLite)")
    docs = db.list_documents()
    if docs:
        for name, n, when in docs:
            st.write(f"• **{name}** ({n} chunks)")
    else:
        st.info("Nothing ingested yet.")

# ---------- Main: ask questions ----------
st.header("2. Ask a question")
question = st.text_input("Your question")

if st.button("Get answer") and question.strip():
    with st.spinner("Searching documents..."):
        answer, sources = rag.ask(question)
    st.subheader("Answer")
    st.write(answer)
    if sources:
        st.subheader("Sources")
        for s in sources:
            with st.expander(f"{s['file_name']} - chunk {s['chunk_index']}"):
                st.write(s["text"])

with st.expander("Recent questions (from SQLite)"):
    for q, when in db.recent_queries():
        st.write(f"{when}  -  {q}")
