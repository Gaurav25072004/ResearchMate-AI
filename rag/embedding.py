from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# Embedding Model
# --------------------------------------------------

MODEL_NAME = "all-MiniLM-L6-v2"


def load_embedding_model():
    """
    Load the sentence-transformer embedding model.
    """

    model = SentenceTransformer(MODEL_NAME)

    return model


# --------------------------------------------------
# Generate Embeddings
# --------------------------------------------------

def generate_embeddings(chunks, model):
    """
    Convert text chunks into numerical vectors.

    Parameters:
        chunks: List of text chunks
        model: Loaded SentenceTransformer model

    Returns:
        embeddings: Numerical vector representations
    """

    if not chunks:
        return []

    embeddings = model.encode(
        chunks,
        show_progress_bar=False
    )

    return embeddings