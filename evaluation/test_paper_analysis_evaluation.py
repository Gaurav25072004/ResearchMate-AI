import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------
# Expected ResearchMate AI paper-analysis sections
# ---------------------------------------------------------

REQUIRED_SECTIONS = [
    "## Research Problem",
    "## Research Objectives",
    "## Methodology",
    "## Dataset / Data",
    "## Results / Findings",
    "## Main Contributions",
    "## Limitations",
]


# ---------------------------------------------------------
# Evaluation function
# ---------------------------------------------------------

def evaluate_paper_analysis(paper_analysis):
    print("=" * 60)
    print("RESEARCHMATE AI - PAPER ANALYSIS EVALUATION")
    print("=" * 60)

    assert paper_analysis.strip(), (
        "Paper analysis output is empty."
    )

    print("\n[1] Checking required sections...")

    missing_sections = []

    for section in REQUIRED_SECTIONS:
        if section not in paper_analysis:
            missing_sections.append(section)
        else:
            print(f"PASS: {section}")

    assert not missing_sections, (
        f"Missing sections: {missing_sections}"
    )

    print("\nPASS: All required sections are present.")

    # -----------------------------------------------------
    # Check that sections contain actual content
    # -----------------------------------------------------

    print("\n[2] Checking section content...")

    for index, section in enumerate(REQUIRED_SECTIONS):

        start = paper_analysis.find(section)

        if index + 1 < len(REQUIRED_SECTIONS):
            end = paper_analysis.find(
                REQUIRED_SECTIONS[index + 1]
            )
        else:
            end = len(paper_analysis)

        section_content = paper_analysis[
            start + len(section):end
        ].strip()

        assert section_content, (
            f"Section is empty: {section}"
        )

        print(f"PASS: Content found for {section}")

    # -----------------------------------------------------
    # Terminology safety checks
    # -----------------------------------------------------

    print("\n[3] Checking ResearchMate terminology...")

    prohibited_phrases = [
        "research gap has been proven",
        "definitively identified research gap",
        "definitively identifies a research gap",
    ]

    lower_output = paper_analysis.lower()

    for phrase in prohibited_phrases:
        assert phrase not in lower_output, (
            f"Prohibited phrase found: {phrase}"
        )

    print("PASS: No prohibited research-gap claims found.")

    # -----------------------------------------------------
    # Research-quality score check
    # -----------------------------------------------------

    print("\n[4] Checking for research-quality scoring...")

    prohibited_score_phrases = [
        "research quality score",
        "overall research score",
        "research quality: 10/10",
        "research quality: 9/10",
        "research quality: 8/10",
    ]

    for phrase in prohibited_score_phrases:
        assert phrase not in lower_output, (
            f"Unexpected scoring phrase found: {phrase}"
        )

    print("PASS: No research-quality score detected.")

    # -----------------------------------------------------
    # Final result
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("PAPER ANALYSIS EVALUATION PASSED")
    print("=" * 60)


# ---------------------------------------------------------
# Test data
# ---------------------------------------------------------

TEST_PAPER_ANALYSIS = """
## Research Problem

The paper addresses the problem of evaluating
novelty in scientific ideas.

## Research Objectives

The research aims to develop a literature-grounded
novelty assessment system.

## Methodology

The system uses retrieval, re-ranking, and
LLM-based assessment.

## Dataset / Data

The study uses expert-annotated scientific ideas.

## Results / Findings

The study reports moderate agreement among experts.

## Main Contributions

The paper proposes an automated novelty assessment
framework.

## Limitations

The study identifies challenges related to
subjectivity in novelty assessment.
"""


# ---------------------------------------------------------
# Run evaluation
# ---------------------------------------------------------

if __name__ == "__main__":
    evaluate_paper_analysis(TEST_PAPER_ANALYSIS)