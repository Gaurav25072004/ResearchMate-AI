import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.research_direction_agent import (
    build_research_direction_prompt
)


# ---------------------------------------------------------
# Evaluation inputs
# ---------------------------------------------------------

PAPER_ANALYSIS = """
## Research Problem

The paper studies automated evaluation of novelty
in scientific ideas.

## Research Objectives

The research aims to develop a literature-grounded
novelty assessment framework.

## Methodology

The system uses literature retrieval and
LLM-based assessment.

## Dataset / Data

The study uses expert-annotated scientific ideas.

## Results / Findings

The study reports results from expert evaluation.

## Main Contributions

The paper proposes an automated novelty
assessment framework.

## Limitations

The paper discusses subjectivity in novelty
assessment.
"""


NOVELTY_ANALYSIS = """
## Research Focus

The paper focuses on literature-grounded
novelty assessment.

## Similarity Evidence

Retrieved literature also studies scientific
novelty evaluation using language models.

## Differences

The uploaded paper uses a specific retrieval
and assessment pipeline.

## Potentially Distinctive Aspects

The paper combines literature retrieval with
structured novelty assessment.

## Researcher Validation

These observations require broader literature
review and domain expertise.
"""


RETRIEVED_LITERATURE = [
    {
        "source": "paper_a.pdf",
        "chunk": (
            "The study investigates scientific novelty "
            "evaluation using language models."
        )
    },
    {
        "source": "paper_b.pdf",
        "chunk": (
            "The authors evaluate different approaches "
            "for assessing novelty against prior literature."
        )
    },
]


# ---------------------------------------------------------
# Evaluation
# ---------------------------------------------------------

def evaluate_research_directions():

    print("=" * 60)
    print(
        "RESEARCHMATE AI - RESEARCH DIRECTIONS EVALUATION"
    )
    print("=" * 60)

    # -----------------------------------------------------
    # 1. Build prompt
    # -----------------------------------------------------

    print(
        "\n[1] Building research-direction prompt..."
    )

    prompt = build_research_direction_prompt(
        PAPER_ANALYSIS,
        NOVELTY_ANALYSIS,
        RETRIEVED_LITERATURE
    )

    assert prompt.strip(), (
        "Research-direction prompt is empty."
    )

    print("Prompt created.")
    print("PASS: Prompt construction")

    # -----------------------------------------------------
    # 2. Check required main section
    # -----------------------------------------------------

    print(
        "\n[2] Checking required output section..."
    )

    assert (
        "## Potential Research Directions" in prompt
    ), (
        "Potential Research Directions section "
        "is missing."
    )

    print(
        "PASS: Potential Research Directions section"
    )

    # -----------------------------------------------------
    # 3. Check direction structure
    # -----------------------------------------------------

    print(
        "\n[3] Checking direction structure..."
    )

    required_structure = [
        "**Potential Direction**",
        "**Reasoning**",
        "**Supporting Evidence**",
        "**Research Question**",
    ]

    for item in required_structure:

        assert item in prompt, (
            f"Missing direction structure: {item}"
        )

        print(f"PASS: {item}")

    # -----------------------------------------------------
    # 4. Check number of directions requirement
    # -----------------------------------------------------

    print(
        "\n[4] Checking direction-count requirement..."
    )

    normalized_prompt = " ".join(
        prompt.lower().split()
    )

    assert (
        "provide 3 to 5 potential research directions"
        in normalized_prompt
    ), (
        "Prompt does not require 3 to 5 "
        "potential research directions."
    )

    print(
        "PASS: 3-5 direction requirement"
    )

    # -----------------------------------------------------
    # 5. Check evidence-grounding rules
    # -----------------------------------------------------

    print(
        "\n[5] Checking evidence-grounding rules..."
    )

    evidence_phrases = [
        "use only the information supplied",
        "do not use outside knowledge",
        "do not invent facts",
        "every suggested direction must be connected",
        "supporting evidence",
    ]

    for phrase in evidence_phrases:

        assert phrase in normalized_prompt, (
            f"Missing evidence-grounding rule: {phrase}"
        )

    print(
        "PASS: Evidence-grounding rules"
    )

    # -----------------------------------------------------
    # 6. Check research-gap safeguards
    # -----------------------------------------------------

    print(
        "\n[6] Checking research-gap safeguards..."
    )

    safety_phrases = [
        "you are not proving or definitively identifying a research gap",
        "do not claim that a research gap has been definitively identified",
        "do not claim that a topic is completely unexplored",
        "do not claim that a proposed direction is novel",
    ]

    for phrase in safety_phrases:

        normalized_phrase = " ".join(
            phrase.lower().split()
        )

        assert normalized_phrase in normalized_prompt, (
            f"Missing safety rule: {phrase}"
        )

    print(
        "PASS: Research-gap and novelty safeguards"
    )

    # -----------------------------------------------------
    # 7. Check researcher validation
    # -----------------------------------------------------

    print(
        "\n[7] Checking researcher validation..."
    )

    assert (
        "researcher validation" in normalized_prompt
    ), (
        "Researcher Validation section is missing."
    )

    assert (
        "broader literature review" in normalized_prompt
    ), (
        "Broader literature-review validation "
        "requirement is missing."
    )

    assert (
        "domain expertise" in normalized_prompt
    ), (
        "Domain-expertise validation requirement "
        "is missing."
    )

    print(
        "PASS: Researcher validation"
    )

    # -----------------------------------------------------
    # 8. Check literature source handling
    # -----------------------------------------------------

    print(
        "\n[8] Checking literature source handling..."
    )

    assert "SOURCE: paper_a.pdf" in prompt, (
        "paper_a.pdf source is missing."
    )

    assert "SOURCE: paper_b.pdf" in prompt, (
        "paper_b.pdf source is missing."
    )

    print(
        "PASS: Literature source handling"
    )

    # -----------------------------------------------------
    # Final result
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("RESEARCH DIRECTIONS EVALUATION PASSED")
    print("=" * 60)


# ---------------------------------------------------------
# Run evaluation
# ---------------------------------------------------------

if __name__ == "__main__":
    evaluate_research_directions()