"""
In-memory Vector Retriever utilizing cosine similarity over normalized embeddings.
Simulates production FAISS index for document retrieval without heavy GPU dependencies.
"""
import numpy as np
from typing import List, Tuple
from app.schemas.loan import QualitativeDocument

class VectorDocumentRetriever:
    def __init__(self, embedding_dim: int = 128):
        self.embedding_dim = embedding_dim
        self.documents: List[QualitativeDocument] = []
        self.vectors: np.ndarray = np.empty((0, embedding_dim), dtype=np.float32)

    def _pseudo_embed(self, text: str) -> np.ndarray:
        """Deterministic pseudo-embedding for consistent semantic demonstration without network latency."""
        np.random.seed(abs(hash(text)) % (2**31))
        vec = np.random.randn(self.embedding_dim).astype(np.float32)
        norm = np.linalg.norm(vec)
        return vec / (norm + 1e-10)

    def add_documents(self, docs: List[QualitativeDocument]):
        if not docs:
            return
        embeddings = [self._pseudo_embed(d.text_content) for d in docs]
        new_vecs = np.vstack(embeddings)
        self.documents.extend(docs)
        if self.vectors.size == 0:
            self.vectors = new_vecs
        else:
            self.vectors = np.vstack([self.vectors, new_vecs])

    def search(self, query: str, top_k: int = 2) -> List[Tuple[QualitativeDocument, float]]:
        if self.vectors.size == 0:
            return []
        query_vec = self._pseudo_embed(query)
        scores = np.dot(self.vectors, query_vec)
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [(self.documents[i], float(scores[i])) for i in top_indices]
