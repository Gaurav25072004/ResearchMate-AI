import faiss
import numpy as np


# --------------------------------------------------
# Create FAISS Index
# --------------------------------------------------

def create_faiss_index(embeddings):
    """
    Create a FAISS index using cosine similarity.

    Parameters:
        embeddings: NumPy array containing text embeddings

    Returns:
        FAISS index
    """

    if len(embeddings) == 0:
        return None

    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )

    # Normalize vectors for cosine similarity
    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]

    # Inner Product on normalized vectors
    # is equivalent to cosine similarity.
    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    return index


# --------------------------------------------------
# Search FAISS Index
# --------------------------------------------------

def search_faiss_index(
    index,
    query_embedding,
    top_k=5
):
    """
    Search the FAISS index using cosine similarity.

    Parameters:
        index: FAISS index
        query_embedding: Embedding vector of the query
        top_k: Number of results to retrieve

    Returns:
        scores: Cosine similarity scores
        indices: Indices of matching vectors
    """

    if index is None:
        return [], []

    query_embedding = np.asarray(
        query_embedding,
        dtype="float32"
    )

    # Make sure query has 2D shape
    if query_embedding.ndim == 1:
        query_embedding = query_embedding.reshape(
            1,
            -1
        )

    # Normalize query vector
    faiss.normalize_L2(query_embedding)

    top_k = min(
        top_k,
        index.ntotal
    )

    scores, indices = index.search(
        query_embedding,
        top_k
    )

    return scores[0], indices[0]