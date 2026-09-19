import streamlit as st
import tempfile
import os

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
    build_rag_prompt,
    build_paper_analysis_prompt
)

from rag.citation_analyzer import (
    analyze_pdf_citations
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ResearchMate AI",
    page_icon="📚",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

if "paper_processed" not in st.session_state:
    st.session_state.paper_processed = False

if "paper_text" not in st.session_state:
    st.session_state.paper_text = ""

if "cleaned_text" not in st.session_state:
    st.session_state.cleaned_text = ""

if "chunks" not in st.session_state:
    st.session_state.chunks = []

if "embeddings" not in st.session_state:
    st.session_state.embeddings = None

if "faiss_index" not in st.session_state:
    st.session_state.faiss_index = None

if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = ""

if "page_count" not in st.session_state:
    st.session_state.page_count = 0

if "citation_result" not in st.session_state:
    st.session_state.citation_result = None


# ============================================================
# CACHED MODELS
# ============================================================

@st.cache_resource
def get_embedding_model():
    return load_embedding_model()


@st.cache_resource
def get_gemini_model():
    return load_gemini_model()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("📚 ResearchMate AI")

st.sidebar.markdown(
    """
### AI-Powered Research Assistant

Upload a research paper and explore:

- 📄 Paper Analysis
- 🔎 Citation Analysis
- ✨ Novelty Analysis
- 🧭 Potential Research Directions
- 📊 Research Score
"""
)

page = st.sidebar.radio(
    "Navigate",
    [
        "🏠 Home",
        "📄 Paper Analysis",
        "🔎 Citation Analysis",
        "✨ Novelty Analysis",
        "🧭 Potential Research Directions",
        "📊 Research Score"
    ]
)

st.sidebar.markdown("---")

st.sidebar.info(
    """
AI-generated outputs are intended to support
researchers and should be validated using
domain knowledge and further literature review.
"""
)


# ============================================================
# HOME PAGE
# ============================================================

if page == "🏠 Home":

    st.title("📚 ResearchMate AI")

    st.subheader(
        "AI-Powered Research Assistant"
    )

    st.markdown(
        """
ResearchMate AI helps researchers analyze
academic papers using Retrieval-Augmented
Generation (RAG), semantic retrieval,
structured paper analysis, and citation analysis.
"""
    )

    st.markdown("---")

    st.header("🚀 Current Capabilities")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            """
### 📄 Paper Analysis

Extract structured information such as:

- Research Problem
- Research Objectives
- Methodology
- Dataset / Data
- Results / Findings
- Main Contributions
- Limitations
"""
        )

    with col2:

        st.markdown(
            """
### 🔎 Citation Analysis

Analyze the reference section of
a research paper and extract:

- Total references
- Reconstructed references
- References from two-column PDFs
- Multi-line references
"""
        )

    st.markdown("---")

    st.header("🧠 RAG-Based Question Answering")

    st.markdown(
        """
Ask questions about the uploaded research paper.

ResearchMate AI retrieves relevant paper content
using semantic and keyword-based retrieval and
uses Gemini to generate a grounded answer.
"""
    )

    st.markdown("---")

    st.header("⚠️ Important Disclaimer")

    st.warning(
        """
ResearchMate AI provides AI-generated assistance.

The generated analysis and suggestions should not
be treated as definitive academic conclusions.

Potential research directions should be validated
by the researcher using domain knowledge and
further literature review.
"""
    )


# ============================================================
# PDF UPLOAD
# ============================================================

if page in [
    "📄 Paper Analysis",
    "🔎 Citation Analysis",
    "✨ Novelty Analysis",
    "🧭 Potential Research Directions",
    "📊 Research Score"
]:

    st.title(page)

    uploaded_file = st.file_uploader(
        "Upload a research paper (PDF)",
        type=["pdf"]
    )

    if uploaded_file is not None:

        # ----------------------------------------------------
        # Detect new file
        # ----------------------------------------------------

        if (
            st.session_state.uploaded_file_name
            != uploaded_file.name
        ):

            st.session_state.paper_processed = False
            st.session_state.paper_text = ""
            st.session_state.cleaned_text = ""
            st.session_state.chunks = []
            st.session_state.embeddings = None
            st.session_state.faiss_index = None
            st.session_state.citation_result = None

            st.session_state.uploaded_file_name = (
                uploaded_file.name
            )

        # ----------------------------------------------------
        # Process PDF
        # ----------------------------------------------------

        if st.button(
            "🚀 Process Research Paper",
            type="primary"
        ):

            with st.spinner(
                "Processing research paper..."
            ):

                # Read PDF
                uploaded_file.seek(0)

                raw_text, page_count = (
                    extract_text_from_pdf(
                        uploaded_file
                    )
                )

                # Clean text
                cleaned = clean_text(
                    raw_text
                )

                # Create chunks
                chunks = split_text_into_chunks(
                    cleaned
                )

                # Load embedding model
                embedding_model = (
                    get_embedding_model()
                )

                # Generate embeddings
                embeddings = generate_embeddings(
                    chunks,
                    embedding_model
                )

                # Create FAISS index
                faiss_index = create_faiss_index(
                    embeddings
                )

                # Save to session
                st.session_state.paper_text = (
                    raw_text
                )

                st.session_state.cleaned_text = (
                    cleaned
                )

                st.session_state.chunks = (
                    chunks
                )

                st.session_state.embeddings = (
                    embeddings
                )

                st.session_state.faiss_index = (
                    faiss_index
                )

                st.session_state.page_count = (
                    page_count
                )

                st.session_state.paper_processed = (
                    True
                )

                st.success(
                    "Research paper processed successfully!"
                )


