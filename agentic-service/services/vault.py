"""Utilities for ingesting personal knowledge documents into FAISS."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Optional, Sequence, List, Dict, Any, Generator
import json

from fastapi import UploadFile
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from pypdf import PdfReader
from docx import Document
import openai

from config import settings


class VaultIngestionService:
    """Handles file storage, text extraction, chunking, and FAISS persistence."""

    def __init__(self) -> None:
        self.upload_dir = Path("data/uploads")
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        self.index_dir = Path(settings.faiss_index_path)
        self.index_dir.mkdir(parents=True, exist_ok=True)

        # Embedder + splitter reused across requests to avoid reload overhead.
        self.embedder = HuggingFaceEmbeddings(model_name=settings.hf_model_name)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=200,
        )

    def ingest_document(
        self,
        *,
        upload: UploadFile,
        document_id: str,
        user_id: str,
        title: str,
        notes: Optional[str] = None,
    ) -> dict:
        saved_path = self._persist_upload(upload, document_id)
        raw_text = self._extract_text(saved_path, upload.content_type)
        if not raw_text.strip():
            raise ValueError("Uploaded document does not contain extractable text.")

        chunks = self.splitter.split_text(raw_text)
        if not chunks:
            raise ValueError("Unable to generate chunks from uploaded document.")

        store = self._load_or_create_index()
        metadatas = [
            {
                "document_id": document_id,
                "user_id": user_id,
                "chunk_index": idx,
                "title": title,
                "notes": notes,
                "source_path": str(saved_path),
            }
            for idx in range(len(chunks))
        ]

        if store:
            store.add_texts(chunks, metadatas=metadatas)
        else:
            store = FAISS.from_texts(chunks, embedding=self.embedder, metadatas=metadatas)

        store.save_local(str(self.index_dir))
        token_estimate = math.ceil(len(raw_text) / 4)

        return {
            "documentId": document_id,
            "chunkCount": len(chunks),
            "tokenEstimate": token_estimate,
            "message": "Document ingested and indexed.",
        }

    def _persist_upload(self, upload: UploadFile, document_id: str) -> Path:
        target_path = self.upload_dir / f"{document_id}_{upload.filename or 'document'}"
        with target_path.open("wb") as destination:
            contents = upload.file.read()
            destination.write(contents)
        upload.file.seek(0)
        return target_path

    def _extract_text(self, path: Path, content_type: Optional[str]) -> str:
        suffix = path.suffix.lower()
        content_type = (content_type or "").lower()

        if "pdf" in content_type or suffix == ".pdf":
            return self._extract_pdf_text(path)

        if "wordprocessingml" in content_type or suffix == ".docx":
            return self._extract_docx_text(path)

        data = path.read_text(encoding="utf-8", errors="ignore")
        return data

    @staticmethod
    def _extract_pdf_text(path: Path) -> str:
        reader = PdfReader(str(path))
        text_segments: list[str] = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text_segments.append(page_text)
        return "\n".join(text_segments)

    @staticmethod
    def _extract_docx_text(path: Path) -> str:
        document = Document(str(path))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)

    def _load_or_create_index(self):
        index_files = list(self.index_dir.glob("*"))
        if index_files:
            return FAISS.load_local(
                str(self.index_dir),
                self.embedder,
            )
        return None

    def query_documents(
        self,
        query: str,
        user_id: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Query FAISS index for documents relevant to user's question.
        Filters results by user_id to ensure data isolation.
        """
        store = self._load_or_create_index()
        if not store:
            return []

        # Retrieve top results with scores
        results = store.similarity_search_with_score(query, k=top_k * 3)

        # Filter by user_id and format results
        filtered_results = []
        for doc, score in results:
            if doc.metadata.get("user_id") == user_id:
                filtered_results.append({
                    "text": doc.page_content,
                    "title": doc.metadata.get("title", "Unknown"),
                    "document_id": doc.metadata.get("document_id"),
                    "chunk_index": doc.metadata.get("chunk_index", 0),
                    "relevance_score": float(score),
                })
                if len(filtered_results) >= top_k:
                    break

        return filtered_results

    def generate_answer(
        self,
        query: str,
        user_id: str,
        top_k: int = 3,
    ) -> Dict[str, Any]:
        """
        RAG pipeline: retrieve relevant chunks, generate answer with OpenAI.
        Returns answer with citations.
        """
        # Retrieve relevant document chunks
        chunks = self.query_documents(query, user_id, top_k)

        if not chunks:
            return {
                "answer": "I don't have any documents in your Knowledge Vault yet. Please upload some travel guides or notes first!",
                "chunks": [],
                "citations": [],
            }

        # Build context from top chunks
        context_parts = []
        citations = []
        seen_docs = set()

        for idx, chunk in enumerate(chunks, 1):
            context_parts.append(f"[Source {idx}] {chunk['text']}")
            doc_key = (chunk["document_id"], chunk["title"])
            if doc_key not in seen_docs:
                citations.append({
                    "title": chunk["title"],
                    "document_id": chunk["document_id"],
                })
                seen_docs.add(doc_key)

        context = "\n\n".join(context_parts)

        # Generate answer with OpenAI
        client = openai.OpenAI(api_key=settings.openai_api_key)
        system_prompt = """You are a helpful travel assistant. Answer the user's question based on the provided context from their uploaded documents.

IMPORTANT:
- Only use information from the provided sources
- If the context doesn't contain the answer, say so clearly
- Cite sources using [Source N] format when referencing information
- Be concise but comprehensive"""

        user_prompt = f"""Context from user's documents:
{context}

User's question: {query}

Answer the question based on the context above. Include [Source N] citations."""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=500,
            )

            answer = response.choices[0].message.content

            return {
                "answer": answer,
                "chunks": chunks,
                "citations": citations,
                "tokens_used": response.usage.total_tokens,
            }

        except Exception as e:
            return {
                "answer": f"Error generating answer: {str(e)}",
                "chunks": chunks,
                "citations": citations,
                "error": str(e),
            }

    def generate_answer_stream(
        self,
        query: str,
        user_id: str,
        top_k: int = 3,
    ) -> Generator[str, None, None]:
        """
        RAG pipeline with streaming: retrieve chunks, stream OpenAI response.
        Yields Server-Sent Event formatted messages.
        """
        # Retrieve relevant document chunks
        chunks = self.query_documents(query, user_id, top_k)

        if not chunks:
            yield f"data: {json.dumps({'type': 'error', 'content': 'No documents found in your Knowledge Vault'})}\n\n"
            return

        # Build context and citations
        context_parts = []
        citations = []
        seen_docs = set()

        for idx, chunk in enumerate(chunks, 1):
            context_parts.append(f"[Source {idx}] {chunk['text']}")
            doc_key = (chunk["document_id"], chunk["title"])
            if doc_key not in seen_docs:
                citations.append({
                    "title": chunk["title"],
                    "document_id": chunk["document_id"],
                })
                seen_docs.add(doc_key)

        # Send citations first
        yield f"data: {json.dumps({'type': 'citations', 'content': citations})}\n\n"

        context = "\n\n".join(context_parts)

        # Stream answer from OpenAI
        client = openai.OpenAI(api_key=settings.openai_api_key)
        system_prompt = """You are a helpful travel assistant. Answer the user's question based on the provided context from their uploaded documents.

IMPORTANT:
- Only use information from the provided sources
- If the context doesn't contain the answer, say so clearly
- Cite sources using [Source N] format when referencing information
- Be concise but comprehensive"""

        user_prompt = f"""Context from user's documents:
{context}

User's question: {query}

Answer the question based on the context above. Include [Source N] citations."""

        try:
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=500,
                stream=True,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"

            # Signal completion
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
