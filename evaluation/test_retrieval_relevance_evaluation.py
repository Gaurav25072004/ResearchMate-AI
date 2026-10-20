
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from rag.pdf_loader import extract_text_from_pdf
from rag.text_processor import clean_text, split_text_into_chunks
from rag.embedding import load_embedding_model, generate_embeddings
from rag.vector_store import create_faiss_index, hybrid_search


PDF_PATH = Path(r"D:\My capstone Research papers\2506.22026v1.pdf")
TOP_K = 5

QUERIES = [
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
    {
        "query": "What limitations of the study are discussed?",
        "terms": [
            "limitations",
            "limitation",
            "threats to validity",
            "future work",
        ],
    },
    {
        "query": "What are the main contributions of the research?",
        "terms": [
            "contribution",
            "contributions",
            "we propose",
            "we introduce",
        ],
    },
    {
        "query": "How was the proposed system evaluated?",
        "terms": [
            "evaluation",
            "evaluated",
            "experiments",
            "baseline",
            "accuracy",
        ],
    },
]


def load_paper(pdf_path):
    """Extract, clean, and chunk the research paper."""
    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {pdf_path}\n"
            "Update PDF_PATH to point to your research paper."
        )

    # extract_text_from_pdf expects a file-like object
    # and returns (full_text, page_count).
    with pdf_path.open("rb") as pdf_file:
        text, page_count = extract_text_from_pdf(pdf_file)

    if not text or not text.strip():
        raise ValueError("No text could be extracted from the PDF.")

    chunks = split_text_into_chunks(clean_text(text))

    if not chunks:
        raise ValueError("No chunks were extracted from the paper.")

    return text, page_count, chunks


def calculate_keyword_proxy(chunk, terms):
    """
    Calculate a simple keyword-match proxy.

    This is not a human-validated relevance judgment.
    """
    text = chunk.casefold()
    return any(term.casefold() in text for term in terms)


def main():
    print("=" * 75)
    print("DAY 21 - EXPANDED RETRIEVAL RELEVANCE EVALUATION")
    print("=" * 75)

    text, page_count, chunks = load_paper(PDF_PATH)

    print(f"Paper: {PDF_PATH.name}")
    print(f"Pages: {page_count}")
    print(f"Chunks: {len(chunks)}")
    print(f"Top K: {TOP_K}")
    print(f"Queries: {len(QUERIES)}")
    print()
    print(
        "IMPORTANT: Keyword matches are only proxies. "
        "Inspect each full passage to judge actual relevance."
    )

    print("\nLoading embedding model...")
    model = load_embedding_model()

    print("Generating document embeddings...")
    embeddings = generate_embeddings(chunks, model)

    print("Creating FAISS index...")
    index = create_faiss_index(embeddings)

    all_proxy_matches = 0
    all_results = 0
    first_match_ranks = []

    for query_number, query_data in enumerate(QUERIES, start=1):
        query = query_data["query"]
        terms = query_data["terms"]

        print("\n" + "=" * 75)
        print(f"QUERY {query_number}/{len(QUERIES)}: {query}")
        print("=" * 75)

        # Use the same loaded embedding model for the query.
        query_embedding = model.encode(
            [query],
            show_progress_bar=False,
        )

        results = hybrid_search(
            index=index,
            query_embedding=query_embedding,
            query=query,
            chunks=chunks,
            top_k=TOP_K,
        )

        if not results:
            print("No results returned.")
            first_match_ranks.append(None)
            continue

        proxy_matches = 0
        first_match_rank = None

        for rank, result in enumerate(results, start=1):
            chunk = result["chunk"]
            is_match = calculate_keyword_proxy(chunk, terms)

            if is_match:
                proxy_matches += 1
                if first_match_rank is None:
                    first_match_rank = rank

            all_results += 1

            print(
                f"\nRank: {rank} | "
                f"Keyword proxy: "
                f"{'MATCH' if is_match else 'NO MATCH'} | "
                f"Score: {result.get('final_score', 0.0):.3f}"
            )

            lines = chunk.splitlines()
            section = lines[0].strip() if lines else "Unknown"

            print(f"Section: {section}")
            print("\nFull retrieved passage:")
            print(chunk)
            print("\n" + "-" * 75)

        all_proxy_matches += proxy_matches
        first_match_ranks.append(first_match_rank)

        precision = proxy_matches / len(results)
        hit = 1 if proxy_matches > 0 else 0

        print(f"\nRetrieved: {len(results)}")
        print(f"Keyword-proxy matches: {proxy_matches}")
        print(f"Proxy Precision@{len(results)}: {precision:.3f}")
        print(f"Proxy Hit@{len(results)}: {hit}")

    precision_at_k = (
        all_proxy_matches / all_results
        if all_results
        else 0.0
    )

    hit_at_k = (
        sum(rank is not None for rank in first_match_ranks)
        / len(QUERIES)
        if QUERIES
        else 0.0
    )

    reciprocal_ranks = [
        1 / rank if rank is not None else 0.0
        for rank in first_match_ranks
    ]

    mrr_at_k = (
        sum(reciprocal_ranks) / len(reciprocal_ranks)
        if reciprocal_ranks
        else 0.0
    )

    print("\n" + "=" * 75)
    print("SUMMARY - KEYWORD-PROXY METRICS")
    print(f"Precision@{TOP_K}: {precision_at_k:.3f}")
    print(f"Hit@{TOP_K}: {hit_at_k:.3f}")
    print(f"MRR@{TOP_K}: {mrr_at_k:.3f}")
    print(f"Queries evaluated: {len(QUERIES)}")
    print(f"Total results inspected: {all_results}")
    print()
    print(
        "These are keyword-proxy metrics, not human-validated "
        "relevance measurements."
    )
    print(
        "Manually review the full passages before assigning "
        "relevance ratings or calculating nDCG@5."
    )
    print("=" * 75)


if __name__ == "__main__":
    main()
