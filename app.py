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
from agents.research_direction_agent import (
    build_research_direction_prompt
)
from agents.research_assessment_agent import (
    build_research_assessment_prompt
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

# Day 10 literature corpus state
if "literature_corpus" not in st.session_state:
    st.session_state.literature_corpus = None

if "literature_corpus_path" not in st.session_state:
    st.session_state.literature_corpus_path = None

# Day 11 research comparison state
if "literature_results" not in st.session_state:
    st.session_state.literature_results = []

if "novelty_analysis" not in st.session_state:
    st.session_state.novelty_analysis = None

if "research_directions" not in st.session_state:
    st.session_state.research_directions = None

# Day 12 research assessment state
if "citation_analysis" not in st.session_state:
    st.session_state.citation_analysis = None

if "research_assessment" not in st.session_state:
    st.session_state.research_assessment = None


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
        "📊 Research Assessment",
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
retrieval, citation analysis, cross-paper
comparison, and potential research direction
suggestions.
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

        ResearchMate AI can suggest potential research
        directions based on the analyzed paper and
        retrieved literature.

        These are AI-generated suggestions and are not
        definitive research gaps. They should be validated
        through broader literature review and domain expertise.
        """
    )


# ============================================================
# UPLOAD SECTION
# ============================================================

if page in [
    "📄 Paper Analysis",
    "🔎 Citation Analysis",
    "✨ Novelty Analysis",
    "🧭 Potential Research Directions",
    "📊 Research Assessment"
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

            # Reset Day 10 / Day 11 analysis state
            st.session_state.literature_results = []
            st.session_state.novelty_analysis = None
            st.session_state.research_directions = None

            # Reset Day 12 analysis state
            st.session_state.citation_analysis = None
            st.session_state.research_assessment = None

            st.session_state.uploaded_file_name = (
                uploaded_file.name
            )

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

                        pdf_object = UploadedPDF(
                            pdf_bytes
                        )

                        # Extract PDF text
                        text, page_count = (
                            extract_text_from_pdf(
                                pdf_object
                            )
                        )

                        st.session_state.pdf_text = text
                        st.session_state.page_count = (
                            page_count
                        )

                        # Clean text
                        cleaned_text = clean_text(
                            text
                        )

                        st.session_state.cleaned_text = (
                            cleaned_text
                        )

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

                        st.session_state.embeddings = (
                            embeddings
                        )

                        # Create FAISS index
                        faiss_index = create_faiss_index(
                            embeddings
                        )

                        st.session_state.faiss_index = (
                            faiss_index
                        )

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

                if (
                    st.session_state.faiss_index
                    is not None
                ):

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

        st.subheader(
            "💬 Ask Questions About the Paper"
        )

        question = st.text_input(
            "Enter your research question",
            placeholder=(
                "Example: What methodology was used in the study?"
            )
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
                            .encode(
                                [question]
                            )[0]
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

                        st.markdown(
                            "### 🤖 Answer"
                        )

                        st.write(answer)

                        # Retrieval evidence
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

                    prompt = (
                        build_paper_analysis_prompt(
                            retrieved_chunks
                        )
                    )

                    analysis = generate_answer(
                        st.session_state.gemini_client,
                        prompt
                    )

                    st.session_state.paper_analysis = (
                        analysis
                    )

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

                        temp_pdf.write(
                            pdf_bytes
                        )

                        temp_pdf_path = (
                            temp_pdf.name
                        )

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

                    # Save citation analysis for
                    # Research Assessment
                    st.session_state.citation_analysis = (
                        citation_result
                    )

                    # A new citation analysis means
                    # previous research assessment should
                    # be regenerated.
                    st.session_state.research_assessment = (
                        None
                    )

                    st.success(
                        "Citation analysis completed."
                    )

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

    # Display previously generated citation analysis
    # after navigating back to this page.
    if st.session_state.citation_analysis:

        citation_result = (
            st.session_state.citation_analysis
        )

        if uploaded_file is not None:

            st.markdown("---")

            st.subheader(
                "📚 Current Citation Analysis"
            )

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


# ============================================================
# NOVELTY ANALYSIS
# ============================================================

if page == "✨ Novelty Analysis":

    st.title(
        "✨ Cross-Paper Novelty Analysis"
    )

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
        # Build literature corpus
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

                    # Reset dependent analyses
                    st.session_state.literature_results = []
                    st.session_state.novelty_analysis = None
                    st.session_state.research_directions = None

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
        # Display corpus
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

                        if (
                            st.session_state.gemini_client
                            is None
                        ):

                            st.session_state.gemini_client = (
                                load_gemini_model()
                            )

                        # ----------------------------------------
                        # Generate paper analysis if missing
                        # ----------------------------------------

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

                        # ----------------------------------------
                        # Retrieve literature
                        # ----------------------------------------

                        literature_query = (
                            """
                            research problem methodology
                            approach dataset results contribution
                            research focus
                            """
                        )

                        literature_results = (
                            search_literature(
                                literature_corpus,
                                literature_query,
                                st.session_state.embedding_model,
                                top_k=7
                            )
                        )

                        if not literature_results:

                            st.warning(
                                """
                                No relevant literature was retrieved
                                from the separate literature corpus.
                                """
                            )

                        else:

                            # Save literature results
                            st.session_state.literature_results = (
                                literature_results
                            )

                            # ------------------------------------
                            # Build novelty prompt
                            # ------------------------------------

                            novelty_prompt = (
                                build_novelty_analysis_prompt(
                                    paper_analysis,
                                    literature_results
                                )
                            )

                            # ------------------------------------
                            # Generate novelty analysis
                            # ------------------------------------

                            novelty_analysis = (
                                generate_answer(
                                    st.session_state.gemini_client,
                                    novelty_prompt
                                )
                            )

                            st.session_state.novelty_analysis = (
                                novelty_analysis
                            )

                            # A new novelty analysis means
                            # previous research directions
                            # should be regenerated.
                            st.session_state.research_directions = (
                                None
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

                            # ------------------------------------
                            # Retrieved literature evidence
                            # ------------------------------------

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
This module suggests **potential research directions**
based on the uploaded paper and retrieved literature.

ResearchMate AI does not claim to definitively identify
or prove a research gap.

The suggestions are AI-generated observations that
should be validated through broader literature review
and domain expertise.
"""
    )

    st.info(
        """
        **Researcher Validation**

        Potential research directions are generated from
        the supplied paper analysis, cross-paper comparison,
        and retrieved literature. They should not be treated
        as established research opportunities without further
        validation.
        """
    )

    # --------------------------------------------------------
    # Check uploaded paper
    # --------------------------------------------------------

    if not st.session_state.chunks:

        st.warning(
            "Please upload and process a research paper first."
        )

    elif not st.session_state.literature_corpus:

        st.warning(
            """
            The separate literature corpus is not loaded.

            Go to **✨ Novelty Analysis** and click
            **🔄 Build Literature Corpus** first.
            """
        )

    elif not st.session_state.novelty_analysis:

        st.warning(
            """
            Cross-paper novelty analysis has not been generated yet.

            Go to **✨ Novelty Analysis** and click
            **✨ Analyze Potential Novelty** first.
            """
        )

    elif not st.session_state.literature_results:

        st.warning(
            """
            Literature evidence is not available.

            Please run the cross-paper novelty analysis
            first so ResearchMate AI can use the retrieved
            literature.
            """
        )

    else:

        st.success(
            "Required paper analysis and literature evidence are ready."
        )

        st.markdown("---")

        st.subheader(
            "🧭 Generate Potential Research Directions"
        )

        st.write(
            """
            ResearchMate AI will use the existing paper analysis,
            novelty analysis, and retrieved literature evidence
            to suggest research directions.
            """
        )

        if st.button(
            "🧭 Generate Research Directions",
            key="generate_research_directions"
        ):

            with st.spinner(
                "Generating potential research directions..."
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
                    # Build grounded research direction prompt
                    # --------------------------------------------

                    research_direction_prompt = (
                        build_research_direction_prompt(
                            st.session_state.paper_analysis,
                            st.session_state.novelty_analysis,
                            st.session_state.literature_results
                        )
                    )

                    # --------------------------------------------
                    # Generate directions
                    # --------------------------------------------

                    research_directions = (
                        generate_answer(
                            st.session_state.gemini_client,
                            research_direction_prompt
                        )
                    )

                    st.session_state.research_directions = (
                        research_directions
                    )

                    st.success(
                        "Potential research directions generated successfully."
                    )

                except Exception as e:

                    st.error(
                        f"Error generating research directions: {e}"
                    )

        # --------------------------------------------------------
        # Display generated directions
        # --------------------------------------------------------

        if st.session_state.research_directions:

            st.markdown("---")

            st.subheader(
                "🧭 Suggested Potential Research Directions"
            )

            st.markdown(
                st.session_state.research_directions
            )

            st.markdown("---")

            st.warning(
                """
                **Researcher Validation Required**

                These are AI-generated potential research
                directions based on the supplied paper analysis
                and retrieved literature.

                They should be validated through broader
                literature review, domain expertise, and further
                research before being treated as established
                research opportunities.
                """
            )

            # ----------------------------------------------------
            # Show evidence used by the agent
            # ----------------------------------------------------

            st.markdown("---")

            st.subheader(
                "📚 Literature Evidence Used"
            )

            st.caption(
                """
                These are the same retrieved literature results
                used during the cross-paper novelty analysis.
                """
            )

            for i, result in enumerate(
                st.session_state.literature_results,
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
                        f"**Final Score:** "
                        f"{result['final_score']:.4f}"
                    )

                    st.markdown(
                        "**Retrieved Content:**"
                    )

                    st.text(
                        result["chunk"]
                    )


# ============================================================
# RESEARCH ASSESSMENT — DAY 12
# ============================================================

if page == "📊 Research Assessment":

    st.title(
        "📊 Research Assessment"
    )

    st.markdown(
        """
This module provides a structured assessment of
how clearly and completely different aspects of
the research paper are reported.

The assessment does **not** measure research quality,
scientific validity, originality, or publication
potential.
"""
    )

    st.info(
        """
        **Researcher Validation**

        This assessment is an AI-generated analysis of
        information reported in the supplied paper analysis
        and citation analysis.

        It should be interpreted as a structured aid for
        reviewing the paper rather than an objective measure
        of research quality, scientific validity, or originality.
        """
    )

    # --------------------------------------------------------
    # Check paper processing
    # --------------------------------------------------------

    if not st.session_state.chunks:

        st.warning(
            "Please upload and process a research paper first."
        )

    # --------------------------------------------------------
    # Check paper analysis
    # --------------------------------------------------------

    elif not st.session_state.paper_analysis:

        st.warning(
            """
            Paper analysis has not been generated yet.

            Go to **📄 Paper Analysis** and click
            **🧠 Analyze Entire Paper** first.
            """
        )

    # --------------------------------------------------------
    # Check citation analysis
    # --------------------------------------------------------

    elif not st.session_state.citation_analysis:

        st.warning(
            """
            Citation analysis has not been generated yet.

            Go to **🔎 Citation Analysis** and click
            **🔎 Analyze Citations** first.
            """
        )

    else:

        st.success(
            "Paper analysis and citation analysis are ready."
        )

        st.markdown("---")

        st.subheader(
            "📊 Generate Research Assessment"
        )

        st.write(
            """
            ResearchMate AI will assess the clarity and
            completeness of the information reported in
            the research paper.
            """
        )

        if st.button(
            "📊 Generate Research Assessment",
            key="generate_research_assessment"
        ):

            with st.spinner(
                "Generating structured research assessment..."
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
                    # Build assessment prompt
                    # --------------------------------------------

                    assessment_prompt = (
                        build_research_assessment_prompt(
                            st.session_state.paper_analysis,
                            st.session_state.citation_analysis
                        )
                    )

                    # --------------------------------------------
                    # Generate assessment
                    # --------------------------------------------

                    research_assessment = (
                        generate_answer(
                            st.session_state.gemini_client,
                            assessment_prompt
                        )
                    )

                    st.session_state.research_assessment = (
                        research_assessment
                    )

                    st.success(
                        "Research assessment generated successfully."
                    )

                except Exception as e:

                    st.error(
                        f"Error generating research assessment: {e}"
                    )

        # --------------------------------------------------------
        # Display assessment
        # --------------------------------------------------------

        if st.session_state.research_assessment:

            st.markdown("---")

            st.subheader(
                "📊 Research Assessment"
            )

            st.markdown(
                st.session_state.research_assessment
            )

            st.markdown("---")

            st.warning(
                """
                **Researcher Validation Required**

                This assessment is an AI-generated analysis
                of the information reported in the supplied
                paper analysis and citation analysis.

                It should be interpreted as a structured aid
                for reviewing the paper rather than an objective
                measure of research quality, scientific validity,
                or originality.
                """
            )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "ResearchMate AI • AI-assisted academic research analysis"
)