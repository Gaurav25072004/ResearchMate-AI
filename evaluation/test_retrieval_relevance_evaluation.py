from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from rag.pdf_loader import extract_text_from_pdf
from rag.text_processor import clean_text, split_text_into_chunks
from rag.embedding import load_embedding_model
from rag.vector_store import create_faiss_index, hybrid_search


PAPER_PATH = Path(r"D:\My capstone Research papers\2506.22026v1.pdf")
TOP_K = 5

TEST_CASES = [
    {
        "query": "What methodology was used in the study?",
        "terms": [
            "methodology", "methods", "approach",
            "experimental setup", "system architecture"
        ],
    },
    {
        "query": "What dataset or data was used?",
        "terms": [
            "dataset", "datasets", "data collection",
            "benchmark", "corpus"
        ],
    },
    {
        "query": "What were the main results of the research?",
        "terms": [
            "main results", "experimental results",
            "findings", "accuracy", "performance"
        ],
    },
]


def main():
    if not PAPER_PATH.exists():
        raise FileNotFoundError(f"Research paper not found: {PAPER_PATH}")

    with open(PAPER_PATH, "rb") as pdf_file:
        text, page_count = extract_text_from_pdf(pdf_file)

    chunks = split_text_into_chunks(clean_text(text))
    if not chunks:
        raise RuntimeError("No chunks were extracted from the paper.")

    model = load_embedding_model()
    embeddings = model.encode(chunks, show_progress_bar=False)
    index = create_faiss_index(embeddings)

    total_relevant = 0
    total_retrieved = 0
    query_hits = 0
    reciprocal_ranks = []

    print("=" * 65)
    print("DAY 18 - RETRIEVAL RELEVANCE EVALUATION")
    print("=" * 65)
    print(f"Pages: {page_count} | Chunks: {len(chunks)} | Top K: {TOP_K}")
    print("Relevance is estimated using section/content keyword proxies.")
    print("These metrics are not human-validated relevance judgments.")

    for case in TEST_CASES:
        query = case["query"]
        terms = case["terms"]
        query_embedding = model.encode([query], show_progress_bar=False)[0]

        results = hybrid_search(
            index=index,
            query_embedding=query_embedding,
            query=query,
            chunks=chunks,
            top_k=TOP_K,
        )

        relevant_flags = [
            any(term in result["chunk"].casefold() for term in terms)
            for result in results
        ]

        relevant_count = sum(relevant_flags)
        total_relevant += relevant_count
        total_retrieved += len(results)

        hit = relevant_count > 0
        query_hits += int(hit)

        first_relevant_rank = next(
            (rank for rank, is_relevant in enumerate(relevant_flags, 1)
             if is_relevant),
            None,
        )
        reciprocal_ranks.append(
            1 / first_relevant_rank if first_relevant_rank else 0
        )

        precision = relevant_count / len(results) if results else 0

        print(f"\nQuery: {query}")
        print(f"Retrieved: {len(results)} | Proxy-relevant: {relevant_count}")
        print(f"Precision@{TOP_K}: {precision:.3f}")
        print(f"Hit@{TOP_K}: {int(hit)}")

        for rank, (result, is_relevant) in enumerate(
            zip(results, relevant_flags), 1
        ):
            heading = result["chunk"].splitlines()[0][:100]
            print(
                f"  {rank}. {'PROXY-RELEVANT' if is_relevant else 'UNMATCHED'}"
                f" | score={result['final_score']:.3f} | {heading}"
            )

    query_count = len(TEST_CASES)
    overall_precision = (
        total_relevant / total_retrieved if total_retrieved else 0
    )
    hit_at_k = query_hits / query_count
    mrr = sum(reciprocal_ranks) / query_count

    print("\n" + "=" * 65)
    print("SUMMARY")
    print(f"Precision@{TOP_K}: {overall_precision:.3f}")
    print(f"Hit@{TOP_K}: {hit_at_k:.3f}")
    print(f"MRR@{TOP_K}: {mrr:.3f}")
    print(f"Queries evaluated: {query_count}")
    print("Evaluation completed. Inspect the matches before interpreting them.")
    print("=" * 65)


if __name__ == "__main__":
    main()
