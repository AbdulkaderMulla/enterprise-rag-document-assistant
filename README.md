# Enterprise RAG Document Intelligent Assistant

A portfolio-ready Retrieval-Augmented Generation (RAG) application for asking questions over enterprise documents.

## Features

- PDF, TXT and DOCX ingestion
- Recursive document chunking
- Google Gemini embeddings
- FAISS vector search
- Gemini-powered answer generation
- Source filename reporting
- FastAPI backend
- Streamlit user interface
- Environment-variable based secrets

## Architecture

```text
Document
   ↓
Loader
   ↓
Chunking
   ↓
Gemini Embeddings
   ↓
FAISS Vector Store
   ↓
Semantic Retrieval
   ↓
Gemini LLM
   ↓
Answer + Sources
```

## Setup

```bash
git clone https://github.com/AbdulkaderMulla/enterprise-rag-document-assistant.git
cd enterprise-rag-document-assistant

python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate  # Windows

pip install -r requirements.txt
cp .env.example .env
```

Add your Gemini API key to `.env`.

## Run the API

```bash
uvicorn app.main:app --reload
```

API documentation: `http://localhost:8000/docs`

## Run Streamlit

In another terminal:

```bash
streamlit run frontend/streamlit_app.py
```

## Example API flow

Upload a document:

```bash
curl -X POST http://localhost:8000/documents \
  -F "file=@data/sample_documents/sample.txt"
```

Ask a question:

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What is this document about?"}'
```

## Security Notes

Never commit `.env` or API keys. The repository intentionally includes `.env.example` instead.

## Portfolio Description

**Enterprise RAG Document Intelligent Assistant** — Built a document question-answering system using Retrieval-Augmented Generation, Gemini embeddings, FAISS vector search, LangChain, FastAPI, and Streamlit. Implemented document ingestion, chunking, semantic retrieval, grounded response generation, and source tracking for enterprise knowledge access.
