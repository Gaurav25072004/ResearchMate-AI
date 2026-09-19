import streamlit as st

from rag.pdf_loader import extract_text_from_pdf
from rag.text_processor import (
    clean_text,
    split_text_into_chunks
)
from rag.embedding import (
    load_embedding_model
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


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ResearchMate AI",
    page_icon="📚",
    layout="wide"
)


# ============================================================
# LOAD MODELS
# ============================================================

@st.cache_resource
def get_embedding_model():
    return load_embedding_model()


@st.cache_resource
def get_gemini_model():
    return load_gemini_model()


embedding_model = get_embedding_model()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("📚 ResearchMate AI")

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


# ============================================================
# HOME
# ============================================================

if page == "🏠 Home":

    st.title("📚 ResearchMate AI")

    st.subheader(
        "AI-Powered Research Assistant"
    )

    st.write(
        """
        ResearchMate AI helps researchers analyze
        research papers using Retrieval-Augmented
        Generation (RAG), semantic search, and
        Generative AI.
        """
    )

    st.markdown(
        """
        ### Current Capabilities

        - 📄 Upload research papers
        - 📝 Extract text from PDF
        - ✂️ Clean and chunk research content
        - 🧠 Generate semantic embeddings
        - 🔎 Search research content using FAISS
        - 🔀 Hybrid semantic + keyword + section retrieval
        - 🤖 Ask questions about the research paper
        - 📊 Generate structured research paper analysis
        """
    )

    st.info(
        """
        More research-analysis modules such as citation
        analysis, novelty analysis, potential research
        directions, and research scoring will be added
        progressively.
        """
    )


# ============================================================
# PAPER ANALYSIS
# ============================================================

