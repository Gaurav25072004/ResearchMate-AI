from rag.pdf_loader import extract_text_from_pdf
from rag.text_processor import (
    clean_text,
    split_text_into_chunks
)
from rag.embedding import (
    load_embedding_model,
    generate_embeddings
)
from rag.vector_store import (
    create_faiss_index,
    hybrid_search
)
from rag.llm import (
    load_gemini_model,
    generate_answer,
    build_paper_analysis_prompt
)
from rag.literature_store import (
    build_literature_corpus,
    search_literature
)
from agents.novelty_agent import (
    build_novelty_analysis_prompt
)


# ============================================================
# Configuration
# ============================================================

UPLOADED_PAPER_PATH = (
    r"D:\My capstone Research papers\2506.22026v1.pdf"
)

LITERATURE_DIRECTORY = (
    r".\documents\literature"
)


# ============================================================
# STEP 1: Load uploaded paper
# ============================================================

print("\n========================================")
print("STEP 1: UPLOADED PAPER")
print("========================================")

with open(
    UPLOADED_PAPER_PATH,
    "rb"
) as pdf_file:

    paper_text, page_count = (
        extract_text_from_pdf(
            pdf_file
        )
    )

cleaned_paper = clean_text(
    paper_text
)

paper_chunks = split_text_into_chunks(
    cleaned_paper
)

print(
    "Uploaded paper pages:",
    page_count
)

print(
    "Uploaded paper chunks:",
    len(paper_chunks)
)


# ============================================================
# STEP 2: Load embedding model
# ============================================================

print("\n========================================")
print("STEP 2: EMBEDDING MODEL")
print("========================================")

embedding_model = (
    load_embedding_model()
)

print(
    "Embedding model loaded successfully."
)


# ============================================================
# STEP 3: Build uploaded-paper FAISS
# ============================================================

print("\n========================================")
print("STEP 3: UPLOADED PAPER FAISS")
print("========================================")

paper_embeddings = generate_embeddings(
    paper_chunks,
    embedding_model
)

paper_index = create_faiss_index(
    paper_embeddings
)

print(
    "Uploaded paper FAISS vectors:",
    paper_index.ntotal
)


# ============================================================
# STEP 4: Paper Analysis Retrieval
# ============================================================

print("\n========================================")
print("STEP 4: PAPER ANALYSIS RETRIEVAL")
print("========================================")

analysis_query = """
What is the research problem, research objectives,
methodology, dataset, results, contributions,
and limitations of this research paper?
"""

analysis_embedding = (
    embedding_model.encode(
        [analysis_query]
    )[0]
)

analysis_results = hybrid_search(
    paper_index,
    analysis_embedding,
    analysis_query,
    paper_chunks,
    top_k=7
)

analysis_chunks = [
    result["chunk"]
    for result in analysis_results
]

print(
    "Paper analysis results:",
    len(analysis_results)
)


# ============================================================
# STEP 5: Generate Paper Analysis
# ============================================================

print("\n========================================")
print("STEP 5: PAPER ANALYSIS")
print("========================================")

gemini_client = (
    load_gemini_model()
)

paper_analysis_prompt = (
    build_paper_analysis_prompt(
        analysis_chunks
    )
)

paper_analysis = generate_answer(
    gemini_client,
    paper_analysis_prompt
)

print(
    paper_analysis
)


# ============================================================
# STEP 6: Build SEPARATE Literature Corpus
# ============================================================

print("\n========================================")
print("STEP 6: SEPARATE LITERATURE CORPUS")
print("========================================")

literature_corpus = (
    build_literature_corpus(
        LITERATURE_DIRECTORY,
        embedding_model
    )
)

literature_papers = literature_corpus[
    "papers"
]

literature_chunks = literature_corpus[
    "chunks"
]

literature_index = literature_corpus[
    "index"
]

print(
    "Literature papers:",
    len(literature_papers)
)

print(
    "Literature chunks:",
    len(literature_chunks)
)

print(
    "Literature FAISS vectors:",
    literature_index.ntotal
)


# ============================================================
# STEP 7: Retrieve RELATED literature
# ============================================================

print("\n========================================")
print("STEP 7: RELATED LITERATURE RETRIEVAL")
print("========================================")

literature_query = f"""
Find research papers related to the following
research problem, methodology, datasets,
and contributions:

{paper_analysis}

Retrieve literature that can be used to compare
the uploaded paper with prior research.
"""

literature_results = search_literature(
    literature_corpus,
    literature_query,
    embedding_model,
    top_k=7
)

print(
    "Retrieved literature results:",
    len(literature_results)
)


# ============================================================
# Display retrieved literature
# ============================================================

for i, result in enumerate(
    literature_results,
    start=1
):

    print(
        f"\n--- Literature Result {i} ---"
    )

    print(
        "Source:",
        result["source"]
    )

    print(
        "Final Score:",
        round(
            result["final_score"],
            4
        )
    )

    print(
        "Chunk:",
        result["chunk"][:400]
    )


# ============================================================
# STEP 8: Build Novelty Analysis Prompt
# ============================================================

print("\n========================================")
print("STEP 8: NOVELTY PROMPT")
print("========================================")

novelty_prompt = (
    build_novelty_analysis_prompt(
        paper_analysis,
        literature_results
    )
)

print(
    "Novelty prompt created successfully."
)


# ============================================================
# STEP 9: Generate Novelty Analysis
# ============================================================

print("\n========================================")
print("STEP 9: NOVELTY ANALYSIS")
print("========================================")

novelty_analysis = generate_answer(
    gemini_client,
    novelty_prompt
)

print(
    novelty_analysis
)


# ============================================================
# FINAL
# ============================================================

print("\n========================================")
print("REAL CROSS-PAPER NOVELTY TEST COMPLETE")
print("========================================")