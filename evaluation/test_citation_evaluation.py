import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from rag.citation_analyzer import analyze_pdf_citations


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

PAPER_PATH = Path(
    r"D:\My capstone Research papers\2506.22026v1.pdf"
)


# ---------------------------------------------------------
# Citation Analysis Evaluation
# ---------------------------------------------------------

def evaluate_citation_analysis():

    print("=" * 60)
    print("RESEARCHMATE AI - CITATION ANALYSIS EVALUATION")
    print("=" * 60)

    # -----------------------------------------------------
    # 1. Check paper
    # -----------------------------------------------------

    print("\n[1] Checking research paper...")

    assert PAPER_PATH.exists(), (
        f"Research paper not found: {PAPER_PATH}"
    )

    print(f"Paper found: {PAPER_PATH.name}")
    print("PASS: Research paper availability")

    # -----------------------------------------------------
    # 2. Run citation analysis
    # -----------------------------------------------------

    print("\n[2] Running citation analysis...")

    result = analyze_pdf_citations(
        str(PAPER_PATH)
    )

    assert isinstance(result, dict), (
        "Citation analysis result must be a dictionary."
    )

    print("Citation analysis completed.")

    # -----------------------------------------------------
    # 3. Check required fields
    # -----------------------------------------------------

    print("\n[3] Checking required result fields...")

    required_fields = [
        "page_count",
        "reference_blocks",
        "total_references",
        "references",
        "parsed_references",
    ]

    for field in required_fields:

        assert field in result, (
            f"Missing citation-analysis field: {field}"
        )

        print(f"PASS: {field}")

    # -----------------------------------------------------
    # 4. Check page count
    # -----------------------------------------------------

    print("\n[4] Checking page count...")

    page_count = result["page_count"]

    assert isinstance(page_count, int), (
        "page_count must be an integer."
    )

    assert page_count > 0, (
        "page_count must be greater than zero."
    )

    print(f"Pages detected: {page_count}")
    print("PASS: Page count")

    # -----------------------------------------------------
    # 5. Check reference blocks
    # -----------------------------------------------------

    print("\n[5] Checking reference blocks...")

    reference_blocks = result["reference_blocks"]

    assert isinstance(reference_blocks, int), (
        "reference_blocks must be an integer."
    )

    assert reference_blocks >= 0, (
        "reference_blocks cannot be negative."
    )

    print(
        f"Reference blocks detected: "
        f"{reference_blocks}"
    )

    print("PASS: Reference block information")

    # -----------------------------------------------------
    # 6. Check total references
    # -----------------------------------------------------

    print("\n[6] Checking total references...")

    total_references = result["total_references"]

    assert isinstance(total_references, int), (
        "total_references must be an integer."
    )

    assert total_references >= 0, (
        "total_references cannot be negative."
    )

    print(
        f"Total references: "
        f"{total_references}"
    )

    print("PASS: Total reference count")

    # -----------------------------------------------------
    # 7. Check reference list
    # -----------------------------------------------------

    print("\n[7] Checking extracted references...")

    references = result["references"]

    assert isinstance(references, list), (
        "references must be a list."
    )

    if total_references > 0:

        assert len(references) > 0, (
            "Reference count is greater than zero, "
            "but references list is empty."
        )

    print(
        f"Reference entries available: "
        f"{len(references)}"
    )

    print("PASS: Extracted references")

    # -----------------------------------------------------
    # 8. Check parsed references
    # -----------------------------------------------------

    print("\n[8] Checking parsed references...")

    parsed_references = result["parsed_references"]

    assert isinstance(parsed_references, list), (
        "parsed_references must be a list."
    )

    if total_references > 0:

        assert len(parsed_references) > 0, (
            "Reference count is greater than zero, "
            "but parsed_references is empty."
        )

    print(
        f"Parsed references available: "
        f"{len(parsed_references)}"
    )

    print("PASS: Parsed references")

    # -----------------------------------------------------
    # 9. Inspect parsed reference structure
    # -----------------------------------------------------

    print("\n[9] Inspecting parsed reference structure...")

    if parsed_references:

        first_reference = parsed_references[0]

        assert isinstance(first_reference, str), (
            "Each parsed reference should be a string."
        )

        assert first_reference.strip(), (
            "Parsed reference cannot be empty."
        )

        print("First parsed reference:")
        print(first_reference)

        print("PASS: Parsed reference structure")

    else:

        print(
            "No parsed references available to inspect."
        )

    # -----------------------------------------------------
    # Final result
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("CITATION ANALYSIS EVALUATION PASSED")
    print("=" * 60)


# ---------------------------------------------------------
# Run evaluation
# ---------------------------------------------------------

if __name__ == "__main__":
    evaluate_citation_analysis()