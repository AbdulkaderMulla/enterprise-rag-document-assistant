import requests
import streamlit as st

st.set_page_config(
    page_title="Enterprise RAG Assistant",
    page_icon="📚",
    layout="wide",
)

API_URL = st.sidebar.text_input("FastAPI URL", "http://localhost:8000")

st.title("📚 Enterprise RAG Document Intelligent Assistant")
st.caption("Upload documents, build a searchable knowledge base, and ask questions.")

uploaded = st.file_uploader(
    "Upload PDF, TXT, or DOCX",
    type=["pdf", "txt", "docx"],
)

if uploaded and st.button("Index Document"):
    with st.spinner("Indexing document..."):
        try:
            response = requests.post(
                f"{API_URL}/documents",
                files={"file": (uploaded.name, uploaded.getvalue())},
                timeout=120,
            )
            response.raise_for_status()
            st.success(response.json()["message"])
            st.json(response.json())
        except requests.RequestException as exc:
            st.error(f"API request failed: {exc}")

st.divider()

question = st.text_area(
    "Ask a question about your indexed documents",
    placeholder="What are the key requirements described in the document?",
)

if st.button("Ask") and question.strip():
    with st.spinner("Searching documents and generating answer..."):
        try:
            response = requests.post(
                f"{API_URL}/ask",
                json={"question": question},
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()
            st.subheader("Answer")
            st.write(data["answer"])
            st.subheader("Sources")
            for source in data["sources"]:
                st.write(f"- {source}")
        except requests.RequestException as exc:
            st.error(f"API request failed: {exc}")
