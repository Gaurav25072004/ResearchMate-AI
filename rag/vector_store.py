
import faiss
import numpy as np
import re


def create_faiss_index(embeddings):
    """
    Create a FAISS index using cosine similarity.
    Embeddings are normalized so inner product equals
    cosine similarity.
    """
    if embeddings is None or len(embeddings) == 0:
        return None

    embeddings = np.asarray(embeddings, dtype="float32")

    if embeddings.ndim != 2:
        raise ValueError("Embeddings must be a 2D array.")

    if embeddings.shape[1] == 0:
        raise ValueError("Embedding dimension must be greater than zero.")

    if not np.isfinite(embeddings).all():
        raise ValueError("Embeddings must contain only finite values.")

    embeddings = embeddings.copy()
    faiss.normalize_L2(embeddings)

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    return index


def search_faiss_index(index, query_embedding, top_k=5):
    """
    Perform semantic search using a FAISS index.

    Returns:
        scores: Similarity scores.
        indices: Matching vector indices.
    """
    if index is None or index.ntotal == 0:
        return [], []

    if not isinstance(top_k, int) or isinstance(top_k, bool):
        raise TypeError("top_k must be an integer.")

    if top_k <= 0:
        return [], []

    query_embedding = np.asarray(
        query_embedding,
        dtype="float32"
    )

    if query_embedding.ndim == 1:
        query_embedding = query_embedding.reshape(1, -1)

    if query_embedding.ndim != 2:
        raise ValueError("Query embedding must be a 1D or 2D array.")

    if query_embedding.shape[1] != index.d:
        raise ValueError("Query embedding dimension does not match index.")

    if not np.isfinite(query_embedding).all():
        raise ValueError("Query embedding must contain finite values.")

    query_embedding = query_embedding.copy()
    faiss.normalize_L2(query_embedding)

    actual_k = min(top_k, index.ntotal)
    scores, indices = index.search(query_embedding, actual_k)

    return scores[0], indices[0]


def calculate_keyword_score(query, chunk):
    """
    Calculate query keyword overlap with a chunk.

    Common stop words are ignored. The score measures the
    proportion of meaningful query words found in the chunk.
    """
    stop_words = {
        "what", "was", "were", "the", "this", "that",
        "used", "use", "using", "does", "did", "how",
        "which", "where", "when", "with", "from", "into",
        "about", "research", "study", "paper", "their",
        "they", "them", "these", "those", "are", "and",
        "for", "can", "could", "would", "should", "its",
        "our", "your", "have", "has", "had", "been",
        "being", "show", "shows", "main"
    }

    query_words = set(
        re.findall(r"\b[a-zA-Z]{3,}\b", query.casefold())
    ) - stop_words

    chunk_words = set(
        re.findall(r"\b[a-zA-Z]{3,}\b", chunk.casefold())
    )

    if not query_words:
        return 0.0

    matched_words = query_words.intersection(chunk_words)

    return len(matched_words) / len(query_words)


