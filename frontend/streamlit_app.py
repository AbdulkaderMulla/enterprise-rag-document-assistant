import requests
import streamlit as st

API_URL = st.sidebar.text_input("FastAPI URL", "http://localhost:8000")

st.set_page_config(
    page_title="Enterprise RAG Assistant",
    page_icon="📚",
    layout="wide",
)

st.title("📚 Enterprise RAG Document Intelligent Assistant")
st.caption("Upload documents, build a searchable knowledge base, and ask questions.")

uploaded = st.file_uploader(
    "Upload PDF, TXT, or DOCX",
    type=["pdf", "txt", "docx"],
)

if uploaded and st.button("Index Document"):
    with st.spinner("Indexing document..."):
        response = requests.post(
            f"{API_URL}/documents",
            files={"file": (uploaded.name, uploaded.getvalue())},
            timeout=120,
        )
    if response.ok:
        st.success(response.json()["message"])
        st.json(response.json())
    else:
        st.error(response.text)

st.divider()

question = st.text_area(
    "Ask a question about your indexed documents",
    placeholder="What are the key requirements described in the document?",
)

if st.button("Ask") and question.strip():
    with st.spinner("Searching documents and generating answer..."):
        response = requests.post(
            f"{API_URL}/ask",
            json={"question": question},
            timeout=120,
        )
    if response.ok:
        data = response.json()
        st.subheader("Answer")
        st.write(data["answer"])
        st.subheader("Sources")
        for source in data["sources"]:
            st.write(f"- {source}")
    else:
        st.error(response.text)
