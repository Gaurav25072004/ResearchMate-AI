from rag.citation_analyzer import (
    extract_references_section,
    parse_references,
    analyze_citations
)


sample_text = """
Section: Introduction

This is an example research paper.

## References

[1] Vaswani, A., Shazeer, N., Parmar, N.
Attention Is All You Need. 2017.

[2] Lewis, P., Perez, E., Piktus, A.
Retrieval-Augmented Generation. 2020.

[3] Brown, T., Mann, B., Ryder, N.
Language Models are Few-Shot Learners. 2020.
"""


print("=" * 60)
print("TEST 1: EXTRACT REFERENCES SECTION")
print("=" * 60)

references_section = extract_references_section(
    sample_text
)

print(references_section)


print()
print("=" * 60)
print("TEST 2: PARSE REFERENCES")
print("=" * 60)

references = parse_references(
    references_section
)

for reference in references:
    print(reference)


print()
print("=" * 60)
print("TEST 3: CITATION ANALYSIS")
print("=" * 60)

result = analyze_citations(
    sample_text
)

print(
    "Total references:",
    result["total_references"]
)

print(
    "Parsed references:",
    len(result["references"])
)