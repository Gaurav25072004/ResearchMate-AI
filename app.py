import os
import tempfile
import streamlit as st

from rag.pdf_loader import extract_text_from_pdf
from rag.text_processor import clean_text, split_text_into_chunks
from rag.embedding import load_embedding_model, generate_embeddings
from rag.vector_store import create_faiss_index, hybrid_search
from rag.llm import (
    load_gemini_model,
    generate_answer,
    build_rag_prompt,
    build_paper_analysis_prompt,
)
from rag.citation_analyzer import analyze_pdf_citations
from rag.literature_store import (
    build_literature_corpus,
    search_literature,
)
from agents.novelty_agent import build_novelty_analysis_prompt


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ResearchMate AI",
    page_icon="📚",
    layout="wide"
)


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

if "cleaned_text" not in st.session_state:
    st.session_state.cleaned_text = ""

if "chunks" not in st.session_state:
    st.session_state.chunks = []

if "embedding_model" not in st.session_state:
    st.session_state.embedding_model = None

if "embeddings" not in st.session_state:
    st.session_state.embeddings = None

if "faiss_index" not in st.session_state:
    st.session_state.faiss_index = None

if "gemini_client" not in st.session_state:
    st.session_state.gemini_client = None

if "paper_analysis" not in st.session_state:
    st.session_state.paper_analysis = None

if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None

if "page_count" not in st.session_state:
    st.session_state.page_count = 0

# New Day 10 literature corpus state
if "literature_corpus" not in st.session_state:
    st.session_state.literature_corpus = None

if "literature_corpus_path" not in st.session_state:
    st.session_state.literature_corpus_path = None


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("📚 ResearchMate AI")

st.sidebar.markdown(
    """
### AI-Powered Research Assistant

Analyze research papers, retrieve relevant content,
inspect citations, compare literature, and explore
potential research directions.
"""
)

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    [
        "🏠 Home",
        "📄 Paper Analysis",
        "🔎 Citation Analysis",
        "✨ Novelty Analysis",
        "🧭 Potential Research Directions",
        "📊 Research Score",
    ]
)

st.sidebar.markdown("---")

st.sidebar.info(
    """
**Important**

ResearchMate AI provides AI-generated analysis
to support researchers.

Results should be validated using broader
literature review and domain expertise.
"""
)


# ============================================================
# HOME
# ============================================================

