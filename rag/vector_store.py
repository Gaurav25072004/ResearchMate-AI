import faiss
import numpy as np


# --------------------------------------------------
# Create FAISS Index
# --------------------------------------------------

def create_faiss_index(embeddings):
    """
    Create a FAISS index from embedding vectors.

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

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    return index