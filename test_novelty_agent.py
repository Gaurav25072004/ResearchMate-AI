from agents.novelty_agent import (
    build_novelty_analysis_prompt
)


paper_analysis = """
Research Problem:
The paper studies how large language models
can assess novelty in scholarly publications.

Research Objectives:
The study proposes an approach for evaluating
novelty using retrieved scholarly information.

Methodology:
The approach uses retrieval augmented generation,
temporal retrieval, embeddings, and language models.

Dataset / Data:
The study uses scholarly publications from arXiv.

Main Contributions:
The paper proposes a framework for LLM-based
novelty assessment.
"""


retrieved_literature = [
    """
Paper A:
This work studies creativity assessment using
large language models and scholarly literature.
It uses language models to evaluate creative
ideas.
""",

    """
Paper B:
This research investigates retrieval augmented
generation for academic literature analysis.
The approach retrieves relevant scholarly
documents before generating an assessment.
""",

    """
Paper C:
This study examines temporal information in
scientific literature and uses publication
metadata for analysis.
"""
]


prompt = build_novelty_analysis_prompt(
    paper_analysis,
    retrieved_literature
)


print("=" * 70)
print("DAY 10 - NOVELTY AGENT PROMPT TEST")
print("=" * 70)

print()

print(prompt)

print()

print("=" * 70)
print("TEST RESULT")
print("=" * 70)

if prompt.strip():

    print(
        "Novelty analysis prompt created successfully!"
    )

else:

    print(
        "ERROR: Prompt is empty."
    )