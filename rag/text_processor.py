
import re


def clean_text(text):
    """
    Clean extracted research paper text.

    Removes unnecessary whitespace while preserving
    the actual content and line structure.
    """
    if not text:
        return ""

    text = re.sub(r"[ \t]+", " ", text)

    text = re.sub(r"\n\s*\n+", "\n\n", text)

    text = "\n".join(
        line.strip()
        for line in text.splitlines()
    )

    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def is_section_heading(line):
    """
    Determine whether a line is a standalone research-paper heading.
    """
    line = line.strip()

    if not line:
        return False

    known_headings = {
        "abstract",
        "introduction",
        "background",
        "related work",
        "literature review",
        "methodology",
        "methods",
        "materials and methods",
        "experimental setup",
        "experiments",
        "results",
        "discussion",
        "results and discussion",
        "evaluation",
        "conclusion",
        "conclusions",
        "future work",
        "limitations",
        "acknowledgments",
        "acknowledgements",
        "references",
        "appendix",
    }

    return line.casefold() in known_headings


def split_text_into_sections(text):
    """
    Split research paper text into logical sections.

    Handles:
    - Common standalone section headings.
    - Numbered headings where the number and title
      appear on separate lines.
    - Lettered headings where the letter and title
      appear on separate lines.
    """
    if not text:
        return []

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    sections = []
    current_section = "Document"
    current_lines = []

    i = 0

    while i < len(lines):
        line = lines[i]

        # Case 1: Number and title are on separate lines.
        # Example:
        # 4
        # RAG-Novelty
        if re.fullmatch(r"\d+(?:\.\d+)*", line):
            if i + 1 < len(lines):
                next_line = lines[i + 1]

                if re.fullmatch(
                    r"[A-Za-z][A-Za-z0-9 ,:&()'/-]*",
                    next_line,
                ):
                    heading = f"{line} {next_line}"

                    if current_lines:
                        sections.append({
                            "section": current_section,
                            "text": " ".join(current_lines),
                        })

                    current_section = heading
                    current_lines = []

                    i += 2
                    continue

        # Case 2: Lettered section number and title.
        # Example:
        # A
        # Appendix
        if re.fullmatch(r"[A-Z](?:\.\d+)*", line):
            if i + 1 < len(lines):
                next_line = lines[i + 1]

                if re.fullmatch(
                    r"[A-Za-z][A-Za-z0-9 ,:&()'/-]*",
                    next_line,
                ):
                    heading = f"{line} {next_line}"

                    if current_lines:
                        sections.append({
                            "section": current_section,
                            "text": " ".join(current_lines),
                        })

                    current_section = heading
                    current_lines = []

                    i += 2
                    continue

        # Case 3: Recognized standalone section heading.
        if is_section_heading(line):
            if current_lines:
                sections.append({
                    "section": current_section,
                    "text": " ".join(current_lines),
                })

            current_section = line
            current_lines = []

            i += 1
            continue

        # Case 4: Normal content.
        current_lines.append(line)
        i += 1

    # Save the final section.
    if current_lines:
        sections.append({
            "section": current_section,
            "text": " ".join(current_lines),
        })

    return sections


def split_text_into_chunks(
    text,
    chunk_size=1500,
    chunk_overlap=200,
):
    """
    Split research paper text into overlapping chunks
    while preserving section information.
    """
    if not text:
        return []

    if not isinstance(chunk_size, int) or isinstance(chunk_size, bool):
        raise TypeError("chunk_size must be an integer.")

    if not isinstance(chunk_overlap, int) or isinstance(chunk_overlap, bool):
        raise TypeError("chunk_overlap must be an integer.")

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative.")

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size."
        )

    sections = split_text_into_sections(text)
    chunks = []

    for section in sections:
        section_name = section["section"]
        section_text = section["text"]

        if not section_text:
            continue

        prefix = f"Section: {section_name}\n\n"
        available_size = chunk_size - len(prefix)

        if available_size <= 0:
            raise ValueError(
                "chunk_size is too small for the section prefix."
            )

        start = 0
        text_length = len(section_text)

        while start < text_length:
            end = min(
                start + available_size,
                text_length,
            )

            chunk_text = section_text[start:end].strip()

            if chunk_text:
                chunks.append(prefix + chunk_text)

            if end >= text_length:
                break

            start = end - chunk_overlap

    return chunks
