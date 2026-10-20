
from pathlib import Path
import re
from math import log2


PROJECT_ROOT = Path(__file__).resolve().parent.parent
JUDGMENTS_PATH = (
    PROJECT_ROOT
    / "evaluation"
    / "retrieval_relevance_judgments.md"
)
TOP_K = 5


def dcg_at_k(relevance_scores, k):
    """Calculate Discounted Cumulative Gain at rank k."""
    return sum(
        (2**score - 1) / log2(rank + 1)
        for rank, score in enumerate(
            relevance_scores[:k],
            start=1,
        )
    )


def ndcg_at_k(relevance_scores, k):
    """Calculate normalized DCG using ideal ranking."""
    actual_dcg = dcg_at_k(relevance_scores, k)
    ideal_scores = sorted(
        relevance_scores,
        reverse=True,
    )
    ideal_dcg = dcg_at_k(ideal_scores, k)

    return actual_dcg / ideal_dcg if ideal_dcg else 0.0


def load_judgments(path):
    """Read relevance ratings from the Markdown tables."""
    content = path.read_text(encoding="utf-8")
    judgments = {}
    current_query = None

    for line in content.splitlines():
        if line.startswith("## Query "):
            current_query = line.split(":", 1)[-1].strip()
            judgments[current_query] = []

        elif current_query and line.startswith("|"):
            cells = [
                cell.strip()
                for cell in line.strip().strip("|").split("|")
            ]

            # Skip the Markdown table header and separator.
            if (
                len(cells) >= 3
                and cells[0] == "Rank"
            ):
                continue

            if (
                len(cells) >= 3
                and re.fullmatch(r"\d+", cells[0])
                and re.fullmatch(r"[012]", cells[2])
            ):
                judgments[current_query].append(
                    int(cells[2])
                )

    if not judgments:
        raise ValueError(
            "No query judgments found in the Markdown file."
        )

    for query, ratings in judgments.items():
        if len(ratings) != TOP_K:
            raise ValueError(
                f"{query}: expected {TOP_K} ratings, "
                f"found {len(ratings)}."
            )

    return judgments


def main():
    if not JUDGMENTS_PATH.exists():
        raise FileNotFoundError(
            f"Judgment file not found: {JUDGMENTS_PATH}"
        )

    judgments = load_judgments(JUDGMENTS_PATH)

    print("=" * 60)
    print("DAY 20 - nDCG@5 EVALUATION")
    print("Ratings loaded from the Markdown judgment file")
    print("Ratings were reviewed against the full retrieved passages.")
    print("=" * 60)

    scores = []

    for query, ratings in judgments.items():
        score = ndcg_at_k(ratings, TOP_K)
        scores.append(score)

        print(f"\nQuery: {query}")
        print(f"Relevance ratings: {ratings}")
        print(f"nDCG@{TOP_K}: {score:.3f}")

    print("\n" + "=" * 60)
    print(f"Queries evaluated: {len(scores)}")
    print(f"Mean nDCG@{TOP_K}: {sum(scores) / len(scores):.3f}")
    print(
        "This score measures the ordering of the entered ratings; "
        "it does not independently validate retrieval quality."
    )
    print("=" * 60)


if __name__ == "__main__":
    main()
