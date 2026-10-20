
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
PREVIEW_LENGTH = 350

TEST_CASES = [
    {
        "query": "What methodology was used in the study?",
        "terms": [
            "methodology",
            "methods",
            "approach",
            "experimental setup",
            "system architecture",
        ],
    },
    {
        "query": "What dataset or data was used?",
        "terms": [
            "dataset",
            "datasets",
            "data collection",
            "benchmark",
            "corpus",
        ],
    },
    {
        "query": "What were the main results of the research?",
        "terms": [
            "main results",
            "experimental results",
            "findings",
            "accuracy",
            "performance",
        ],
    },
]


def main():
    if not PAPER_PATH.exists():
        raise FileNotFoundError(
            f"Research paper not found: {PAPER_PATH}"
        )

    with open(PAPER_PATH, "rb") as pdf_file:
        text, page_count = extract_text_from_pdf(pdf_file)

    chunks = split_text_into_chunks(clean_text(text))

    if not chunks:
        raise RuntimeError(
            "No chunks were extracted from the paper."
        )

    model = load_embedding_model()
    embeddings = model.encode(
        chunks,
        show_progress_bar=False,
    )
    index = create_faiss_index(embeddings)

    total_proxy_relevant = 0
    total_retrieved = 0
    query_hits = 0
    reciprocal_ranks = []

    print("=" * 75)
    print("DAY 19 - RETRIEVAL RELEVANCE INSPECTION")
    print("=" * 75)
    print(f"Paper: {PAPER_PATH.name}")
    print(f"Pages: {page_count}")
    print(f"Chunks: {len(chunks)}")
    print(f"Top K: {TOP_K}")
    print(
        "\nIMPORTANT: Keyword matches are only proxies. "
        "Inspect each preview to judge actual relevance."
    )

    for case in TEST_CASES:
        query = case["query"]
        terms = case["terms"]

        query_embedding = model.encode(
            [query],
            show_progress_bar=False,
        )[0]

        results = hybrid_search(
            index=index,
            query_embedding=query_embedding,
            query=query,
            chunks=chunks,
            top_k=TOP_K,
        )

        # Retain the existing keyword-proxy metric for comparison.
        relevant_flags = [
            any(
                term in result["chunk"].casefold()
                for term in terms
            )
            for result in results
        ]

        relevant_count = sum(relevant_flags)
        result_count = len(results)

        total_proxy_relevant += relevant_count
        total_retrieved += result_count

        hit = relevant_count > 0
        query_hits += int(hit)

        first_relevant_rank = next(
            (
                rank
                for rank, is_relevant in enumerate(
                    relevant_flags, start=1
                )
                if is_relevant
            ),
            None,
        )

        reciprocal_ranks.append(
            1 / first_relevant_rank
            if first_relevant_rank is not None
            else 0
        )

        precision = (
            relevant_count / result_count
            if result_count
            else 0
        )

        print("\n" + "-" * 75)
        print(f"QUERY: {query}")
        print(
            f"Retrieved: {result_count}"
            f" | Keyword-proxy matches: {relevant_count}"
        )
        print(f"Proxy Precision@{TOP_K}: {precision:.3f}")
        print(f"Proxy Hit@{TOP_K}: {int(hit)}")
        print("-" * 75)

        for rank, (result, proxy_match) in enumerate(
            zip(results, relevant_flags),
            start=1,
        ):
            chunk = result["chunk"]
            lines = chunk.splitlines()
            heading = (
                lines[0].strip()[:120]
                if lines
                else "(No heading)"
            )
            preview = " ".join(chunk.split())[
                :PREVIEW_LENGTH
            ]

            print(
                f"\nRank: {rank}"
                f" | Proxy: {'MATCH' if proxy_match else 'NO MATCH'}"
                f" | Score: {result['final_score']:.3f}"
            )
            print(f"Section: {heading}")
            print(f"Preview: {preview}...")

    query_count = len(TEST_CASES)

    overall_precision = (
        total_proxy_relevant / total_retrieved
        if total_retrieved
        else 0
    )
    hit_at_k = (
        query_hits / query_count
        if query_count
        else 0
    )
    mrr = (
        sum(reciprocal_ranks) / query_count
        if query_count
        else 0
    )

    print("\n" + "=" * 75)
    print("SUMMARY — KEYWORD-PROXY METRICS")
    print(f"Precision@{TOP_K}: {overall_precision:.3f}")
    print(f"Hit@{TOP_K}: {hit_at_k:.3f}")
    print(f"MRR@{TOP_K}: {mrr:.3f}")
    print(f"Queries evaluated: {query_count}")
    print(f"Total results inspected: {total_retrieved}")
    print(
        "\nThese are keyword-proxy metrics, not "
        "human-validated relevance measurements."
    )
    print("=" * 75)


if __name__ == "__main__":
    main()
