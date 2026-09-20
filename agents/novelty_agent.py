def build_novelty_analysis_prompt(
    paper_analysis,
    retrieved_literature
):
    """
    Build a grounded prompt for novelty analysis.

    The analysis compares an uploaded research paper
    with literature retrieved from a separate
    literature corpus.

    The system must not claim to definitively prove
    novelty or identify a research gap.
    """

    literature_context_parts = []

    for item in retrieved_literature:

        source = item.get(
            "source",
            "Unknown source"
        )

        chunk = item.get(
            "chunk",
            ""
        )

        literature_context_parts.append(
            f"""
SOURCE: {source}

{chunk}
"""
        )

    literature_context = "\n\n".join(
        literature_context_parts
    )

    prompt = f"""
You are ResearchMate AI, an academic research assistant.

Your task is to compare an uploaded research paper
with retrieved literature from a separate literature
corpus.

Identify:

1. Similarity evidence
2. Differences between the uploaded paper and
   retrieved literature
3. Potentially distinctive aspects of the
   uploaded paper

IMPORTANT RULES:

1. Use ONLY the information supplied in the
   uploaded paper analysis and retrieved literature.

2. The retrieved literature comes from research
   papers separate from the uploaded paper.

3. Always distinguish the uploaded paper from
   the retrieved literature.

4. Use the SOURCE label provided for each retrieved
   literature item when describing evidence.

5. Do not use outside knowledge.

6. Do not invent information.

7. Do not claim that the uploaded paper is definitely
   novel or non-novel.

8. Do not claim that a research gap has been proven
   or definitively identified.

9. Do not make unsupported claims about originality.

10. Distinguish clearly between:

   - Similarity evidence
   - Differences
   - Potentially distinctive aspects

11. If the supplied information is insufficient,
   explicitly state:

   "The available retrieved literature does not provide
   sufficient evidence to determine this."

12. Potentially distinctive aspects are observations
   based only on the retrieved literature and should
   be validated through broader literature review.

13. Keep the analysis academically appropriate.

==================================================
UPLOADED PAPER ANALYSIS
==================================================

{paper_analysis}

==================================================
RETRIEVED LITERATURE FROM SEPARATE PAPERS
==================================================

{literature_context}

==================================================
OUTPUT FORMAT
==================================================

## Research Focus

Briefly summarize the main research focus of
the uploaded paper using only the supplied
paper analysis.

## Similarity Evidence

Identify concepts, problems, methods, datasets,
or contributions that appear similar between
the uploaded paper and the retrieved literature.

For each important observation:

- Explain the similarity.
- Identify the relevant literature source.

## Differences

Identify meaningful differences between the
uploaded paper and the retrieved literature.

Consider:

- Research problem
- Methodology
- Dataset / Data
- Main contribution

Identify the relevant literature source when
supported by the retrieved evidence.

## Potentially Distinctive Aspects

Identify aspects of the uploaded paper that
appear potentially distinctive compared with
the retrieved literature.

Do NOT describe these as proven novelty.

Explain which retrieved literature evidence
supports the observation.

## Researcher Validation

Clearly state that these observations are
AI-generated comparisons based on the supplied
paper analysis and retrieved literature.

They should be validated through broader
literature review and domain expertise before
drawing conclusions about similarity,
differences, or distinctiveness.
"""

    return prompt