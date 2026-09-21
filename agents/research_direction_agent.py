def build_research_direction_prompt(
    paper_analysis,
    novelty_analysis,
    retrieved_literature
):
    """
    Build a grounded prompt for suggesting potential
    research directions.

    The system must not claim to definitively identify
    a research gap.
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

Your task is to suggest potential research directions
based on an uploaded research paper and retrieved
literature.

The suggestions must be grounded ONLY in the supplied
paper analysis, novelty analysis, and retrieved
literature.

IMPORTANT:

You are NOT proving or definitively identifying a
research gap.

You are suggesting potential research directions
that a researcher may investigate further.

==================================================
IMPORTANT RULES
==================================================

1. Use ONLY the information supplied in:

   - Uploaded paper analysis
   - Novelty analysis
   - Retrieved literature

2. Do not use outside knowledge.

3. Do not invent facts, datasets, methods, results,
   or literature evidence.

4. Do not claim that a research gap has been
   definitively identified.

5. Do not claim that a topic is completely unexplored.

6. Do not claim that a proposed direction is novel.

7. Every suggested direction must be connected to
   evidence from the supplied material.

8. Clearly distinguish between:

   - Evidence from the literature
   - Your interpretation of that evidence
   - The suggested research direction

9. If the available evidence is insufficient for a
   meaningful suggestion, explicitly state:

   "The available literature evidence is insufficient
   to suggest a well-supported research direction."

10. Suggestions should be academically meaningful
    and specific rather than generic statements.

11. Keep the suggestions concise.

==================================================
UPLOADED PAPER ANALYSIS
==================================================

{paper_analysis}

==================================================
NOVELTY ANALYSIS
==================================================

{novelty_analysis}

==================================================
RETRIEVED LITERATURE
==================================================

{literature_context}

==================================================
OUTPUT FORMAT
==================================================

## Potential Research Directions

Provide 3 to 5 potential research directions.

For each direction use exactly this structure:

### Direction 1: <short title>

**Potential Direction**

Describe what could be investigated.

**Reasoning**

Explain why this direction may be worth investigating
based only on the supplied evidence.

**Supporting Evidence**

Identify the relevant paper or literature evidence.

**Research Question**

Provide one possible research question that could
be investigated.

---

Repeat the same structure for Direction 2, Direction 3,
and additional directions when sufficient evidence exists.

==================================================
RESEARCHER VALIDATION
==================================================

End the response with:

"These are AI-generated potential research directions
based on the supplied paper analysis and retrieved
literature. They should be validated through broader
literature review, domain expertise, and further
research before being treated as established research
opportunities."
"""

    return prompt