def calculate_section_score(query, chunk):
    """
    Score section relevance according to query intent.

    Methodology questions favour method sections, dataset
    questions favour dataset sections, and results questions
    favour results sections.

    Appendix, supplement, and reference sections are penalized
    to reduce misleading keyword matches.
    """
    query_lower = query.casefold()

    section_match = re.search(
        r"^Section:\s*(.+)$",
        chunk,
        re.IGNORECASE | re.MULTILINE
    )

    if not section_match:
        return 0.0

    section_name = section_match.group(1).strip().casefold()

    # Penalize reference, appendix, and supplementary sections.
    if (
        section_name in {"document", "references", "reference"}
        or re.match(
            r"^(?:[a-z](?:\.\d+)*\s+)?"
            r"(?:appendix|appendices|supplement|"
            r"supplementary material|references|bibliography)\b",
            section_name
        )
    ):
        return -1.0

    # Methodology questions.
    methodology_terms = (
        "methodology",
        "method",
        "approach",
        "how was the study conducted",
        "how was the research conducted",
        "what technique was used",
        "what approach was used",
        "how does the system work"
    )

    if any(term in query_lower for term in methodology_terms):
        if section_name in {
            "methodology",
            "methods",
            "method",
            "materials and methods",
            "approach",
            "experimental setup",
            "experiments",
            "system architecture",
            "architecture"
        }:
            return 1.0

        if section_name.endswith((
            " methodology",
            " methods",
            " approach",
            " experimental setup",
            " architecture"
        )):
            return 0.8

    # Dataset questions.
    dataset_terms = (
        "dataset",
        "datasets",
        "data collection",
        "what data",
        "which data",
        "benchmark"
    )

    if any(term in query_lower for term in dataset_terms):
        if section_name in {
            "dataset",
            "datasets",
            "dataset construction",
            "dataset statistics",
            "dataset evaluation protocol",
            "data collection",
            "data collection and structure",
            "experimental data"
        }:
            return 1.0

        if section_name.endswith((
            " dataset",
            " dataset construction",
            " dataset statistics",
            " data collection"
        )):
            return 0.8

    # Main-results questions.
    result_terms = (
        "main results",
        "results",
        "findings",
        "what did the study find",
        "what were the findings",
        "what were the main results"
    )

    if any(term in query_lower for term in result_terms):
        if section_name in {
            "results",
            "experimental results",
            "results and discussion",
            "findings"
        }:
            return 1.0

        if section_name.endswith((
            " experimental results",
            " findings"
        )):
            return 0.8

    # Explicit evaluation or performance questions.
    evaluation_terms = (
        "evaluation",
        "performance",
        "accuracy",
        "metrics",
        "benchmark results"
    )

    if any(term in query_lower for term in evaluation_terms):
        if section_name in {
            "evaluation",
            "evaluation results",
            "experimental evaluation",
            "performance evaluation"
        }:
            return 0.8

    return 0.0


def hybrid_search(
    index,
    query_embedding,
    query,
    chunks,
    top_k=5,
    semantic_weight=0.65,
    keyword_weight=0.10,
    section_weight=0.25
):
    """
    Perform hybrid retrieval using:
        - Semantic similarity
        - Keyword overlap
        - Query-aware section relevance

    Returns a list of result dictionaries sorted by final score.
    Each result contains:
        index, semantic_score, keyword_score,
        section_score, final_score, chunk
    """
    if index is None or not chunks or index.ntotal == 0:
        return []

    if not isinstance(top_k, int) or isinstance(top_k, bool):
        raise TypeError("top_k must be an integer.")

    if top_k <= 0:
        return []

    weights = (semantic_weight, keyword_weight, section_weight)

    if any(not isinstance(weight, (int, float)) for weight in weights):
        raise TypeError("Search weights must be numeric.")

    if any(weight < 0 for weight in weights):
        raise ValueError("Search weights cannot be negative.")

    if not np.isclose(sum(weights), 1.0):
        raise ValueError("Search weights must sum to 1.0.")

    query_embedding = np.asarray(
        query_embedding,
        dtype="float32"
    )

    if query_embedding.ndim == 1:
        query_embedding = query_embedding.reshape(1, -1)

    if query_embedding.ndim != 2:
        raise ValueError("Query embedding must be a 1D or 2D array.")

    if query_embedding.shape[1] != index.d:
        raise ValueError("Query embedding dimension does not match index.")

    if not np.isfinite(query_embedding).all():
        raise ValueError("Query embedding must contain finite values.")

    query_embedding = query_embedding.copy()
    faiss.normalize_L2(query_embedding)

    # Search all vectors because the corpus is currently relatively small.
    candidate_k = min(index.ntotal, len(chunks))

    semantic_scores, indices = index.search(
        query_embedding,
        candidate_k
    )

    results = []

    for semantic_score, index_value in zip(
        semantic_scores[0],
        indices[0]
    ):
        if index_value < 0 or index_value >= len(chunks):
            continue

        chunk = chunks[int(index_value)]

        keyword_score = calculate_keyword_score(query, chunk)
        section_score = calculate_section_score(query, chunk)

        final_score = (
            semantic_weight * float(semantic_score)
            + keyword_weight * keyword_score
            + section_weight * section_score
        )

        results.append({
            "index": int(index_value),
            "semantic_score": float(semantic_score),
            "keyword_score": float(keyword_score),
            "section_score": float(section_score),
            "final_score": float(final_score),
            "chunk": chunk
        })

    results.sort(
        key=lambda result: result["final_score"],
        reverse=True
    )

    return results[:top_k]
