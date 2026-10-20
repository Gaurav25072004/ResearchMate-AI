# Retrieval Relevance Judgments — Day 21

## Purpose

This file records graded relevance judgments for the top five passages returned by the hybrid retrieval system in ResearchMate AI.

The evaluation uses one research paper and six queries. Each retrieved passage is assigned a relevance score from 0 to 2 based on how well it answers the query.

## Relevance Rating Rubric

- **2 — Highly relevant:** The passage directly answers the query or provides strong, specific evidence.
- **1 — Partially relevant:** The passage provides related information but does not fully answer the query.
- **0 — Not relevant:** The passage does not meaningfully answer the query.

## Judgment Method

The original three queries were reviewed against their full retrieved passages on Day 20. The three additional queries were reviewed against their full retrieved passages on Day 21.

The relevance ratings are based on the content of the retrieved passages and the rubric above. The nDCG@5 scores measure how well the ordering of passages aligns with these ratings. They do not independently establish the correctness of the judgments.

## Query 1: What methodology was used in the study?

| Rank | Relevance rating | Reason |
|---:|---:|---|
| 1 | 2 | Directly addresses the study methodology. |
| 2 | 1 | Provides related methodological information. |
| 3 | 1 | Provides partially relevant methodological context. |
| 4 | 1 | Provides related information but does not fully answer the query. |
| 5 | 1 | Provides additional related methodological context. |

**Relevance ratings:** `[2, 1, 1, 1, 1]`

**nDCG@5:** 1.000

## Query 2: What dataset or data was used?

| Rank | Relevance rating | Reason |
|---:|---:|---|
| 1 | 1 | Provides related information about the data. |
| 2 | 2 | Directly describes the dataset or data used. |
| 3 | 1 | Provides partially relevant data-related context. |
| 4 | 0 | Does not meaningfully answer the dataset question. |
| 5 | 0 | Does not meaningfully answer the dataset question. |

**Relevance ratings:** `[1, 2, 1, 0, 0]`

**nDCG@5:** 0.821

## Query 3: What were the main results of the research?

| Rank | Relevance rating | Reason |
|---:|---:|---|
| 1 | 2 | Directly reports important research results. |
| 2 | 2 | Provides strong evidence about the research results. |
| 3 | 1 | Provides related findings or results context. |
| 4 | 1 | Provides partially relevant results-related information. |
| 5 | 2 | Provides strong evidence about the main results. |

**Relevance ratings:** `[2, 2, 1, 1, 2]`

**nDCG@5:** 0.969

## Query 4: What limitations of the study are discussed?

| Rank | Relevance rating | Reason |
|---:|---:|---|
| 1 | 1 | Discusses challenges involving subjective novelty criteria and disagreement, providing related limitations context. |
| 2 | 2 | Directly discusses limitations and future work, including context constraints, annotation concerns, and planned expansion. |
| 3 | 1 | Discusses prompt sensitivity, which is related to methodological limitations. |
| 4 | 0 | Primarily describes implementation and baselines rather than study limitations. |
| 5 | 1 | Provides related context about subjective criteria and expert disagreement. |

**Relevance ratings:** `[1, 2, 1, 0, 1]`

**nDCG@5:** 0.829

## Query 5: What are the main contributions of the research?

| Rank | Relevance rating | Reason |
|---:|---:|---|
| 1 | 2 | Describes the proposed retrieval-augmented novelty-checking pipeline and its main components. |
| 2 | 1 | Provides related background about novelty definitions and the formative study. |
| 3 | 2 | Describes the system architecture and pipeline, supporting understanding of the research contribution. |
| 4 | 1 | Provides related formative-study details and agreement results. |
| 5 | 1 | Provides supporting context about observations informing the methodology. |

**Relevance ratings:** `[2, 1, 2, 1, 1]`

**nDCG@5:** 0.958

## Query 6: How was the proposed system evaluated?

| Rank | Relevance rating | Reason |
|---:|---:|---|
| 1 | 2 | Describes implementation, datasets, and baseline comparisons used in the evaluation. |
| 2 | 1 | Provides related formative-study and annotation context. |
| 3 | 2 | Directly describes comparisons with alternative approaches and reports evaluation results. |
| 4 | 1 | Provides related study and agreement details but does not directly describe the full evaluation setup. |
| 5 | 2 | Describes the evaluation dataset, consensus-labeled examples, and baseline setup. |

**Relevance ratings:** `[2, 1, 2, 1, 2]`

**nDCG@5:** 0.932

## Summary of Results

| Query | Relevance ratings, ranks 1–5 | nDCG@5 |
|---|---|---:|
| Methodology | 2, 1, 1, 1, 1 | 1.000 |
| Dataset or data | 1, 2, 1, 0, 0 | 0.821 |
| Main research results | 2, 2, 1, 1, 2 | 0.969 |
| Study limitations | 1, 2, 1, 0, 1 | 0.829 |
| Research contributions | 2, 1, 2, 1, 1 | 0.958 |
| System evaluation | 2, 1, 2, 1, 2 | 0.932 |
| **Mean across six queries** | — | **0.918** |

## Evaluation Notes

- The top five retrieved passages were reviewed for each of the six queries.
- The evaluation uses one research paper and six queries; the sample is too limited to support broad generalizations about retrieval quality.
- nDCG@5 measures ranking alignment with the entered relevance judgments. It does not independently establish whether those judgments are correct.
- Keyword-proxy metrics and graded relevance metrics measure different aspects of retrieval and should be reported separately.
- The evaluation does not compare retrieval methods or establish improvement over a baseline.
- The results do not establish answer completeness, factual correctness, scientific validity, or research originality.
- Further evaluation across multiple papers, more queries, and independently reviewed judgments is needed before drawing wider conclusions.

## Conclusion

Day 21 expanded the graded retrieval relevance evaluation from three to six queries. The resulting mean nDCG@5 is 0.918 based on the recorded relevance ratings. This is an initial assessment of ranking quality for the evaluated paper and queries, not proof of overall retrieval accuracy or improvement.
