import streamlit as st

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
    build_rag_prompt
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
    """
    Load the sentence-transformer embedding model.
    """

    return load_embedding_model()


@st.cache_resource
def get_gemini_model():
    """
    Load the Gemini client.
    """

    return load_gemini_model()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("📚 ResearchMate AI")

st.sidebar.write(
    "AI-Powered Research Assistant"
)

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
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
# HOME PAGE
# ============================================================

if page == "🏠 Home":

    st.title("📚 ResearchMate AI")

    st.subheader(
        "AI-Powered Research Assistant"
    )

    st.write(
        """
        ResearchMate AI helps researchers analyze
        academic papers using Natural Language Processing,
        semantic search, Retrieval-Augmented Generation,
        and Large Language Models.
        """
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info(
            """
            ### 📄 Paper Analysis

            Upload and analyze research papers,
            extract text, and retrieve relevant
            information.
            """
        )

    with col2:
        st.info(
            """
            ### 🔎 Citation Analysis

            Analyze citation-related information
            from research literature.
            """
        )

    with col3:
        st.info(
            """
            ### ✨ Novelty Analysis

            Analyze research literature to support
            novelty assessment.
            """
        )

    st.divider()

    col4, col5, col6 = st.columns(3)

    with col4:
        st.info(
            """
            ### 🧭 Potential Research Directions

            Suggest potential research directions
            based on existing literature.
            """
        )

    with col5:
        st.info(
            """
            ### 📊 Research Score

            Provide an overall research-oriented
            analysis score.
            """
        )

    with col6:
        st.info(
            """
            ### 🤖 RAG + LLM

            Generate grounded answers using
            retrieved research-paper content.
            """
        )


# ============================================================
# PAPER ANALYSIS
# ============================================================

elif page == "📄 Paper Analysis":

    st.title("📄 Research Paper Analysis")

    st.write(
        """
        Upload a research paper to extract, clean,
        process, embed, index, and retrieve its content.
        """
    )

    uploaded_file = st.file_uploader(
        "Upload a research paper PDF",
        type=["pdf"]
    )

    if uploaded_file is not None:

        # ----------------------------------------------------
        # STEP 1: PDF EXTRACTION
        # ----------------------------------------------------

        with st.spinner(
            "Extracting text from PDF..."
        ):

            raw_text, page_count = (
                extract_text_from_pdf(
                    uploaded_file
                )
            )

        # ----------------------------------------------------
        # STEP 2: TEXT CLEANING
        # ----------------------------------------------------

        cleaned_text = clean_text(
            raw_text
        )

        # ----------------------------------------------------
        # STEP 3: CHUNKING
        # ----------------------------------------------------

        chunks = split_text_into_chunks(
            cleaned_text,
            chunk_size=1500,
            chunk_overlap=200
        )

        # ----------------------------------------------------
        # STEP 4: LOAD EMBEDDING MODEL
        # ----------------------------------------------------

        with st.spinner(
            "Loading embedding model..."
        ):

            embedding_model = (
                get_embedding_model()
            )

        # ----------------------------------------------------
        # STEP 5: GENERATE EMBEDDINGS
        # ----------------------------------------------------

        with st.spinner(
            "Generating embeddings..."
        ):

            embeddings = generate_embeddings(
                chunks,
                embedding_model
            )

        # ----------------------------------------------------
        # STEP 6: CREATE FAISS INDEX
        # ----------------------------------------------------

        with st.spinner(
            "Creating FAISS vector index..."
        ):

            faiss_index = create_faiss_index(
                embeddings
            )

        # ----------------------------------------------------
        # METRICS
        # ----------------------------------------------------

        st.success(
            "Research paper processed successfully!"
        )

        col1, col2, col3, col4, col5 = (
            st.columns(5)
        )

        with col1:
            st.metric(
                "Pages",
                page_count
            )

        with col2:
            st.metric(
                "Characters",
                len(raw_text)
            )

        with col3:
            st.metric(
                "Chunks",
                len(chunks)
            )

        with col4:

            if len(embeddings) > 0:

                st.metric(
                    "Embedding Dimension",
                    embeddings.shape[1]
                )

            else:

                st.metric(
                    "Embedding Dimension",
                    0
                )

        with col5:

            if faiss_index is not None:

                st.metric(
                    "FAISS Vectors",
                    faiss_index.ntotal
                )

            else:

                st.metric(
                    "FAISS Vectors",
                    0
                )

        # ----------------------------------------------------
        # RAW EXTRACTED TEXT
        # ----------------------------------------------------

        st.subheader(
            "📄 Extracted Text"
        )

        with st.expander(
            "View extracted text"
        ):

            st.text_area(
                "Raw PDF Text",
                raw_text,
                height=300
            )

        # ----------------------------------------------------
        # CLEANED TEXT
        # ----------------------------------------------------

        st.subheader(
            "🧹 Cleaned Text"
        )

        with st.expander(
            "View cleaned text"
        ):

            st.text_area(
                "Cleaned Research Paper Text",
                cleaned_text,
                height=300
            )

        # ----------------------------------------------------
        # CHUNKS
        # ----------------------------------------------------

        st.subheader(
            "🧩 Text Chunks"
        )

        st.write(
            f"Generated **{len(chunks)}** chunks."
        )

        with st.expander(
            "View generated chunks"
        ):

            for i, chunk in enumerate(
                chunks,
                start=1
            ):

                st.markdown(
                    f"### Chunk {i}"
                )

                st.info(chunk)

        # ----------------------------------------------------
        # EMBEDDINGS
        # ----------------------------------------------------

        st.subheader(
            "🔢 Embeddings"
        )

        if len(embeddings) > 0:

            st.write(
                f"Embedding shape: "
                f"`{embeddings.shape}`"
            )

            st.write(
                "First embedding preview:"
            )

            st.code(
                str(
                    embeddings[0][:10]
                )
            )

        # ----------------------------------------------------
        # FAISS INDEX
        # ----------------------------------------------------

        st.subheader(
            "🗂️ FAISS Vector Index"
        )

        if faiss_index is not None:

            st.success(
                f"FAISS index contains "
                f"**{faiss_index.ntotal}** vectors."
            )

            st.write(
                f"Vector dimension: "
                f"**{faiss_index.d}**"
            )

        # ====================================================
        # HYBRID SEMANTIC RETRIEVAL
        # ====================================================

        st.divider()

        st.subheader(
            "🔎 Semantic + Hybrid Retrieval"
        )

        st.write(
            """
            Enter a research question to retrieve
            the most relevant sections from the
            uploaded research paper.

            Retrieval combines semantic similarity,
            keyword matching, and section relevance.
            """
        )

        query = st.text_input(
            "Enter your research question",
            placeholder=(
                "Example: What methodology was "
                "used in this research?"
            )
        )

        top_k = st.slider(
            "Number of relevant chunks to retrieve",
            min_value=1,
            max_value=10,
            value=5
        )

        # ----------------------------------------------------
        # RETRIEVAL
        # ----------------------------------------------------

        if query:

            if faiss_index is not None:

                with st.spinner(
                    "Searching for relevant content..."
                ):

                    query_embedding = (
                        embedding_model.encode(
                            [query]
                        )
                    )

                    retrieval_results = (
                        hybrid_search(
                            faiss_index,
                            query_embedding,
                            query,
                            chunks,
                            top_k=top_k
                        )
                    )

                st.success(
                    f"Retrieved "
                    f"**{len(retrieval_results)}** "
                    f"relevant chunks."
                )

                # ------------------------------------------------
                # DISPLAY RETRIEVED RESULTS
                # ------------------------------------------------

                st.subheader(
                    "📌 Retrieved Evidence"
                )

                retrieved_chunks = []

                for rank, result in enumerate(
                    retrieval_results,
                    start=1
                ):

                    st.markdown(
                        f"### Result {rank}"
                    )

                    st.write(
                        f"**Hybrid Score:** "
                        f"{result['final_score']:.4f}"
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
                        f"**Chunk "
                        f"{result['index'] + 1}**"
                    )

                    st.info(
                        result["chunk"]
                    )

                    retrieved_chunks.append(
                        result["chunk"]
                    )

                    st.divider()

                # =================================================
                # GEMINI RAG
                # =================================================

                if retrieved_chunks:

                    st.subheader(
                        "🤖 ResearchMate AI Answer"
                    )

                    with st.spinner(
                        "Generating grounded answer..."
                    ):

                        try:

                            gemini_model = (
                                get_gemini_model()
                            )

                            rag_prompt = (
                                build_rag_prompt(
                                    query,
                                    retrieved_chunks
                                )
                            )

                            answer = generate_answer(
                                gemini_model,
                                rag_prompt
                            )

                            st.write(answer)

                        except Exception as e:

                            st.error(
                                "An error occurred "
                                "while generating the "
                                "Gemini response."
                            )

                            st.exception(e)

                    # ---------------------------------------------
                    # DISCLAIMER
                    # ---------------------------------------------

                    st.caption(
                        "⚠️ The answer is generated using "
                        "retrieved content from the uploaded "
                        "research paper. AI-generated responses "
                        "should be verified against the original "
                        "paper."
                    )

            else:

                st.warning(
                    "FAISS index is not available."
                )


# ============================================================
# CITATION ANALYSIS
# ============================================================

elif page == "🔎 Citation Analysis":

    st.title(
        "🔎 Citation Analysis"
    )

    st.info(
        """
        Citation analysis will be implemented
        in a future development phase.
        """
    )


# ============================================================
# NOVELTY ANALYSIS
# ============================================================

elif page == "✨ Novelty Analysis":

    st.title(
        "✨ Novelty Analysis"
    )

    st.info(
        """
        Novelty analysis will be implemented
        in a future development phase.
        """
    )


# ============================================================
# POTENTIAL RESEARCH DIRECTIONS
# ============================================================

elif page == "🧭 Potential Research Directions":

    st.title(
        "🧭 Potential Research Directions"
    )

    st.write(
        """
        This module will analyze research literature
        and suggest potential research directions
        for further investigation.
        """
    )

    st.warning(
        """
        ⚠️ These are AI-generated suggestions and
        should be validated by the researcher using
        domain knowledge and further literature review.
        """
    )


# ============================================================
# RESEARCH SCORE
# ============================================================

elif page == "📊 Research Score":

    st.title(
        "📊 Research Score"
    )

    st.info(
        """
        Research scoring will be implemented
        in a future development phase.
        """
    )