# ============================================================
# PAPER ANALYSIS PAGE
# ============================================================

if page == "📄 Paper Analysis":

    if not st.session_state.paper_processed:

        st.info(
            "Upload a PDF and click "
            "'Process Research Paper' to begin."
        )

    else:

        st.success(
            f"Paper ready: "
            f"{st.session_state.uploaded_file_name}"
        )

        # ----------------------------------------------------
        # PAPER METRICS
        # ----------------------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Pages",
                st.session_state.page_count
            )

        with col2:
            st.metric(
                "Characters",
                len(
                    st.session_state.paper_text
                )
            )

        with col3:
            st.metric(
                "Chunks",
                len(
                    st.session_state.chunks
                )
            )

        st.markdown("---")

        # ----------------------------------------------------
        # RAW TEXT
        # ----------------------------------------------------

        with st.expander(
            "📜 View Extracted Text"
        ):

            st.text_area(
                "Extracted Text",
                st.session_state.paper_text,
                height=300
            )

        # ----------------------------------------------------
        # CLEANED TEXT
        # ----------------------------------------------------

        with st.expander(
            "🧹 View Cleaned Text"
        ):

            st.text_area(
                "Cleaned Text",
                st.session_state.cleaned_text,
                height=300
            )

        # ----------------------------------------------------
        # CHUNKS
        # ----------------------------------------------------

        with st.expander(
            "🧩 View Text Chunks"
        ):

            st.write(
                f"Total chunks: "
                f"{len(st.session_state.chunks)}"
            )

            for i, chunk in enumerate(
                st.session_state.chunks
            ):

                st.markdown(
                    f"**Chunk {i + 1}**"
                )

                st.write(chunk)

                st.markdown("---")

        st.markdown("---")

        # ====================================================
        # RAG QUESTION ANSWERING
        # ====================================================

        st.header(
            "💬 Ask Questions About the Paper"
        )

        question = st.text_input(
            "Enter your research question:"
        )

        top_k = st.slider(
            "Number of retrieved chunks",
            min_value=3,
            max_value=10,
            value=5
        )

        if st.button(
            "🔎 Ask ResearchMate AI"
        ):

            if not question.strip():

                st.warning(
                    "Please enter a question."
                )

            else:

                with st.spinner(
                    "Searching the research paper..."
                ):

                    embedding_model = (
                        get_embedding_model()
                    )

                    query_embedding = (
                        embedding_model.encode(
                            [question]
                        )
                    )

                    retrieved_chunks = hybrid_search(
                        question,
                        query_embedding,
                        st.session_state.chunks,
                        st.session_state.faiss_index,
                        top_k=top_k
                    )

                with st.spinner(
                    "Generating grounded answer..."
                ):

                    gemini_client = (
                        get_gemini_model()
                    )

                    prompt = build_rag_prompt(
                        question,
                        retrieved_chunks
                    )

                    answer = generate_answer(
                        gemini_client,
                        prompt
                    )

                st.markdown(
                    "### 🤖 Answer"
                )

                st.write(answer)

                st.caption(
                    "Answer generated using retrieved "
                    "content from the uploaded research paper."
                )

        st.markdown("---")

        # ====================================================
        # STRUCTURED PAPER ANALYSIS
        # ====================================================

        st.header(
            "📊 Structured Research Paper Analysis"
        )

        st.markdown(
            """
ResearchMate AI analyzes the retrieved paper
content and organizes the findings into
standard research categories.
"""
        )

        if st.button(
            "🧠 Analyze Research Paper"
        ):

            with st.spinner(
                "Retrieving relevant paper sections..."
            ):

                embedding_model = (
                    get_embedding_model()
                )

                analysis_query = """
                research problem objectives methodology
                dataset results findings contributions
                limitations
                """

                query_embedding = (
                    embedding_model.encode(
                        [analysis_query]
                    )
                )

                retrieved_chunks = hybrid_search(
                    analysis_query,
                    query_embedding,
                    st.session_state.chunks,
                    st.session_state.faiss_index,
                    top_k=7
                )

            with st.spinner(
                "Generating structured analysis..."
            ):

                gemini_client = (
                    get_gemini_model()
                )

                prompt = (
                    build_paper_analysis_prompt(
                        retrieved_chunks
                    )
                )

                analysis = generate_answer(
                    gemini_client,
                    prompt
                )

            st.markdown(analysis)

            st.info(
                """
The structured analysis is generated only
from retrieved content from the uploaded paper.
"""
            )


