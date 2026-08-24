import streamlit as st

from rag.pdf_loader import extract_text_from_pdf


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ResearchMate AI",
    page_icon="📚",
    layout="wide"
)


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

st.sidebar.title("📚 ResearchMate AI")

st.sidebar.write("### Navigation")

page = st.sidebar.radio(
    "Select Module",
    [
        "🏠 Home",
        "📄 Paper Analysis",
        "🔎 Research Gap",
        "📚 Citation Analysis",
        "💡 Novelty Analysis",
        "📊 Research Score"
    ]
)


# ============================================================
# HOME PAGE
# ============================================================

if page == "🏠 Home":

    st.title("📚 ResearchMate AI")

    st.subheader("AI-Powered Research Assistant")

    st.write(
        "ResearchMate AI is an intelligent research assistant "
        "designed to help students and researchers analyze "
        "research papers, identify research gaps, verify citations, "
        "and evaluate research proposals."
    )

    st.info(
        "🚧 ResearchMate AI is currently under development."
    )

    st.markdown("---")

    st.header("Welcome to ResearchMate AI")

    st.write(
        "Upload your research papers and use AI-powered tools "
        "to understand, analyze, and improve your research."
    )

    # --------------------------------------------------------
    # FEATURE CARDS - ROW 1
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        st.subheader("📄 Paper Analysis")

        st.write(
            "Analyze research papers and extract important "
            "information from academic documents."
        )

    with col2:

        st.subheader("🔎 Research Gap")

        st.write(
            "Identify potential research gaps by analyzing "
            "existing research literature."
        )

    with col3:

        st.subheader("📚 Citation Analysis")

        st.write(
            "Analyze references and citations used in "
            "research papers."
        )

    # --------------------------------------------------------
    # FEATURE CARDS - ROW 2
    # --------------------------------------------------------

    col4, col5, col6 = st.columns(3)

    with col4:

        st.subheader("💡 Novelty Analysis")

        st.write(
            "Evaluate the potential novelty and contribution "
            "of a research proposal."
        )

    with col5:

        st.subheader("📊 Research Score")

        st.write(
            "Evaluate research quality using multiple "
            "research-related criteria."
        )

    with col6:

        st.subheader("🤖 AI Assistant")

        st.write(
            "Interact with an AI assistant using "
            "Retrieval-Augmented Generation."
        )


# ============================================================
# PAPER ANALYSIS PAGE
# ============================================================

elif page == "📄 Paper Analysis":

    st.title("📄 Research Paper Analysis")

    st.write(
        "Upload a research paper in PDF format to extract "
        "and analyze its text."
    )

    st.markdown("---")

    # --------------------------------------------------------
    # PDF UPLOAD
    # --------------------------------------------------------

    uploaded_file = st.file_uploader(
        "Upload Research Paper",
        type=["pdf"],
        help="Upload a research paper in PDF format."
    )

    # --------------------------------------------------------
    # PROCESS PDF
    # --------------------------------------------------------

    if uploaded_file is not None:

        st.success(
            f"✅ Successfully uploaded: {uploaded_file.name}"
        )

        with st.spinner("📖 Extracting text from PDF..."):

            try:

                text, page_count = extract_text_from_pdf(
                    uploaded_file
                )

                # ------------------------------------------------
                # PAPER INFORMATION
                # ------------------------------------------------

                st.markdown("---")

                st.subheader("📋 Paper Information")

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "📄 File Name",
                        uploaded_file.name
                    )

                with col2:

                    st.metric(
                        "📑 Pages",
                        page_count
                    )

                with col3:

                    st.metric(
                        "🔤 Characters",
                        len(text)
                    )

                # ------------------------------------------------
                # EXTRACTED TEXT
                # ------------------------------------------------

                st.markdown("---")

                st.subheader("📄 Extracted Text")

                if text.strip():

                    st.text_area(
                        "Text extracted from the research paper:",
                        text,
                        height=500
                    )

                else:

                    st.warning(
                        "⚠️ No text could be extracted from this PDF."
                    )

                    st.write(
                        "The PDF may contain scanned images instead "
                        "of selectable text. OCR support can be added "
                        "later."
                    )

            except Exception as e:

                st.error(
                    "❌ An error occurred while processing the PDF."
                )

                st.exception(e)


# ============================================================
# RESEARCH GAP PAGE
# ============================================================

elif page == "🔎 Research Gap":

    st.title("🔎 Research Gap Analysis")

    st.info(
        "🚧 Research Gap Agent will be implemented in a later phase."
    )

    st.write(
        "This module will analyze research literature and "
        "identify potential research gaps."
    )


# ============================================================
# CITATION ANALYSIS PAGE
# ============================================================

elif page == "📚 Citation Analysis":

    st.title("📚 Citation Analysis")

    st.info(
        "🚧 Citation Analysis Agent will be implemented "
        "in a later phase."
    )

    st.write(
        "This module will analyze references and citations "
        "used in research papers."
    )


# ============================================================
# NOVELTY ANALYSIS PAGE
# ============================================================

elif page == "💡 Novelty Analysis":

    st.title("💡 Novelty Analysis")

    st.info(
        "🚧 Novelty Analysis Agent will be implemented "
        "in a later phase."
    )

    st.write(
        "This module will compare research ideas with "
        "existing literature to estimate potential novelty."
    )


# ============================================================
# RESEARCH SCORE PAGE
# ============================================================

elif page == "📊 Research Score":

    st.title("📊 Research Score")

    st.info(
        "🚧 Research Scoring Agent will be implemented "
        "in a later phase."
    )

    st.write(
        "This module will evaluate research quality using "
        "multiple research criteria."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "ResearchMate AI | MCA Capstone Project"
)