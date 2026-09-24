import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from rag.embedding import load_embedding_model
from rag.literature_store import (
    build_literature_corpus,
    search_literature,
)
from agents.novelty_agent import build_novelty_analysis_prompt


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

LITERATURE_DIRECTORY = (
    PROJECT_ROOT / "documents" / "literature"
)


# ---------------------------------------------------------
# Evaluation
# ---------------------------------------------------------

def evaluate_cross_paper_analysis():

    print("=" * 60)
    print("RESEARCHMATE AI - CROSS-PAPER EVALUATION")
    print("=" * 60)

    # -----------------------------------------------------
    # 1. Check literature directory
    # -----------------------------------------------------

    print("\n[1] Checking literature corpus...")

    assert LITERATURE_DIRECTORY.exists(), (
        f"Literature directory not found: "
        f"{LITERATURE_DIRECTORY}"
    )

    pdf_files = list(
        LITERATURE_DIRECTORY.glob("*.pdf")
    )

    assert len(pdf_files) > 0, (
        "No literature PDFs found."
    )

    print(
        f"Literature papers found: "
        f"{len(pdf_files)}"
    )

    for pdf_file in pdf_files:
        print(f"  - {pdf_file.name}")

    print("PASS: Literature corpus availability")

    # -----------------------------------------------------
    # 2. Load embedding model
    # -----------------------------------------------------

    print("\n[2] Loading embedding model...")

    embedding_model = load_embedding_model()

    print("Embedding model loaded.")
    print("PASS: Embedding model")

    # -----------------------------------------------------
    # 3. Build separate literature corpus
    # -----------------------------------------------------

    print("\n[3] Building literature corpus...")

    literature_corpus = build_literature_corpus(
        LITERATURE_DIRECTORY,
        embedding_model
    )

    assert literature_corpus is not None, (
        "Literature corpus was not created."
    )

    assert len(
        literature_corpus["papers"]
    ) > 0, (
        "Literature corpus contains no papers."
    )

    assert len(
        literature_corpus["chunks"]
    ) > 0, (
        "Literature corpus contains no chunks."
    )

    assert literature_corpus["index"] is not None, (
        "Literature FAISS index was not created."
    )

    print(
        f"Papers: "
        f"{len(literature_corpus['papers'])}"
    )

    print(
        f"Chunks: "
        f"{len(literature_corpus['chunks'])}"
    )

    print(
        f"FAISS vectors: "
        f"{literature_corpus['index'].ntotal}"
    )

    assert (
        literature_corpus["index"].ntotal
        == len(literature_corpus["chunks"])
    )

    print("PASS: Separate literature corpus")

    # -----------------------------------------------------
    # 4. Test literature retrieval
    # -----------------------------------------------------

    print("\n[4] Testing literature retrieval...")

    query = (
        "How is novelty of scientific ideas "
        "evaluated using literature?"
    )

    results = search_literature(
        literature_corpus,
        query,
        embedding_model,
        top_k=5
    )

    assert len(results) > 0, (
        "Literature retrieval returned no results."
    )

    print(
        f"Retrieved literature results: "
        f"{len(results)}"
    )

    for number, result in enumerate(
        results,
        start=1
    ):

        print(f"\nResult {number}")

        assert result["source"], (
            "Literature result has no source."
        )

        assert result["chunk"].strip(), (
            "Literature result has empty chunk."
        )

        print(
            f"Source: {result['source']}"
        )

        print(
            f"Final score: "
            f"{result['final_score']:.4f}"
        )

        print(
            "Chunk preview:"
        )

        print(
            result["chunk"][:250].replace(
                "\n",
                " "
            )
        )

    print(
        "\nPASS: Literature retrieval"
    )

    # -----------------------------------------------------
    # 5. Build novelty prompt
    # -----------------------------------------------------

    print("\n[5] Building novelty-analysis prompt...")

    paper_analysis = """
## Research Problem

The uploaded paper studies the evaluation of
novelty in scientific ideas.

## Research Objectives

The research aims to develop a literature-grounded
novelty assessment system.

## Methodology

The system uses retrieval and LLM-based assessment.

## Dataset / Data

The study uses expert-annotated scientific ideas.

## Results / Findings

The study reports results from expert evaluation.

## Main Contributions

The paper proposes an automated novelty assessment
framework.

## Limitations

The study discusses challenges related to
subjectivity in novelty assessment.
"""

    novelty_prompt = build_novelty_analysis_prompt(
        paper_analysis,
        results
    )

    assert novelty_prompt.strip(), (
        "Novelty prompt is empty."
    )

    print("Novelty prompt created.")

    # -----------------------------------------------------
    # 6. Check uploaded paper context
    # -----------------------------------------------------

    print(
        "\n[6] Checking uploaded-paper context..."
    )

    assert (
        "Research Problem" in novelty_prompt
    ), (
        "Uploaded paper analysis is missing."
    )

    assert (
        "Research Objectives" in novelty_prompt
    ), (
        "Uploaded paper objectives are missing."
    )

    print(
        "PASS: Uploaded-paper context"
    )

    # -----------------------------------------------------
    # 7. Check literature evidence
    # -----------------------------------------------------

    print(
        "\n[7] Checking literature evidence..."
    )

    assert (
        "RETRIEVED LITERATURE" in novelty_prompt
    ), (
        "Retrieved literature section missing."
    )

    assert (
        "SOURCE:" in novelty_prompt
    ), (
        "Literature source labels are missing."
    )

    for result in results:

        assert result["source"] in novelty_prompt, (
            "A retrieved literature source is missing "
            "from the novelty prompt."
        )

    print(
        "PASS: Literature evidence and sources"
    )

    # -----------------------------------------------------
    # 8. Check required novelty sections
    # -----------------------------------------------------

    print(
        "\n[8] Checking novelty-analysis structure..."
    )

    required_sections = [
        "## Research Focus",
        "## Similarity Evidence",
        "## Differences",
        "## Potentially Distinctive Aspects",
        "## Researcher Validation",
    ]

    for section in required_sections:

        assert section in novelty_prompt, (
            f"Missing novelty-analysis section: "
            f"{section}"
        )

        print(
            f"PASS: {section}"
        )

    # -----------------------------------------------------
    # 9. Check novelty safety constraints
    # -----------------------------------------------------

    print(
        "\n[9] Checking novelty safety constraints..."
    )

    normalized_prompt = " ".join(
        novelty_prompt.lower().split()
    )

    required_safety_phrases = [
        "do not claim that the uploaded paper is definitely novel or non-novel",
        "do not claim that a research gap has been proven or definitively identified",
        "do not make unsupported claims about originality",
    ]

    for phrase in required_safety_phrases:

        normalized_phrase = " ".join(
            phrase.lower().split()
        )

        assert normalized_phrase in normalized_prompt, (
            f"Missing safety instruction: {phrase}"
        )

    print(
        "PASS: Novelty safety constraints"
    )

    # -----------------------------------------------------
    # Final result
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("CROSS-PAPER EVALUATION PASSED")
    print("=" * 60)


# ---------------------------------------------------------
# Run evaluation
# ---------------------------------------------------------

if __name__ == "__main__":
    evaluate_cross_paper_analysis()