import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.research_assessment_agent import (
    build_research_assessment_prompt
)


# ---------------------------------------------------------
# Controlled evaluation inputs
# ---------------------------------------------------------

PAPER_ANALYSIS = """
## Research Problem

The paper investigates automated assessment of
scientific research novelty.

## Research Objectives

The research aims to develop a structured
literature-grounded assessment approach.

## Methodology

The system uses retrieval and language-model
based analysis.

## Dataset / Data

The study uses a collection of expert-annotated
research examples.

## Results / Findings

The paper reports evaluation results based on
expert assessment.

## Main Contributions

The paper proposes a structured assessment
framework.

## Limitations

The authors discuss limitations related to
evaluation subjectivity.
"""


CITATION_ANALYSIS = """
## Citation Analysis

The paper contains 57 extracted references.

The citation analysis identified 101 reference
blocks across 18 pages.

The references were successfully parsed.
"""


# ---------------------------------------------------------
# Evaluation
# ---------------------------------------------------------

def evaluate_research_assessment():

    print("=" * 60)
    print(
        "RESEARCHMATE AI - RESEARCH ASSESSMENT EVALUATION"
    )
    print("=" * 60)

    # -----------------------------------------------------
    # 1. Build prompt
    # -----------------------------------------------------

    print(
        "\n[1] Building research-assessment prompt..."
    )

    prompt = build_research_assessment_prompt(
        PAPER_ANALYSIS,
        CITATION_ANALYSIS
    )

    assert prompt.strip(), (
        "Research-assessment prompt is empty."
    )

    print("Prompt created.")
    print("PASS: Prompt construction")

    normalized_prompt = " ".join(
        prompt.lower().split()
    )

    # -----------------------------------------------------
    # 2. Check main section
    # -----------------------------------------------------

    print(
        "\n[2] Checking main assessment section..."
    )

    assert (
        "## research assessment" in normalized_prompt
    ), (
        "Research Assessment section is missing."
    )

    print(
        "PASS: Research Assessment section"
    )

    # -----------------------------------------------------
    # 3. Check all eight assessment categories
    # -----------------------------------------------------

    print(
        "\n[3] Checking assessment categories..."
    )

    required_categories = [
        "1. research problem clarity",
        "2. research objective clarity",
        "3. methodology reporting",
        "4. dataset / data reporting",
        "5. results / findings reporting",
        "6. contribution reporting",
        "7. limitation reporting",
        "8. citation / reference information",
    ]

    for category in required_categories:

        assert category in normalized_prompt, (
            f"Missing assessment category: {category}"
        )

        print(
            f"PASS: {category}"
        )

    # -----------------------------------------------------
    # 4. Check assessment classifications
    # -----------------------------------------------------

    print(
        "\n[4] Checking assessment classifications..."
    )

    classifications = [
        "clearly reported",
        "partially reported",
        "insufficient information",
    ]

    for classification in classifications:

        assert classification in normalized_prompt, (
            f"Missing classification: {classification}"
        )

        print(
            f"PASS: {classification}"
        )

    # -----------------------------------------------------
    # 5. Check evidence requirement
    # -----------------------------------------------------

    print(
        "\n[5] Checking evidence requirement..."
    )

    assert "**evidence:**" in normalized_prompt, (
        "Evidence requirement is missing."
    )

    assert (
        "base every assessment on evidence"
        in normalized_prompt
    ), (
        "Prompt does not require evidence-based "
        "assessment."
    )

    print(
        "PASS: Evidence-based assessment"
    )

    # -----------------------------------------------------
    # 6. Check citation analysis integration
    # -----------------------------------------------------

    print(
        "\n[6] Checking citation-analysis integration..."
    )

    assert "citation analysis" in normalized_prompt, (
        "Citation analysis is not included."
    )

    assert "total reference information" in normalized_prompt, (
        "Reference-count information requirement "
        "is missing."
    )

    print(
        "PASS: Citation-analysis integration"
    )

    # -----------------------------------------------------
    # 7. Check overall summary
    # -----------------------------------------------------

    print(
        "\n[7] Checking overall assessment summary..."
    )

    assert (
        "overall assessment summary"
        in normalized_prompt
    ), (
        "Overall Assessment Summary is missing."
    )

    assert (
        "aspects that are clearly reported"
        in normalized_prompt
    ), (
        "Clearly reported summary requirement "
        "is missing."
    )

    assert (
        "aspects that are partially reported"
        in normalized_prompt
    ), (
        "Partially reported summary requirement "
        "is missing."
    )

    assert (
        "aspects for which sufficient information "
        "is unavailable"
        in normalized_prompt
    ), (
        "Insufficient-information summary requirement "
        "is missing."
    )

    print(
        "PASS: Overall assessment summary"
    )

    # -----------------------------------------------------
    # 8. Check research-quality safeguards
    # -----------------------------------------------------

    print(
        "\n[8] Checking research-quality safeguards..."
    )

    required_safety_phrases = [
        "this is not an objective measurement of research quality",
        "do not claim that the paper is good or bad",
        "do not claim that the research is novel",
        "do not claim that the methodology is scientifically valid",
        "do not provide a numerical research-quality score",
        "do not rank the paper",
    ]

    for phrase in required_safety_phrases:

        assert phrase in normalized_prompt, (
            f"Missing safety rule: {phrase}"
        )

    print(
        "PASS: Research-quality safeguards"
    )

    # -----------------------------------------------------
    # 9. Check researcher validation
    # -----------------------------------------------------

    print(
        "\n[9] Checking researcher validation..."
    )

    assert (
        "researcher validation"
        in normalized_prompt
    ), (
        "Researcher Validation section is missing."
    )

    assert (
        "structured aid for reviewing the paper"
        in normalized_prompt
    ), (
        "Structured-review limitation is missing."
    )

    assert (
        "scientific validity"
        in normalized_prompt
    ), (
        "Scientific-validity limitation is missing."
    )

    assert (
        "originality"
        in normalized_prompt
    ), (
        "Originality limitation is missing."
    )

    print(
        "PASS: Researcher validation"
    )

    # -----------------------------------------------------
    # 10. Check no-score/no-ranking requirement
    # -----------------------------------------------------

    print(
        "\n[10] Checking no-score/no-ranking requirement..."
    )

    assert (
        "do not provide a numerical research-quality score"
        in normalized_prompt
    ), (
        "Numerical research-quality score prohibition "
        "is missing."
    )

    assert (
        "do not rank the paper"
        in normalized_prompt
    ), (
        "Ranking prohibition is missing."
    )

    print(
        "PASS: No numerical score or ranking"
    )

    # -----------------------------------------------------
    # Final result
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("RESEARCH ASSESSMENT EVALUATION PASSED")
    print("=" * 60)


# ---------------------------------------------------------
# Run evaluation
# ---------------------------------------------------------

if __name__ == "__main__":
    evaluate_research_assessment()