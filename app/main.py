from pathlib import Path
import tempfile

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.rag_pipeline import (
    SUPPORTED_EXTENSIONS,
    answer_question,
    build_vector_store,
    chunk_documents,
    load_file,
    save_vector_store,
)

app = FastAPI(
    title="Enterprise RAG Document Intelligent Assistant",
    version="1.0.0",
)

VECTOR_STORE = None


class QuestionRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/documents")
async def upload_document(file: UploadFile = File(...)):
    global VECTOR_STORE

    ext = Path(file.filename or "").suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Supported files: PDF, TXT, DOCX",
        )

    contents = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(contents)
        temp_path = tmp.name

    try:
        documents = load_file(temp_path)
        chunks = chunk_documents(documents)
        if not chunks:
            raise HTTPException(status_code=400, detail="No text found in document.")

        if VECTOR_STORE is None:
            VECTOR_STORE = build_vector_store(chunks)
        else:
            VECTOR_STORE.add_documents(chunks)

        save_vector_store(VECTOR_STORE)

        return {
            "message": "Document indexed successfully",
            "filename": file.filename,
            "chunks_indexed": len(chunks),
        }
    finally:
        Path(temp_path).unlink(missing_ok=True)


@app.post("/ask")
def ask(request: QuestionRequest):
    global VECTOR_STORE

    if VECTOR_STORE is None:
        raise HTTPException(
            status_code=400,
            detail="Upload at least one document before asking a question.",
        )

    answer, docs = answer_question(VECTOR_STORE, request.question)

    sources = sorted(
        {Path(doc.metadata.get("source", "unknown")).name for doc in docs}
    )

    return {
        "answer": answer,
        "sources": sources,
    }
