import re


def clean_text(text):
    """
    Clean extracted research paper text.

    Removes unnecessary whitespace while preserving
    the actual content of the research paper.
    """

    if not text:
        return ""

    # Replace multiple spaces/tabs with a single space
    text = re.sub(r"[ \t]+", " ", text)

    # Replace multiple newlines with a single newline
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    # Remove spaces at the beginning and end of each line
    text = "\n".join(
        line.strip()
        for line in text.splitlines()
    )

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def split_text_into_chunks(
    text,
    chunk_size=1500,
    chunk_overlap=200
):
    """
    Split text into overlapping chunks.

    Parameters:
        text: Cleaned research paper text
        chunk_size: Maximum approximate size of each chunk
        chunk_overlap: Number of characters shared between chunks

    Returns:
        List of text chunks
    """

    if not text:
        return []

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size."
        )

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = min(
            start + chunk_size,
            text_length
        )

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - chunk_overlap

    return chunks