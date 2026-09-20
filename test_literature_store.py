from rag.embedding import load_embedding_model
from rag.literature_store import (
    build_literature_corpus,
    search_literature
)


# ============================================================
# Configuration
# ============================================================

LITERATURE_DIRECTORY = (
    r".\documents\literature"
)


# ============================================================
# Step 1: Load embedding model
# ============================================================

print("\n========================================")
print("STEP 1: EMBEDDING MODEL")
print("========================================")

embedding_model = (
    load_embedding_model()
)

print(
    "Embedding model loaded successfully."
)


# ============================================================
# Step 2: Build literature corpus
# ============================================================

print("\n========================================")
print("STEP 2: BUILD LITERATURE CORPUS")
print("========================================")

literature_corpus = (
    build_literature_corpus(
        LITERATURE_DIRECTORY,
        embedding_model
    )
)

papers = literature_corpus[
    "papers"
]

chunks = literature_corpus[
    "chunks"
]

index = literature_corpus[
    "index"
]

print(
    "Number of literature papers:",
    len(papers)
)

print(
    "Number of literature chunks:",
    len(chunks)
)

if index is not None:

    print(
        "FAISS vectors:",
        index.ntotal
    )

else:

    print(
        "FAISS index: None"
    )


# ============================================================
# Step 3: Show loaded papers
# ============================================================

print("\n========================================")
print("STEP 3: LOADED LITERATURE")
print("========================================")

for i, paper in enumerate(
    papers,
    start=1
):

    print(
        f"{i}. {paper['source']}"
    )

    print(
        f"   Pages: {paper['page_count']}"
    )


# ============================================================
# Step 4: Test literature retrieval
# ============================================================

print("\n========================================")
print("STEP 4: LITERATURE RETRIEVAL")
print("========================================")

query = """
research methodology for evaluating
novelty of scientific ideas using
retrieval augmented generation and
large language models
"""

results = search_literature(
    literature_corpus,
    query,
    embedding_model,
    top_k=5
)

print(
    "Retrieved literature results:",
    len(results)
)


# ============================================================
# Step 5: Display results
# ============================================================

print("\n========================================")
print("STEP 5: RETRIEVED RESULTS")
print("========================================")

for i, result in enumerate(
    results,
    start=1
):

    print(
        f"\n--- Result {i} ---"
    )

    print(
        "Source:",
        result["source"]
    )

    print(
        "Final Score:",
        round(
            result["final_score"],
            4
        )
    )

    print(
        "Semantic Score:",
        round(
            result["semantic_score"],
            4
        )
    )

    print(
        "Chunk:"
    )

    print(
        result["chunk"][:500]
    )


# ============================================================
# Final status
# ============================================================

print("\n========================================")
print("LITERATURE CORPUS TEST COMPLETE")
print("========================================")