# ============================================================
# CITATION ANALYSIS - DAY 9
# ============================================================

if page == "🔎 Citation Analysis":

    if not st.session_state.paper_processed:

        st.info(
            "Upload a PDF and click "
            "'Process Research Paper' to begin."
        )

    else:

        st.success(
            f"Paper ready: "
            f"{st.session_state.uploaded_file_name}"
        )

        st.header(
            "🔎 Citation Analysis"
        )

        st.markdown(
            """
ResearchMate AI extracts and reconstructs the
reference section of the uploaded research paper.

The citation analyzer handles:

- Two-column academic PDFs
- Multi-line references
- Author-year references
- PDF line-break artifacts
"""
        )

        st.markdown("---")

        # ----------------------------------------------------
        # ANALYZE CITATIONS
        # ----------------------------------------------------

        if st.button(
            "🔎 Analyze Citations",
            type="primary"
        ):

            with st.spinner(
                "Analyzing references..."
            ):

                uploaded_file.seek(0)

                pdf_bytes = uploaded_file.read()

                temp_pdf_path = None

                try:

                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=".pdf"
                    ) as temp_file:

                        temp_file.write(
                            pdf_bytes
                        )

                        temp_pdf_path = (
                            temp_file.name
                        )

                    citation_result = (
                        analyze_pdf_citations(
                            temp_pdf_path
                        )
                    )

                    st.session_state.citation_result = (
                        citation_result
                    )

                finally:

                    if (
                        temp_pdf_path
                        and os.path.exists(
                            temp_pdf_path
                        )
                    ):

                        os.remove(
                            temp_pdf_path
                        )

            st.success(
                "Citation analysis completed!"
            )

        # ----------------------------------------------------
        # DISPLAY CITATION RESULTS
        # ----------------------------------------------------

        if st.session_state.citation_result:

            result = (
                st.session_state.citation_result
            )

            total_references = result.get(
                "total_references",
                0
            )

            reference_blocks = result.get(
                "reference_blocks",
                0
            )

            page_count = result.get(
                "page_count",
                st.session_state.page_count
            )

            references = result.get(
                "references",
                result.get(
                    "parsed_references",
                    []
                )
            )

            st.markdown("---")

            st.subheader(
                "📊 Citation Statistics"
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "PDF Pages",
                    page_count
                )

            with col2:

                st.metric(
                    "Reference Blocks",
                    reference_blocks
                )

            with col3:

                st.metric(
                    "Total References",
                    total_references
                )

            st.markdown("---")

            st.subheader(
                "📚 Extracted References"
            )

            if references:

                for i, reference in enumerate(
                    references,
                    start=1
                ):

                    st.markdown(
                        f"**{i}.** {reference}"
                    )

            else:

                st.warning(
                    "No references were detected "
                    "in the uploaded paper."
                )

            st.markdown("---")

            st.info(
                """
Citation analysis currently focuses on
extracting and reconstructing the reference
section.

Future versions can extend this module with
citation-year analysis, citation frequency,
and additional bibliographic insights.
"""
            )


# ============================================================
# NOVELTY ANALYSIS
# ============================================================

if page == "✨ Novelty Analysis":

    st.header(
        "✨ Novelty Analysis"
    )

    st.info(
        """
Novelty Analysis will evaluate potentially
novel aspects of the research paper using
retrieved literature context.
"""
    )

    st.markdown(
        """
### Planned Workflow

Research Paper
↓
Relevant Literature Retrieval
↓
Similarity Comparison
↓
Novelty Indicators
↓
AI-Assisted Novelty Analysis

This module will be developed in a later stage.
"""
    )

    st.warning(
        """
AI-generated novelty assessment should not be
treated as definitive evidence of originality.
"""
    )


# ============================================================
# POTENTIAL RESEARCH DIRECTIONS
# ============================================================

if page == "🧭 Potential Research Directions":

    st.header(
        "🧭 Potential Research Directions"
    )

    st.info(
        """
This module will suggest potentially
underexplored research areas based on the
uploaded paper and retrieved literature.
"""
    )

    st.markdown(
        """
### Planned Workflow

Research Paper
↓
Literature Retrieval
↓
Comparison of Existing Approaches
↓
Identify Potentially Underexplored Areas
↓
Potential Research Direction Suggestions
"""
    )

    st.warning(
        """
AI-generated suggestions are not definitive
research gaps. Researchers should validate
these potential research directions using
domain knowledge and further literature review.
"""
    )


# ============================================================
# RESEARCH SCORE
# ============================================================

if page == "📊 Research Score":

    st.header(
        "📊 Research Score"
    )

    st.info(
        """
The Research Score module will provide
structured indicators for evaluating different
dimensions of a research paper.
"""
    )

    st.markdown(
        """
### Planned Evaluation Dimensions

- Methodology
- Dataset / Data
- Results
- Contributions
- Limitations
- Literature Context
- Potential Research Directions

This module will be implemented in a later stage.
"""
    )

    st.warning(
        """
AI-generated scores should be treated as
supporting indicators rather than definitive
academic evaluations.
"""
    )