import math
import re
from pathlib import Path


# DAY 21 - nDCG@5 EVALUATION
# All six queries were reviewed against full retrieved passages.

JUDGMENTS_FILE = (
    Path(__file__).resolve().parent
    / "retrieval_relevance_judgments.md"
)

TOP_K = 5


def calculate_dcg(relevance_scores):
    """Calculate Discounted Cumulative Gain."""
    dcg = 0.0

    for rank, relevance in enumerate(relevance_scores, start=1):
        dcg += (2 ** relevance - 1) / math.log2(rank + 1)

    return dcg


def calculate_ndcg(relevance_scores):
    """Calculate Normalized Discounted Cumulative Gain."""
    dcg = calculate_dcg(relevance_scores)

    ideal_scores = sorted(
        relevance_scores,
        reverse=True,
    )

    ideal_dcg = calculate_dcg(ideal_scores)

    if ideal_dcg == 0:
        return 0.0

    return dcg / ideal_dcg


def load_relevance_judgments(file_path):
    """Load query headings and relevance ratings from Markdown."""
    content = file_path.read_text(encoding="utf-8")

    query_sections = re.split(
        r"(?m)^## Query \d+: ",
        content,
    )[1:]

    judgments = []

    for section in query_sections:
        lines = section.strip().splitlines()

        if not lines:
            continue

        query = lines[0].strip()

        ratings_match = re.search(
            r"\*\*Relevance ratings:\*\*\s*`\[([0-2,\s]+)\]`",
            section,
        )

        if not ratings_match:
            ratings_match = re.search(
                r"\*\*Provisional relevance ratings:\*\*\s*"
                r"`\[([0-2,\s]+)\]`",
                section,
            )

        if not ratings_match:
            raise ValueError(
                f"Could not find relevance ratings for query: {query}"
            )

        ratings = [
            int(value.strip())
            for value in ratings_match.group(1).split(",")
        ]

        if len(ratings) != TOP_K:
            raise ValueError(
                f"Expected {TOP_K} ratings for '{query}', "
                f"but found {len(ratings)}."
            )

        judgments.append(
            {
                "query": query,
                "ratings": ratings,
            }
        )

    if not judgments:
        raise ValueError(
            f"No query judgments found in {file_path}"
        )

    return judgments


def main():
    print("=" * 60)
    print("DAY 21 - nDCG@5 EVALUATION")
    print(
        "All six queries were reviewed against full retrieved passages."
    )
    print("=" * 60)

    judgments = load_relevance_judgments(JUDGMENTS_FILE)

    scores = []

    for judgment in judgments:
        query = judgment["query"]
        ratings = judgment["ratings"]

        ndcg_score = calculate_ndcg(ratings)
        scores.append(ndcg_score)

        print(f"\nQuery: {query}")
        print(f"Relevance ratings: {ratings}")
        print(f"nDCG@{TOP_K}: {ndcg_score:.3f}")

    mean_ndcg = sum(scores) / len(scores)

    print("\n" + "=" * 60)
    print(f"Queries evaluated: {len(judgments)}")
    print(f"Mean nDCG@{TOP_K}: {mean_ndcg:.3f}")
    print(
        "This score measures the ordering of the entered ratings; "
        "it does not independently validate retrieval quality."
    )
    print("=" * 60)


if __name__ == "__main__":
    main()
