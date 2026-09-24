import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from rag.pdf_loader import extract_text_from_pdf
from rag.text_processor import clean_text, split_text_into_chunks
from rag.embedding import load_embedding_model, generate_embeddings
from rag.vector_store import create_faiss_index, hybrid_search


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

PAPER_PATH = Path(
    r"D:\My capstone Research papers\2506.22026v1.pdf"
)

TEST_QUERIES = [
    "What methodology was used in the study?",
    "What dataset or data was used?",
    "What were the main results of the research?",
]


# ---------------------------------------------------------
# Load and process paper
# ---------------------------------------------------------

def load_paper():
    if not PAPER_PATH.exists():
        raise FileNotFoundError(
            f"Research paper not found: {PAPER_PATH}"
        )

    with open(PAPER_PATH, "rb") as pdf_file:
        text, page_count = extract_text_from_pdf(pdf_file)

    cleaned_text = clean_text(text)

    chunks = split_text_into_chunks(cleaned_text)

    return page_count, chunks


# ---------------------------------------------------------
# Retrieval evaluation
# ---------------------------------------------------------

def evaluate_retrieval():

    print("=" * 60)
    print("RESEARCHMATE AI - RETRIEVAL EVALUATION")
    print("=" * 60)

    # Step 1: Load paper
    print("\n[1] Loading research paper...")

    page_count, chunks = load_paper()

    print(f"Pages: {page_count}")
    print(f"Chunks: {len(chunks)}")

    assert page_count > 0
    assert len(chunks) > 0

    print("PASS: Paper processing")

    # Step 2: Load embedding model
    print("\n[2] Loading embedding model...")

    embedding_model = load_embedding_model()

    print("Embedding model loaded.")

    # Step 3: Generate embeddings
    print("\n[3] Generating embeddings...")

    embeddings = generate_embeddings(
        chunks,
        embedding_model
    )

    print(f"Embeddings generated: {len(embeddings)}")

    assert len(embeddings) == len(chunks)

    print("PASS: Embedding generation")

    # Step 4: Create FAISS index
    print("\n[4] Creating FAISS index...")

    index = create_faiss_index(embeddings)

    assert index is not None
    assert index.ntotal == len(chunks)

    print(f"FAISS vectors: {index.ntotal}")
    print("PASS: FAISS index creation")

    # Step 5: Evaluate queries
    print("\n[5] Evaluating retrieval queries...")

    for query_number, query in enumerate(
        TEST_QUERIES,
        start=1
    ):

        print("\n" + "-" * 60)
        print(f"Query {query_number}: {query}")
        print("-" * 60)

        query_embedding = embedding_model.encode(
            [query]
        )[0]

        results = hybrid_search(
            index=index,
            query_embedding=query_embedding,
            query=query,
            chunks=chunks,
            top_k=5
        )

        print(f"Retrieved results: {len(results)}")

        assert len(results) > 0

        for result_number, result in enumerate(
            results,
            start=1
        ):

            print(
                f"\nResult {result_number}"
            )

            print(
                f"Final score: "
                f"{result['final_score']:.4f}"
            )

            print(
                f"Semantic score: "
                f"{result['semantic_score']:.4f}"
            )

            print(
                f"Keyword score: "
                f"{result['keyword_score']:.4f}"
            )

            print(
                f"Section score: "
                f"{result['section_score']:.4f}"
            )

            chunk = result["chunk"]

            assert isinstance(chunk, str)
            assert len(chunk.strip()) > 0

            print(
                "Chunk preview:"
            )

            print(
                chunk[:300].replace(
                    "\n",
                    " "
                )
            )

        print(
            f"\nPASS: Query {query_number}"
        )

    print("\n" + "=" * 60)
    print("RETRIEVAL EVALUATION PASSED")
    print("=" * 60)


if __name__ == "__main__":
    evaluate_retrieval()