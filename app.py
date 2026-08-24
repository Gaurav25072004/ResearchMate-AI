import streamlit as st


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="ResearchMate AI",
    page_icon="📚",
    layout="wide"
)


# --------------------------------------------------
# Main Title
# --------------------------------------------------

st.title("📚 ResearchMate AI")

st.subheader("AI-Powered Research Assistant")

st.write(
    "ResearchMate AI is an intelligent research assistant "
    "designed to help students and researchers analyze research "
    "papers, identify research gaps, verify citations, and "
    "evaluate research proposals."
)


# --------------------------------------------------
# Project Status
# --------------------------------------------------

st.info(
    "🚧 ResearchMate AI is currently under development."
)


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.title("📚 ResearchMate AI")

st.sidebar.write("### Navigation")

st.sidebar.button("📄 Paper Analysis")

st.sidebar.button("🔎 Research Gap")

st.sidebar.button("📚 Citation Analysis")

st.sidebar.button("💡 Novelty Analysis")

st.sidebar.button("📊 Research Score")


# --------------------------------------------------
# Main Dashboard
# --------------------------------------------------

st.markdown("---")

st.header("Welcome to ResearchMate AI")

st.write(
    "Upload your research papers and use AI-powered tools "
    "to understand, analyze, and improve your research."
)


# --------------------------------------------------
# Feature Overview
# --------------------------------------------------

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


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.markdown("---")

st.caption(
    "ResearchMate AI | MCA Capstone Project"
)