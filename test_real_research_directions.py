from rag.llm import load_gemini_model, generate_answer
from agents.research_direction_agent import (
    build_research_direction_prompt
)


paper_analysis = """
The paper proposes a retrieval-augmented approach
for evaluating the novelty of scientific ideas.
It combines information retrieval with large
language models to compare scientific ideas with
existing literature.
"""


novelty_analysis = """
## Research Focus

The paper focuses on evaluating the novelty of
scientific ideas using retrieved literature.

## Similarity Evidence

The retrieved literature also uses retrieval
and language-model-based approaches.

## Differences

The uploaded paper focuses specifically on
scientific idea novelty evaluation.

## Potentially Distinctive Aspects

The combination of retrieval and LLM-based
comparison appears potentially distinctive
within the supplied literature.
"""


retrieved_literature = [
    {
        "source": "2026.eacl-long.121.pdf",
        "chunk": """
        The paper describes a retrieval-based
        approach for processing and comparing
        information from scientific documents.
        """
    },
    {
        "source": "2026.findings-acl.1607.pdf",
        "chunk": """
        The study discusses language-model-based
        processing of research literature.
        """
    }
]


print("=" * 70)
print("REAL RESEARCH DIRECTIONS TEST")
print("=" * 70)


print("\nLoading Gemini...")
client = load_gemini_model()

print("Building research direction prompt...")

prompt = build_research_direction_prompt(
    paper_analysis,
    novelty_analysis,
    retrieved_literature
)

print("Generating potential research directions...\n")

answer = generate_answer(
    client,
    prompt
)


print("=" * 70)
print("GENERATED POTENTIAL RESEARCH DIRECTIONS")
print("=" * 70)

print(answer)


print("\n" + "=" * 70)
print("REAL RESEARCH DIRECTIONS TEST COMPLETE")
print("=" * 70)