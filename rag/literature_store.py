from pathlib import Path

from rag.pdf_loader import extract_text_from_pdf
from rag.text_processor import (
    clean_text,
    split_text_into_chunks
)
from rag.embedding import generate_embeddings
from rag.vector_store import (
    create_faiss_index,
    hybrid_search
)


def load_literature_papers(
    literature_directory
):
    """
    Load research papers from the literature directory.

    Returns:
        List of dictionaries containing:
            - source
            - path
            - text
            - page_count
    """

    literature_directory = Path(
        literature_directory
    )

    if not literature_directory.exists():
        return []

    pdf_files = sorted(
        literature_directory.glob("*.pdf")
    )

    papers = []

    for pdf_path in pdf_files:

        with open(
            pdf_path,
            "rb"
        ) as pdf_file:

            text, page_count = (
                extract_text_from_pdf(
                    pdf_file
                )
            )

        cleaned_text = clean_text(
            text
        )

        papers.append({
            "source": pdf_path.name,
            "path": str(pdf_path),
            "text": cleaned_text,
            "page_count": page_count
        })

    return papers


def build_literature_corpus(
    literature_directory,
    embedding_model
):
    """
    Build a FAISS literature corpus from
    multiple research papers.

    The uploaded research paper is not included
    unless its PDF is explicitly placed inside
    the literature directory.

    Returns:
        {
            "index": FAISS index,
            "chunks": list of text chunks,
            "metadata": list of metadata dictionaries,
            "papers": list of paper information
        }
    """

    papers = load_literature_papers(
        literature_directory
    )

    all_chunks = []
    metadata = []

    for paper in papers:

        chunks = split_text_into_chunks(
            paper["text"]
        )

        for chunk in chunks:

            all_chunks.append(
                chunk
            )

            metadata.append({
                "source": paper["source"],
                "path": paper["path"],
                "page_count": paper["page_count"]
            })

    if not all_chunks:

        return {
            "index": None,
            "chunks": [],
            "metadata": [],
            "papers": papers
        }

    embeddings = generate_embeddings(
        all_chunks,
        embedding_model
    )

    index = create_faiss_index(
        embeddings
    )

    return {
        "index": index,
        "chunks": all_chunks,
        "metadata": metadata,
        "papers": papers
    }


def search_literature(
    literature_corpus,
    query,
    embedding_model,
    top_k=7
):
    """
    Search the separate literature corpus.

    Returns:
        List of dictionaries containing:
            - source
            - chunk
            - retrieval scores
    """

    if not literature_corpus:
        return []

    index = literature_corpus.get(
        "index"
    )

    chunks = literature_corpus.get(
        "chunks",
        []
    )

    metadata = literature_corpus.get(
        "metadata",
        []
    )

    if index is None or not chunks:
        return []

    query_embedding = (
        embedding_model.encode(
            [query]
        )[0]
    )

    results = hybrid_search(
        index,
        query_embedding,
        query,
        chunks,
        top_k=top_k
    )

    literature_results = []

    for result in results:

        chunk_index = result[
            "index"
        ]

        paper_metadata = metadata[
            chunk_index
        ]

        literature_results.append({
            "source": paper_metadata[
                "source"
            ],
            "path": paper_metadata[
                "path"
            ],
            "page_count": paper_metadata[
                "page_count"
            ],
            "chunk": result[
                "chunk"
            ],
            "semantic_score": result[
                "semantic_score"
            ],
            "keyword_score": result[
                "keyword_score"
            ],
            "section_score": result[
                "section_score"
            ],
            "final_score": result[
                "final_score"
            ]
        })

    return literature_results