if page == "🏠 Home":

    st.title("📚 ResearchMate AI")

    st.subheader(
        "AI-Powered Research Paper Analysis Assistant"
    )

    st.markdown(
        """
ResearchMate AI helps researchers and students
understand and analyze academic literature using
Retrieval-Augmented Generation (RAG), semantic
retrieval, citation analysis, and cross-paper
comparison.
"""
    )

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            ### 📄 Paper Analysis

            Extract and analyze:

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
            uploaded research papers.

            Identify:

            - Number of references
            - Reference entries
            - Reference structure
            - Citation information
            """
        )

    with col3:
        st.markdown(
            """
            ### ✨ Novelty Analysis

            Compare the uploaded paper with
            a separate literature corpus.

            Analyze:

            - Similarity evidence
            - Differences
            - Potentially distinctive aspects
            """
        )

    st.markdown("---")

    st.info(
        """
        🧭 **Potential Research Directions**

        ResearchMate AI can later provide AI-generated
        suggestions for potentially underexplored areas
        based on analyzed literature.

        These suggestions are not definitive research gaps
        and should be validated by the researcher.
        """
    )


# ============================================================
# UPLOAD SECTION
# ============================================================

if page in [
    "📄 Paper Analysis",
    "🔎 Citation Analysis",
    "✨ Novelty Analysis"
]:

    st.header("📤 Upload Research Paper")

    uploaded_file = st.file_uploader(
        "Upload a research paper in PDF format",
        type=["pdf"]
    )

    if uploaded_file is not None:

        # ----------------------------------------------------
        # Detect new uploaded paper
        # ----------------------------------------------------

        new_file = (
            st.session_state.uploaded_file_name
            != uploaded_file.name
        )

        if new_file:

            st.session_state.pdf_text = ""
            st.session_state.cleaned_text = ""
            st.session_state.chunks = []
            st.session_state.embeddings = None
            st.session_state.faiss_index = None
            st.session_state.paper_analysis = None
            st.session_state.page_count = 0
            st.session_state.uploaded_file_name = uploaded_file.name

        st.success(
            f"Uploaded: **{uploaded_file.name}**"
        )

        # ----------------------------------------------------
        # Process uploaded paper
        # ----------------------------------------------------

        if not st.session_state.chunks:

            if st.button(
                "⚙️ Process Research Paper",
                key="process_paper"
            ):

                with st.spinner(
                    "Extracting and processing research paper..."
                ):

                    try:

                        pdf_bytes = uploaded_file.getvalue()

                        class UploadedPDF:
                            def __init__(self, data):
                                self.data = data

                            def read(self):
                                return self.data

                        pdf_object = UploadedPDF(pdf_bytes)

                        # Extract PDF text
                        text, page_count = extract_text_from_pdf(
                            pdf_object
                        )

                        st.session_state.pdf_text = text
                        st.session_state.page_count = page_count

                        # Clean text
                        cleaned_text = clean_text(text)

                        st.session_state.cleaned_text = cleaned_text

                        # Create chunks
                        chunks = split_text_into_chunks(
                            cleaned_text
                        )

                        st.session_state.chunks = chunks

                        # Load embedding model
                        if (
                            st.session_state.embedding_model
                            is None
                        ):
                            st.session_state.embedding_model = (
                                load_embedding_model()
                            )

                        # Generate embeddings
                        embeddings = generate_embeddings(
                            chunks,
                            st.session_state.embedding_model
                        )

                        st.session_state.embeddings = embeddings

                        # Create FAISS index
                        faiss_index = create_faiss_index(
                            embeddings
                        )

                        st.session_state.faiss_index = faiss_index

                        st.success(
                            "Research paper processed successfully."
                        )

                        st.write(
                            f"**Pages:** {page_count}"
                        )

                        st.write(
                            f"**Chunks:** {len(chunks)}"
                        )

                        if faiss_index is not None:
                            st.write(
                                f"**FAISS vectors:** "
                                f"{faiss_index.ntotal}"
                            )

                    except Exception as e:

                        st.error(
                            f"Error while processing paper: {e}"
                        )

        else:

            st.success(
                "Research paper is already processed."
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Pages",
                    st.session_state.page_count
                )

            with col2:
                st.metric(
                    "Chunks",
                    len(st.session_state.chunks)
                )

            with col3:

                if st.session_state.faiss_index is not None:
                    st.metric(
                        "FAISS Vectors",
                        st.session_state.faiss_index.ntotal
                    )


# ============================================================
# PAPER ANALYSIS
# ============================================================

if page == "📄 Paper Analysis":

    st.title("📄 Research Paper Analysis")

    if not st.session_state.chunks:

        st.warning(
            "Please upload and process a research paper first."
        )

    else:

        st.subheader("💬 Ask Questions About the Paper")

        question = st.text_input(
            "Enter your research question",
            placeholder="Example: What methodology was used in the study?"
        )

        if st.button(
            "🔍 Ask Question",
            key="ask_question"
        ):

            if not question.strip():

                st.warning(
                    "Please enter a question."
                )

            else:

                with st.spinner(
                    "Searching the research paper..."
                ):

                    try:

                        # Load Gemini
                        if (
                            st.session_state.gemini_client
                            is None
                        ):
                            st.session_state.gemini_client = (
                                load_gemini_model()
                            )

                        # Query embedding
                        query_embedding = (
                            st.session_state.embedding_model
                            .encode([question])[0]
                        )

                        # Hybrid retrieval
                        retrieved_results = hybrid_search(
                            st.session_state.faiss_index,
                            query_embedding,
                            question,
                            st.session_state.chunks,
                            top_k=5
                        )

                        retrieved_chunks = [
                            result["chunk"]
                            for result in retrieved_results
                        ]

                        # Build prompt
                        prompt = build_rag_prompt(
                            question,
                            retrieved_chunks
                        )

                        # Gemini answer
                        answer = generate_answer(
                            st.session_state.gemini_client,
                            prompt
                        )

                        st.markdown("### 🤖 Answer")

                        st.write(answer)

                        # ------------------------------------------------
                        # Retrieval evidence
                        # ------------------------------------------------

                        with st.expander(
                            "🔎 View Retrieved Evidence"
                        ):

                            for i, result in enumerate(
                                retrieved_results,
                                start=1
                            ):

                                st.markdown(
                                    f"### Result {i}"
                                )

                                st.write(
                                    f"Semantic Score: "
                                    f"{result['semantic_score']:.4f}"
                                )

                                st.write(
                                    f"Keyword Score: "
                                    f"{result['keyword_score']:.4f}"
                                )

                                st.write(
                                    f"Section Score: "
                                    f"{result['section_score']:.4f}"
                                )

                                st.write(
                                    f"Final Score: "
                                    f"{result['final_score']:.4f}"
                                )

                                st.text(
                                    result["chunk"]
                                )

                                st.markdown("---")

                    except Exception as e:

                        st.error(
                            f"Error while answering question: {e}"
                        )

        st.markdown("---")

        st.subheader(
            "📊 Structured Research Paper Analysis"
        )

        if st.button(
            "🧠 Analyze Entire Paper",
            key="analyze_paper"
        ):

            with st.spinner(
                "Analyzing research paper..."
            ):

                try:

                    if (
                        st.session_state.gemini_client
                        is None
                    ):
                        st.session_state.gemini_client = (
                            load_gemini_model()
                        )

                    # Retrieve broad paper context
                    analysis_query = (
                        "research problem objectives methodology "
                        "dataset results findings contributions limitations"
                    )

                    query_embedding = (
                        st.session_state.embedding_model
                        .encode([analysis_query])[0]
                    )

                    retrieved_results = hybrid_search(
                        st.session_state.faiss_index,
                        query_embedding,
                        analysis_query,
                        st.session_state.chunks,
                        top_k=10
                    )

                    retrieved_chunks = [
                        result["chunk"]
                        for result in retrieved_results
                    ]

                    prompt = build_paper_analysis_prompt(
                        retrieved_chunks
                    )

                    analysis = generate_answer(
                        st.session_state.gemini_client,
                        prompt
                    )

                    st.session_state.paper_analysis = analysis

                except Exception as e:

                    st.error(
                        f"Error during paper analysis: {e}"
                    )

        if st.session_state.paper_analysis:

            st.markdown(
                st.session_state.paper_analysis
            )


# ============================================================
# CITATION ANALYSIS
# ============================================================

if page == "🔎 Citation Analysis":

    st.title("🔎 Citation Analysis")

    if uploaded_file is None:

        st.warning(
            "Please upload a research paper first."
        )

    else:

        if st.button(
            "🔎 Analyze Citations",
            key="analyze_citations"
        ):

            with st.spinner(
                "Analyzing citations and references..."
            ):

                try:

                    pdf_bytes = uploaded_file.getvalue()

                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=".pdf"
                    ) as temp_pdf:

                        temp_pdf.write(pdf_bytes)

                        temp_pdf_path = temp_pdf.name

                    try:

                        citation_result = (
                            analyze_pdf_citations(
                                temp_pdf_path
                            )
                        )

                    finally:

                        if os.path.exists(
                            temp_pdf_path
                        ):
                            os.remove(
                                temp_pdf_path
                            )

                    st.success(
                        "Citation analysis completed."
                    )

                    # ------------------------------------------------
                    # Summary
                    # ------------------------------------------------

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Pages",
                            citation_result[
                                "page_count"
                            ]
                        )

                    with col2:
                        st.metric(
                            "Reference Blocks",
                            citation_result[
                                "reference_blocks"
                            ]
                        )

                    with col3:
                        st.metric(
                            "Parsed References",
                            citation_result[
                                "total_references"
                            ]
                        )

                    st.markdown("---")

                    st.subheader(
                        "📚 Extracted References"
                    )

                    references = citation_result.get(
                        "references",
                        []
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

                        st.info(
                            "No references were successfully parsed."
                        )

                except Exception as e:

                    st.error(
                        f"Error during citation analysis: {e}"
                    )


# ============================================================
# NOVELTY ANALYSIS
# ============================================================

if page == "✨ Novelty Analysis":

    st.title("✨ Cross-Paper Novelty Analysis")

    st.markdown(
        """
