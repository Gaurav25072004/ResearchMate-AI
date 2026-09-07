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
    create_faiss_index
)


# --------------------------------------------------
# Embedding Model Cache
# --------------------------------------------------

@st.cache_resource
def get_embedding_model():
    """
    Load and cache the embedding model.

    Caching prevents Streamlit from loading the
    embedding model repeatedly on every interaction.
    """
    return load_embedding_model()


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="ResearchMate AI",
    page_icon="📚",
    layout="wide"
)


# --------------------------------------------------
# Sidebar Navigation
# --------------------------------------------------

st.sidebar.title("📚 ResearchMate AI")

st.sidebar.write(
    "AI-powered research assistant for literature analysis."
)

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigate",
    [
        "🏠 Home",
        "📄 Paper Analysis",
        "🧭 Potential Research Directions",
        "📚 Citation Analysis",
        "💡 Novelty Analysis",
        "📊 Research Score"
    ]
)


# --------------------------------------------------
# Home Page
# --------------------------------------------------

if page == "🏠 Home":

    st.title("📚 ResearchMate AI")

    st.subheader(
        "AI-Powered Research Assistant"
    )

    st.write(
        """
        ResearchMate AI helps students and researchers
        analyze research papers and understand existing
        literature using Artificial Intelligence.
        """
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("📄 Paper Analysis")

        st.write(
            "Upload and analyze research papers using "
            "automated text processing."
        )

    with col2:
        st.subheader("🧭 Potential Research Directions")

        st.write(
            "Suggest potential research directions by "
            "analyzing existing research literature."
        )

    with col3:
        st.subheader("📚 Citation Analysis")

        st.write(
            "Analyze citation information and research "
            "references."
        )

    col4, col5, col6 = st.columns(3)

    with col4:
        st.subheader("💡 Novelty Analysis")

        st.write(
            "Analyze research content to provide insights "
            "about potentially novel aspects."
        )

    with col5:
        st.subheader("📊 Research Score")

        st.write(
            "Generate an overall research-oriented score "
            "based on multiple analysis factors."
        )

    with col6:
        st.subheader("🤖 AI Research Assistant")

        st.write(
            "Use AI-powered retrieval and analysis to "
            "support research exploration."
        )


# --------------------------------------------------
# Paper Analysis
# --------------------------------------------------

elif page == "📄 Paper Analysis":

    st.title("📄 Research Paper Analysis")

    st.write(
        """
        Upload a research paper to extract, clean,
        split, embed, and index its content for
        semantic search.
        """
    )

    st.divider()

    uploaded_file = st.file_uploader(
        "Upload a research paper",
        type=["pdf"]
    )

    if uploaded_file is not None:

        st.success(
            f"Uploaded successfully: {uploaded_file.name}"
        )

        # --------------------------------------------------
        # Step 1: Extract Text
        # --------------------------------------------------

        raw_text, page_count = extract_text_from_pdf(
            uploaded_file
        )

        # --------------------------------------------------
        # Step 2: Clean Text
        # --------------------------------------------------

        text = clean_text(raw_text)

        # --------------------------------------------------
        # Step 3: Split Text into Chunks
        # --------------------------------------------------

        chunks = split_text_into_chunks(
            text,
            chunk_size=1500,
            chunk_overlap=200
        )

        # --------------------------------------------------
        # Step 4: Generate Embeddings
        # --------------------------------------------------

        with st.spinner(
            "Generating embeddings..."
        ):

            embedding_model = get_embedding_model()

            embeddings = generate_embeddings(
                chunks,
                embedding_model
            )

        # --------------------------------------------------
        # Step 5: Create FAISS Index
        # --------------------------------------------------

        with st.spinner(
            "Creating FAISS vector index..."
        ):

            faiss_index = create_faiss_index(
                embeddings
            )

        st.divider()

        # --------------------------------------------------
        # Paper Statistics
        # --------------------------------------------------

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                "File Name",
                uploaded_file.name
            )

        with col2:
            st.metric(
                "Pages",
                page_count
            )

        with col3:
            st.metric(
                "Characters",
                len(text)
            )

        with col4:
            st.metric(
                "Chunks",
                len(chunks)
            )

        with col5:

            embedding_dimension = (
                embeddings.shape[1]
                if len(embeddings) > 0
                else 0
            )

            st.metric(
                "Embedding Dimension",
                embedding_dimension
            )

        # --------------------------------------------------
        # Embedding Status
        # --------------------------------------------------

        if len(embeddings) > 0:

            st.success(
                f"Successfully generated "
                f"{len(embeddings)} embeddings "
                f"with {embeddings.shape[1]} dimensions each."
            )

        else:

            st.warning(
                "No embeddings were generated because "
                "no text chunks were available."
            )

        # --------------------------------------------------
        # FAISS Status
        # --------------------------------------------------

        if faiss_index is not None:

            st.success(
                f"FAISS index created successfully with "
                f"{faiss_index.ntotal} vectors."
            )

            st.info(
                f"FAISS vector dimension: "
                f"{faiss_index.d}"
            )

        else:

            st.warning(
                "FAISS index could not be created because "
                "no embeddings were available."
            )

        st.divider()

        # --------------------------------------------------
        # Cleaned Text
        # --------------------------------------------------

        st.subheader("🧹 Cleaned Text")

        st.text_area(
            "Processed research paper text",
            text,
            height=400
        )

        # --------------------------------------------------
        # Text Chunks
        # --------------------------------------------------

        st.subheader("🧩 Text Chunks")

        st.write(
            f"The paper has been divided into "
            f"**{len(chunks)} overlapping chunks** "
            f"for further analysis."
        )

        for i, chunk in enumerate(chunks):

            with st.expander(
                f"Chunk {i + 1}"
            ):

                st.write(chunk)

        # --------------------------------------------------
        # Embedding Preview
        # --------------------------------------------------

        st.subheader("🔢 Embedding Preview")

        if len(embeddings) > 0:

            st.write(
                """
                Each text chunk has been converted into
                a numerical vector using the
                `all-MiniLM-L6-v2` embedding model.
                """
            )

            st.write(
                f"Total embeddings: **{len(embeddings)}**"
            )

            st.write(
                f"Vector dimensions: **{embeddings.shape[1]}**"
            )

            st.write(
                "First embedding vector "
                "(first 10 values):"
            )

            st.code(
                str(embeddings[0][:10])
            )

        # --------------------------------------------------
        # FAISS Index Preview
        # --------------------------------------------------

        st.subheader("🔎 FAISS Vector Index")

        if faiss_index is not None:

            st.write(
                """
                FAISS stores the embedding vectors in a
                searchable index. This index will be used
                in the next stage for retrieving the most
                relevant research-paper chunks.
                """
            )

            st.write(
                f"Total vectors stored: "
                f"**{faiss_index.ntotal}**"
            )

            st.write(
                f"Vector dimension: "
                f"**{faiss_index.d}**"
            )

            st.success(
                "Research paper embeddings are now "
                "indexed and ready for semantic retrieval."
            )


