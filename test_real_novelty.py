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
from agents.novelty_agent import (
    build_novelty_analysis_prompt
)


# ============================================================
# Configuration
# ============================================================

PDF_PATH = r"D:\My capstone Research papers\2025.aisd-main.5.pdf"


# ============================================================
# Step 1: Extract PDF text
# ============================================================

print("\n========================================")
print("STEP 1: PDF EXTRACTION")
print("========================================")

with open(PDF_PATH, "rb") as pdf_file:

    text, page_count = extract_text_from_pdf(
        pdf_file
    )

print("Pages:", page_count)
print("Characters:", len(text))


# ============================================================
# Step 2: Clean text
# ============================================================

print("\n========================================")
print("STEP 2: TEXT CLEANING")
print("========================================")

cleaned_text = clean_text(text)

print("Cleaned characters:", len(cleaned_text))


# ============================================================
# Step 3: Create chunks
# ============================================================

print("\n========================================")
print("STEP 3: TEXT CHUNKING")
print("========================================")

chunks = split_text_into_chunks(
    cleaned_text
)

print("Number of chunks:", len(chunks))


# ============================================================
# Step 4: Load embedding model
# ============================================================

print("\n========================================")
print("STEP 4: EMBEDDING MODEL")
print("========================================")

embedding_model = load_embedding_model()

print("Embedding model loaded successfully.")


# ============================================================
# Step 5: Generate embeddings
# ============================================================

print("\n========================================")
print("STEP 5: EMBEDDINGS")
print("========================================")

embeddings = generate_embeddings(
    chunks,
    embedding_model
)

print("Number of embeddings:", len(embeddings))


# ============================================================
# Step 6: Create FAISS index
# ============================================================

print("\n========================================")
print("STEP 6: FAISS INDEX")
print("========================================")

faiss_index = create_faiss_index(
    embeddings
)

print(
    "FAISS vectors:",
    faiss_index.ntotal
)


# ============================================================
# Step 7: Retrieve paper-analysis context
# ============================================================

print("\n========================================")
print("STEP 7: PAPER ANALYSIS RETRIEVAL")
print("========================================")

analysis_query = """
What is the research problem, methodology,
dataset, results, contributions, and limitations
of this research paper?
"""

analysis_embedding = embedding_model.encode(
    [analysis_query]
)[0]

analysis_results = hybrid_search(
    faiss_index,
    analysis_embedding,
    analysis_query,
    chunks,
    top_k=7
)

print(
    "Retrieved analysis results:",
    len(analysis_results)
)


# ============================================================
# Extract actual chunk text
# ============================================================

analysis_chunks = [
    result["chunk"]
    for result in analysis_results
]


# ============================================================
# Step 8: Generate structured paper analysis
# ============================================================

print("\n========================================")
print("STEP 8: STRUCTURED PAPER ANALYSIS")
print("========================================")

paper_analysis_prompt = build_paper_analysis_prompt(
    analysis_chunks
)

gemini_client = load_gemini_model()

paper_analysis = generate_answer(
    gemini_client,
    paper_analysis_prompt
)

print("\n")
print(paper_analysis)


# ============================================================
# Step 9: Retrieve related literature
# ============================================================

print("\n========================================")
print("STEP 9: RELATED LITERATURE RETRIEVAL")
print("========================================")

literature_query = """
Find research related to the problem,
methodology, techniques, datasets, and
contributions discussed in this paper.
"""

literature_embedding = embedding_model.encode(
    [literature_query]
)[0]

literature_results = hybrid_search(
    faiss_index,
    literature_embedding,
    literature_query,
    chunks,
    top_k=7
)

print(
    "Retrieved literature results:",
    len(literature_results)
)


# ============================================================
# Extract literature chunk text
# ============================================================

literature_chunks = [
    result["chunk"]
    for result in literature_results
]


# ============================================================
# Step 10: Build Novelty Analysis prompt
# ============================================================

print("\n========================================")
print("STEP 10: NOVELTY ANALYSIS PROMPT")
print("========================================")

novelty_prompt = build_novelty_analysis_prompt(
    paper_analysis,
    literature_chunks
)

print(
    "Novelty analysis prompt created successfully."
)


# ============================================================
# Step 11: Generate Novelty Analysis
# ============================================================

print("\n========================================")
print("STEP 11: NOVELTY ANALYSIS")
print("========================================")

novelty_analysis = generate_answer(
    gemini_client,
    novelty_prompt
)

print("\n")
print(novelty_analysis)


# ============================================================
# Final status
# ============================================================

print("\n========================================")
print("DAY 10 NOVELTY ANALYSIS TEST COMPLETE")
print("========================================")