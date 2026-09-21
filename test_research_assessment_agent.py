from agents.research_assessment_agent import (
    build_research_assessment_prompt
)


def main():
    paper_analysis = """
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

    citation_analysis = {
        "page_count": 18,
        "reference_blocks": 2,
        "total_references": 35,
        "references": [
            "Reference 1",
            "Reference 2"
        ]
    }

    prompt = build_research_assessment_prompt(
        paper_analysis,
        citation_analysis
    )

    print("=" * 60)
    print("RESEARCH ASSESSMENT PROMPT TEST")
    print("=" * 60)

    print(prompt)

    assert "Research Assessment" in prompt
    assert "Research Problem Clarity" in prompt
    assert "Research Objective Clarity" in prompt
    assert "Methodology Reporting" in prompt
    assert "Dataset / Data Reporting" in prompt
    assert "Results / Findings Reporting" in prompt
    assert "Contribution Reporting" in prompt
    assert "Limitation Reporting" in prompt
    assert "Citation / Reference Information" in prompt

    assert "Do NOT provide a numerical research-quality score." in prompt
    assert "Do NOT rank the paper." in prompt

    assert "18" in prompt
    assert "35" in prompt

    print("=" * 60)
    print("TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()