# --------------------------------------------------
# Potential Research Directions
# --------------------------------------------------

elif page == "🧭 Potential Research Directions":

    st.title("🧭 Potential Research Directions")

    st.write(
        """
        This module will analyze research literature
        and suggest potential research directions
        for further investigation.
        """
    )

    st.info(
        """
        This feature will use retrieved research content
        and AI-based analysis to suggest potentially
        underexplored areas for further investigation.
        """
    )

    st.warning(
        """
        ⚠️ These are AI-generated suggestions and should
        be validated by the researcher using domain
        knowledge and further literature review.
        """
    )


# --------------------------------------------------
# Citation Analysis
# --------------------------------------------------

elif page == "📚 Citation Analysis":

    st.title("📚 Citation Analysis")

    st.write(
        """
        This module will analyze citations and references
        from research papers.
        """
    )

    st.info(
        "Citation analysis functionality will be implemented in a future development stage."
    )


# --------------------------------------------------
# Novelty Analysis
# --------------------------------------------------

elif page == "💡 Novelty Analysis":

    st.title("💡 Novelty Analysis")

    st.write(
        """
        This module will analyze research content and
        provide insights about potentially novel aspects
        of the research.
        """
    )

    st.info(
        "Novelty analysis functionality will be implemented in a future development stage."
    )


# --------------------------------------------------
# Research Score
# --------------------------------------------------

elif page == "📊 Research Score":

    st.title("📊 Research Score")

    st.write(
        """
        This module will generate an overall research
        score based on multiple analysis factors.
        """
    )

    st.info(
        "Research scoring functionality will be implemented in a future development stage."
    )


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "ResearchMate AI | MCA Capstone Project"
)