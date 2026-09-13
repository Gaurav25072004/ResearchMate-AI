import faiss
import numpy as np
import re


def create_faiss_index(embeddings):
    """
    Create a FAISS index using cosine similarity.
    """

    if len(embeddings) == 0:
        return None

    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )

    # Normalize vectors so Inner Product = Cosine Similarity
    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    return index


def search_faiss_index(
    index,
    query_embedding,
    top_k=5
):
    """
    Perform normal semantic search using FAISS.
    """

    if index is None:
        return [], []

    query_embedding = np.asarray(
        query_embedding,
        dtype="float32"
    )

    if query_embedding.ndim == 1:
        query_embedding = query_embedding.reshape(
            1,
            -1
        )

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


def calculate_keyword_score(
    query,
    chunk
):
    """
    Calculate keyword overlap between query and chunk.

    Common English stop words are ignored so that words
    such as 'what', 'was', 'the', etc. do not dominate
    retrieval.
    """

    stop_words = {
        "what",
        "was",
        "were",
        "the",
        "this",
        "that",
        "used",
        "use",
        "using",
        "does",
        "did",
        "how",
        "which",
        "where",
        "when",
        "with",
        "from",
        "into",
        "about",
        "research",
        "study",
        "paper",
        "their",
        "they",
        "them",
        "these",
        "those",
        "are",
        "and",
        "for",
        "can",
        "could",
        "would",
        "should"
    }

    query_words = set(
        re.findall(
            r"\b[a-zA-Z]{3,}\b",
            query.lower()
        )
    )

    chunk_words = set(
        re.findall(
            r"\b[a-zA-Z]{3,}\b",
            chunk.lower()
        )
    )

    query_words = query_words - stop_words

    if not query_words:
        return 0.0

    matched_words = query_words.intersection(
        chunk_words
    )

    return len(matched_words) / len(query_words)


def calculate_section_score(
    query,
    chunk
):
    """
    Calculate relevance based on the actual section
    heading of the research paper.

    Main methodology sections receive a positive boost.

    Appendix and reference sections receive a penalty
    because they often contain prompts, citations, or
    supporting material that can create misleading
    keyword matches.
    """

    query_lower = query.lower()

    # -----------------------------------------
    # Extract section heading
    # -----------------------------------------

    section_match = re.search(
        r"^Section:\s*(.+)",
        chunk,
        re.IGNORECASE
    )

    if not section_match:
        return 0.0

    section_name = (
        section_match.group(1)
        .strip()
        .lower()
    )

    # -----------------------------------------
    # Penalize appendix sections
    # -----------------------------------------

    if re.match(
        r"^[a-z]\.",
        section_name
    ):
        return -1.0

    # -----------------------------------------
    # Penalize references
    # -----------------------------------------

    if section_name.startswith(
        "reference"
    ):
        return -1.0

    # =========================================
    # Methodology-related questions
    # =========================================

    methodology_query_terms = [
        "methodology",
        "method",
        "approach",
        "how was the research conducted",
        "how was the study conducted",
        "how does the system work",
        "how does the method work",
        "what technique was used",
        "what approach was used"
    ]

    if any(
        term in query_lower
        for term in methodology_query_terms
    ):

        strong_method_sections = [
            "rag-novelty",
            "indexing and retriever",
            "prompt",
            "methodology",
            "methods",
            "method",
            "approach",
            "framework",
            "architecture"
        ]

        for term in strong_method_sections:

            if (
                section_name == term
                or section_name.endswith(
                    " " + term
                )
            ):
                return 1.0

        # Experimental setup is related to methodology
        if "experimental setup" in section_name:
            return 0.8

    # =========================================
    # Result-related questions
    # =========================================

    result_query_terms = [
        "result",
        "results",
        "findings",
        "performance",
        "evaluation"
    ]

    if any(
        term in query_lower
        for term in result_query_terms
    ):

        result_sections = [
            "experimental results",
            "results",
            "findings",
            "evaluation"
        ]

        for term in result_sections:

            if (
                section_name == term
                or section_name.endswith(
                    " " + term
                )
            ):
                return 1.0

    # =========================================
    # Dataset-related questions
    # =========================================

    dataset_query_terms = [
        "dataset",
        "data collection",
        "data",
        "benchmark"
    ]

    if any(
        term in query_lower
        for term in dataset_query_terms
    ):

        dataset_sections = [
            "dataset collection and structure",
            "dataset",
            "data collection",
            "scholarly novelty benchmark"
        ]

        for term in dataset_sections:

            if (
                section_name == term
                or section_name.endswith(
                    " " + term
                )
            ):
                return 1.0

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
    Perform hybrid retrieval.

    Combines:

        65% semantic similarity
        10% keyword overlap
        25% section relevance

    For the current capstone, all chunks are considered
    because research papers currently contain a relatively
    small number of chunks.

    Returns the Top-K most relevant chunks.
    """

    if index is None:
        return []

    if not chunks:
        return []

    # -----------------------------------------
    # Prepare query embedding
    # -----------------------------------------

    query_embedding = np.asarray(
        query_embedding,
        dtype="float32"
    )

    if query_embedding.ndim == 1:
        query_embedding = query_embedding.reshape(
            1,
            -1
        )

    # Normalize query
    faiss.normalize_L2(query_embedding)

    # -----------------------------------------
    # Search all available chunks
    # -----------------------------------------

    candidate_k = index.ntotal

    semantic_scores, indices = index.search(
        query_embedding,
        candidate_k
    )

    # -----------------------------------------
    # Calculate hybrid score
    # -----------------------------------------

    results = []

    for semantic_score, index_value in zip(
        semantic_scores[0],
        indices[0]
    ):

        if index_value < 0:
            continue

        chunk = chunks[index_value]

        keyword_score = calculate_keyword_score(
            query,
            chunk
        )

        section_score = calculate_section_score(
            query,
            chunk
        )

        final_score = (
            semantic_weight * float(
                semantic_score
            )
            +
            keyword_weight * keyword_score
            +
            section_weight * section_score
        )

        results.append({
            "index": int(index_value),
            "semantic_score": float(
                semantic_score
            ),
            "keyword_score": float(
                keyword_score
            ),
            "section_score": float(
                section_score
            ),
            "final_score": float(
                final_score
            ),
            "chunk": chunk
        })

    # -----------------------------------------
    # Sort by final score
    # -----------------------------------------

    results.sort(
        key=lambda x: x["final_score"],
        reverse=True
    )

    # -----------------------------------------
    # Return Top-K
    # -----------------------------------------

    return results[:top_k]