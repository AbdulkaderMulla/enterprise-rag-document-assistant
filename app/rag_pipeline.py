from pathlib import Path
from typing import Iterable

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader,
)
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".docx"}


def load_file(path: str) -> list[Document]:
    p = Path(path)
    ext = p.suffix.lower()

    if ext == ".pdf":
        return PyPDFLoader(str(p)).load()
    if ext == ".txt":
        return TextLoader(str(p), encoding="utf-8").load()
    if ext == ".docx":
        return UnstructuredWordDocumentLoader(str(p)).load()

    raise ValueError(f"Unsupported file type: {ext}")


def chunk_documents(documents: Iterable[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    return splitter.split_documents(list(documents))


def build_vector_store(documents: list[Document]) -> FAISS:
    embeddings = GoogleGenerativeAIEmbeddings(
        model=settings.embedding_model,
        google_api_key=settings.google_api_key,
    )
    return FAISS.from_documents(documents, embeddings)


def save_vector_store(vector_store: FAISS) -> None:
    vector_store.save_local(settings.vector_store_dir)


def load_vector_store() -> FAISS:
    embeddings = GoogleGenerativeAIEmbeddings(
        model=settings.embedding_model,
        google_api_key=settings.google_api_key,
    )
    return FAISS.load_local(
        settings.vector_store_dir,
        embeddings,
        allow_dangerous_deserialization=True,
    )


def answer_question(vector_store: FAISS, question: str) -> tuple[str, list[Document]]:
    retriever = vector_store.as_retriever(search_kwargs={"k": settings.top_k})
    docs = retriever.invoke(question)

    context = "\n\n--- SOURCE ---\n\n".join(
        f"{doc.page_content}\nSource: {doc.metadata.get('source', 'unknown')}"
        for doc in docs
    )

    prompt = f"""
You are an enterprise document assistant.

Answer the user's question using only the supplied context.
If the context does not contain enough information, say that you do not have
enough information instead of inventing facts.

Context:
{context}

Question:
{question}

Give a clear, concise answer and mention the relevant source filenames.
"""

    llm = ChatGoogleGenerativeAI(
        model=settings.llm_model,
        google_api_key=settings.google_api_key,
        temperature=0.2,
    )
    response = llm.invoke(prompt)
    return response.content, docs