This module compares the uploaded research paper
with **separate research papers stored in the
literature corpus**.

The analysis focuses on:

- Similarity Evidence
- Differences
- Potentially Distinctive Aspects

It does **not** claim to definitively prove novelty
or identify a research gap.
"""
    )

    st.info(
        """
        🧭 **Important**

        The generated observations are based only on
        the uploaded paper and the retrieved literature.

        They should be validated through broader
        literature review and domain expertise.
        """
    )

    # --------------------------------------------------------
    # Check uploaded paper
    # --------------------------------------------------------

    if not st.session_state.chunks:

        st.warning(
            "Please upload and process a research paper first."
        )

    else:

        # ----------------------------------------------------
        # Literature corpus path
        # ----------------------------------------------------

        literature_directory = os.path.join(
            "documents",
            "literature"
        )

        st.markdown("---")

        st.subheader(
            "📚 Separate Literature Corpus"
        )

        st.write(
            f"Literature directory: "
            f"`{literature_directory}`"
        )

        # ----------------------------------------------------
        # Build / load literature corpus
        # ----------------------------------------------------

        if st.button(
            "🔄 Build Literature Corpus",
            key="build_literature_corpus"
        ):

            with st.spinner(
                "Loading literature papers and building literature index..."
            ):

                try:

                    if (
                        st.session_state.embedding_model
                        is None
                    ):
                        st.session_state.embedding_model = (
                            load_embedding_model()
                        )

                    literature_corpus = (
                        build_literature_corpus(
                            literature_directory,
                            st.session_state.embedding_model
                        )
                    )

                    st.session_state.literature_corpus = (
                        literature_corpus
                    )

                    st.session_state.literature_corpus_path = (
                        literature_directory
                    )

                    literature_papers = (
                        literature_corpus.get(
                            "papers",
                            []
                        )
                    )

                    literature_chunks = (
                        literature_corpus.get(
                            "chunks",
                            []
                        )
                    )

                    st.success(
                        "Literature corpus built successfully."
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Literature Papers",
                            len(literature_papers)
                        )

                    with col2:
                        st.metric(
                            "Literature Chunks",
                            len(literature_chunks)
                        )

                    with col3:

                        literature_index = (
                            literature_corpus.get(
                                "index"
                            )
                        )

                        if literature_index is not None:

                            st.metric(
                                "FAISS Vectors",
                                literature_index.ntotal
                            )

                except Exception as e:

                    st.error(
                        f"Error building literature corpus: {e}"
                    )

        # ----------------------------------------------------
        # Display current corpus status
        # ----------------------------------------------------

        if st.session_state.literature_corpus:

            literature_corpus = (
                st.session_state.literature_corpus
            )

            literature_papers = (
                literature_corpus.get(
                    "papers",
                    []
                )
            )

            literature_chunks = (
                literature_corpus.get(
                    "chunks",
                    []
                )
            )

            literature_index = (
                literature_corpus.get(
                    "index"
                )
            )

            st.success(
                "Separate literature corpus is ready."
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Literature Papers",
                    len(literature_papers)
                )

            with col2:

                st.metric(
                    "Literature Chunks",
                    len(literature_chunks)
                )

            with col3:

                if literature_index is not None:

                    st.metric(
                        "FAISS Vectors",
                        literature_index.ntotal
                    )

            # ------------------------------------------------
            # Literature papers list
            # ------------------------------------------------

            with st.expander(
                "📚 View Literature Corpus"
            ):

                for paper in literature_papers:

                    st.markdown(
                        f"**{paper['source']}**"
                    )

                    st.write(
                        f"Pages: {paper['page_count']}"
                    )

                    st.markdown("---")

            st.markdown("---")

            # ------------------------------------------------
            # Generate novelty analysis
            # ------------------------------------------------

            st.subheader(
                "✨ Generate Cross-Paper Analysis"
            )

            if st.button(
                "✨ Analyze Potential Novelty",
                key="analyze_novelty"
            ):

                with st.spinner(
                    "Comparing uploaded paper with separate literature..."
                ):

                    try:

                        # --------------------------------------------
                        # Load Gemini
                        # --------------------------------------------

                        if (
                            st.session_state.gemini_client
                            is None
                        ):
                            st.session_state.gemini_client = (
                                load_gemini_model()
                            )

                        # --------------------------------------------
                        # Generate paper analysis if missing
                        # --------------------------------------------

                        if (
                            not st.session_state.paper_analysis
                        ):

                            analysis_query = (
                                "research problem objectives methodology "
                                "dataset results findings contributions limitations"
                            )

                            query_embedding = (
                                st.session_state.embedding_model
                                .encode(
                                    [analysis_query]
                                )[0]
                            )

                            paper_results = hybrid_search(
                                st.session_state.faiss_index,
                                query_embedding,
                                analysis_query,
                                st.session_state.chunks,
                                top_k=10
                            )

                            paper_chunks = [
                                result["chunk"]
                                for result in paper_results
                            ]

                            paper_prompt = (
                                build_paper_analysis_prompt(
                                    paper_chunks
                                )
                            )

                            paper_analysis = (
                                generate_answer(
                                    st.session_state.gemini_client,
                                    paper_prompt
                                )
                            )

                            st.session_state.paper_analysis = (
                                paper_analysis
                            )

                        else:

                            paper_analysis = (
                                st.session_state.paper_analysis
                            )

                        # --------------------------------------------
                        # Create literature retrieval query
                        # --------------------------------------------

                        literature_query = (
                            """
                            research problem methodology
                            approach dataset results contribution
                            research focus
                            """
                        )

                        # --------------------------------------------
                        # Search separate literature corpus
                        # --------------------------------------------

                        literature_results = search_literature(
                            literature_corpus,
                            literature_query,
                            st.session_state.embedding_model,
                            top_k=7
                        )

                        if not literature_results:

                            st.warning(
                                """
                                No relevant literature was retrieved
                                from the separate literature corpus.
                                """
                            )

                        else:

                            # ----------------------------------------
                            # Build novelty prompt
                            # ----------------------------------------

                            novelty_prompt = (
                                build_novelty_analysis_prompt(
                                    paper_analysis,
                                    literature_results
                                )
                            )

                            # ----------------------------------------
                            # Generate novelty analysis
                            # ----------------------------------------

                            novelty_analysis = (
                                generate_answer(
                                    st.session_state.gemini_client,
                                    novelty_prompt
                                )
                            )

                            st.success(
                                "Cross-paper novelty analysis completed."
                            )

                            st.markdown("---")

                            st.subheader(
                                "🧠 Analysis"
                            )

                            st.markdown(
                                novelty_analysis
                            )

                            st.markdown("---")

                            # ----------------------------------------
                            # Retrieved literature evidence
                            # ----------------------------------------

                            st.subheader(
                                "📚 Retrieved Literature Evidence"
                            )

                            st.caption(
                                """
                                These are the literature chunks used
                                to generate the comparison.
                                """
                            )

                            for i, result in enumerate(
                                literature_results,
                                start=1
                            ):

                                with st.expander(
                                    f"{i}. {result['source']}"
                                ):

                                    st.write(
                                        f"**Source:** "
                                        f"{result['source']}"
                                    )

                                    st.write(
                                        f"**Pages:** "
                                        f"{result['page_count']}"
                                    )

                                    st.write(
                                        f"**Semantic Score:** "
                                        f"{result['semantic_score']:.4f}"
                                    )

                                    st.write(
                                        f"**Keyword Score:** "
                                        f"{result['keyword_score']:.4f}"
                                    )

                                    st.write(
                                        f"**Section Score:** "
                                        f"{result['section_score']:.4f}"
                                    )

                                    st.write(
                                        f"**Final Score:** "
                                        f"{result['final_score']:.4f}"
                                    )

                                    st.markdown(
                                        "**Retrieved Content:**"
                                    )

                                    st.text(
                                        result["chunk"]
                                    )

                    except Exception as e:

                        st.error(
                            f"Error during novelty analysis: {e}"
                        )

        else:

            st.warning(
                """
                Literature corpus is not loaded yet.

                Click **Build Literature Corpus** above
                before running cross-paper novelty analysis.
                """
            )


# ============================================================
# POTENTIAL RESEARCH DIRECTIONS
# ============================================================

if page == "🧭 Potential Research Directions":

    st.title(
        "🧭 Potential Research Directions"
    )

    st.markdown(
        """
This module is intended to suggest **potential research
directions** based on analyzed literature.

ResearchMate AI does not claim to definitively identify
or prove a research gap.
"""
    )

    st.info(
        """
        🚧 This module is currently under development.

        Future versions will analyze the uploaded paper
        together with retrieved literature and generate
        AI-assisted research opportunity suggestions.

        All suggestions will require validation through
        broader literature review and domain expertise.
        """
    )


# ============================================================
# RESEARCH SCORE
# ============================================================

if page == "📊 Research Score":

    st.title(
        "📊 Research Score"
    )

    st.info(
        """
        🚧 Research Score is currently under development.

        Future versions may provide structured indicators
        related to research-paper characteristics.

        Any such score should be treated as an AI-assisted
        indicator rather than an objective measurement of
        research quality or originality.
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "ResearchMate AI • AI-assisted academic research analysis"
)