elif page == "📄 Paper Analysis":

    st.title("📄 Research Paper Analysis")

    st.write(
        """
        Upload a research paper to extract, process,
        retrieve, and analyze its content.
        """
    )

    # --------------------------------------------------------
    # PDF UPLOAD
    # --------------------------------------------------------

    uploaded_file = st.file_uploader(
        "Upload a research paper (PDF)",
        type=["pdf"]
    )

    if uploaded_file is not None:

        # ----------------------------------------------------
        # PDF TEXT EXTRACTION
        # ----------------------------------------------------

        with st.spinner(
            "Extracting text from research paper..."
        ):

            text, page_count = (
                extract_text_from_pdf(
                    uploaded_file
                )
            )

        if not text.strip():

            st.error(
                "No readable text was found in the PDF."
            )

        else:

            # ------------------------------------------------
            # TEXT CLEANING
            # ------------------------------------------------

            cleaned_text = clean_text(text)

            # ------------------------------------------------
            # TEXT CHUNKING
            # ------------------------------------------------

            chunks = split_text_into_chunks(
                cleaned_text
            )

            # ------------------------------------------------
            # EMBEDDINGS
            # ------------------------------------------------

            with st.spinner(
                "Generating embeddings..."
            ):

                embeddings = (
                    embedding_model.encode(
                        chunks,
                        show_progress_bar=False
                    )
                )

            # ------------------------------------------------
            # FAISS INDEX
            # ------------------------------------------------

            faiss_index = create_faiss_index(
                embeddings
            )

            # ------------------------------------------------
            # PAPER INFORMATION
            # ------------------------------------------------

            st.success(
                "Research paper processed successfully."
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Pages",
                    page_count
                )

            with col2:
                st.metric(
                    "Characters",
                    len(cleaned_text)
                )

            with col3:
                st.metric(
                    "Chunks",
                    len(chunks)
                )

            # =================================================
            # RAW / CLEANED TEXT
            # =================================================

            with st.expander(
                "📄 View Extracted Text"
            ):

                st.text_area(
                    "Extracted Text",
                    text,
                    height=300
                )

            with st.expander(
                "🧹 View Cleaned Text"
            ):

                st.text_area(
                    "Cleaned Text",
                    cleaned_text,
                    height=300
                )

            with st.expander(
                "✂️ View Text Chunks"
            ):

                for i, chunk in enumerate(
                    chunks
                ):

                    st.markdown(
                        f"### Chunk {i + 1}"
                    )

                    st.write(chunk)

                    st.divider()

            # =================================================
            # ASK QUESTIONS
            # =================================================

            st.divider()

            st.subheader(
                "💬 Ask Questions About the Paper"
            )

            question = st.text_input(
                "Enter your research question:"
            )

            top_k = st.slider(
                "Number of retrieved sections",
                min_value=1,
                max_value=10,
                value=5
            )

            if st.button(
                "🔎 Search and Answer",
                type="primary"
            ):

                if not question.strip():

                    st.warning(
                        "Please enter a question."
                    )

                elif faiss_index is None:

                    st.error(
                        "FAISS index is not available."
                    )

                else:

                    with st.spinner(
                        "Retrieving relevant research sections..."
                    ):

                        query_embedding = (
                            embedding_model.encode(
                                [question]
                            )
                        )

                        retrieval_results = hybrid_search(
                            faiss_index,
                            query_embedding,
                            question,
                            chunks,
                            top_k=top_k
                        )

                    if retrieval_results:

                        # ------------------------------------
                        # DISPLAY RETRIEVED CONTENT
                        # ------------------------------------

                        st.subheader(
                            "🔎 Retrieved Research Sections"
                        )

                        retrieved_chunks = []

                        for i, result in enumerate(
                            retrieval_results
                        ):

                            retrieved_chunks.append(
                                result["chunk"]
                            )

                            with st.expander(
                                f"Result {i + 1}"
                            ):

                                st.write(
                                    result["chunk"]
                                )

                                col1, col2, col3, col4 = (
                                    st.columns(4)
                                )

                                with col1:
                                    st.metric(
                                        "Hybrid Score",
                                        f"{result['final_score']:.4f}"
                                    )

                                with col2:
                                    st.metric(
                                        "Semantic",
                                        f"{result['semantic_score']:.4f}"
                                    )

                                with col3:
                                    st.metric(
                                        "Keyword",
                                        f"{result['keyword_score']:.4f}"
                                    )

                                with col4:
                                    st.metric(
                                        "Section",
                                        f"{result['section_score']:.4f}"
                                    )

                        # ------------------------------------
                        # GEMINI RAG ANSWER
                        # ------------------------------------

                        with st.spinner(
                            "Generating answer using Gemini..."
                        ):

                            try:

                                gemini_model = (
                                    get_gemini_model()
                                )

                                prompt = (
                                    build_rag_prompt(
                                        question,
                                        retrieved_chunks
                                    )
                                )

                                answer = generate_answer(
                                    gemini_model,
                                    prompt
                                )

                                st.subheader(
                                    "🤖 ResearchMate AI Answer"
                                )

                                st.markdown(
                                    answer
                                )

                                st.caption(
                                    """
                                    ⚠️ This answer is generated
                                    using retrieved content from
                                    the uploaded research paper.
                                    Verify important information
                                    against the original paper.
                                    """
                                )

                            except Exception as e:

                                st.error(
                                    "An error occurred while "
                                    "generating the answer."
                                )

                                st.exception(e)

                    else:

                        st.warning(
                            "No relevant research content "
                            "was retrieved."
                        )

            # =================================================
            # STRUCTURED RESEARCH PAPER ANALYSIS
            # =================================================

            st.divider()

            st.subheader(
                "📊 Structured Research Paper Analysis"
            )

            st.write(
                """
                Generate a structured analysis of the
                research paper using retrieved research
                content.
                """
            )

            st.info(
                """
                The analysis is generated only from
                retrieved content of the uploaded paper.
                If information is not available in the
                retrieved content, ResearchMate AI will
                explicitly state that.
                """
            )

            if st.button(
                "📊 Analyze Research Paper",
                type="primary"
            ):

                if faiss_index is not None:

                    # ----------------------------------------
                    # ANALYSIS RETRIEVAL
                    # ----------------------------------------

                    with st.spinner(
                        "Retrieving relevant research sections..."
                    ):

                        analysis_query = """
                        Analyze the research paper and identify
                        its research problem, objectives,
                        methodology, dataset or data,
                        results or findings, main contributions,
                        and limitations.
                        """

                        analysis_query_embedding = (
                            embedding_model.encode(
                                [analysis_query]
                            )
                        )

                        analysis_results = hybrid_search(
                            faiss_index,
                            analysis_query_embedding,
                            analysis_query,
                            chunks,
                            top_k=7
                        )

                    analysis_chunks = [
                        result["chunk"]
                        for result in analysis_results
                    ]

                    if analysis_chunks:

                        # ------------------------------------
                        # GEMINI STRUCTURED ANALYSIS
                        # ------------------------------------

                        with st.spinner(
                            "Generating structured paper analysis..."
                        ):

                            try:

                                gemini_model = (
                                    get_gemini_model()
                                )

                                analysis_prompt = (
                                    build_paper_analysis_prompt(
                                        analysis_chunks
                                    )
                                )

                                analysis_answer = (
                                    generate_answer(
                                        gemini_model,
                                        analysis_prompt
                                    )
                                )

                                st.subheader(
                                    "📋 Research Paper Analysis"
                                )

                                st.markdown(
                                    analysis_answer
                                )

                                st.divider()

                                st.caption(
                                    """
                                    ⚠️ This analysis is generated
                                    from retrieved content in the
                                    uploaded research paper.
                                    Information should be verified
                                    against the original paper.
                                    """
                                )

                            except Exception as e:

                                st.error(
                                    "An error occurred while "
                                    "generating the structured "
                                    "paper analysis."
                                )

                                st.exception(e)

                    else:

                        st.warning(
                            "No relevant content was retrieved "
                            "for structured analysis."
                        )

                else:

                    st.warning(
                        "FAISS index is not available."
                    )


# ============================================================
# CITATION ANALYSIS
# ============================================================

elif page == "🔎 Citation Analysis":

    st.title("🔎 Citation Analysis")

    st.info(
        """
        Citation Analysis will be implemented in a
        future development stage.
        """
    )


# ============================================================
# NOVELTY ANALYSIS
# ============================================================

elif page == "✨ Novelty Analysis":

    st.title("✨ Novelty Analysis")

    st.info(
        """
        Novelty Analysis will be implemented in a
        future development stage.
        """
    )


# ============================================================
# POTENTIAL RESEARCH DIRECTIONS
# ============================================================

elif page == "🧭 Potential Research Directions":

    st.title(
        "🧭 Potential Research Directions"
    )

    st.info(
        """
        This module will suggest potentially
        underexplored research areas based on
        the uploaded research literature.

        AI-generated suggestions must be validated
        by the researcher using domain knowledge
        and further literature review.
        """
    )


# ============================================================
# RESEARCH SCORE
# ============================================================

elif page == "📊 Research Score":

    st.title("📊 Research Score")

    st.info(
        """
        Research Score will be implemented in a
        future development stage.
        """
    )