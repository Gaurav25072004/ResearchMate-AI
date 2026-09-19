import re
import pymupdf


def extract_references_section(text):
    """
    Extract the References section from plain text.

    This function is useful for normal text-based documents
    where references are represented sequentially.
    """

    lines = text.splitlines()

    start_index = None
    end_index = len(lines)

    for i, line in enumerate(lines):

        cleaned = line.strip()

        # Remove markdown heading markers
        cleaned = re.sub(
            r"^#+\s*",
            "",
            cleaned
        )

        # Remove section numbering such as:
        # 8 References
        # 9. References
        cleaned = re.sub(
            r"^\d+(?:\.\d+)*\s*",
            "",
            cleaned,
        ).strip()

        if cleaned.lower() in {
            "references",
            "reference"
        }:
            start_index = i + 1
            break

    if start_index is None:
        return ""

    # Stop at common following sections
    for i in range(start_index, len(lines)):

        cleaned = lines[i].strip()

        cleaned = re.sub(
            r"^#+\s*",
            "",
            cleaned
        )

        cleaned = re.sub(
            r"^\d+(?:\.\d+)*\s*",
            "",
            cleaned,
        ).strip()

        if cleaned.lower() in {
            "appendix",
            "appendices"
        }:
            end_index = i
            break

    return "\n".join(
        lines[start_index:end_index]
    ).strip()


def is_reference_start(text):
    """
    Detect whether a text block looks like the beginning
    of an individual reference.

    Supports:
    - Numbered references: [1], [2], etc.
    - Numbered references: 1.
    - Author-year references: Author Name. 2024.
    """

    text = text.strip()

    if not text:
        return False

    # [1] Reference
    if re.match(
        r"^\[\d+\]",
        text
    ):
        return True

    # 1. Reference
    if re.match(
        r"^\d+\.\s+",
        text
    ):
        return True

    # Author ... 2024.
    if re.search(
        r"\b(19|20)\d{2}\.",
        text
    ):
        return True

    return False


def parse_references(references_text):
    """
    Parse references from normal sequential text.

    This is mainly used for simple text-based PDFs.
    Layout-aware PDF extraction uses parse_layout_references().
    """

    if not references_text.strip():
        return []

    lines = references_text.splitlines()

    references = []
    current_reference = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if is_reference_start(line):

            if current_reference:
                references.append(
                    " ".join(current_reference)
                )

            current_reference = [line]

        else:

            if current_reference:
                current_reference.append(line)

    if current_reference:
        references.append(
            " ".join(current_reference)
        )

    return references


def find_references_start_page(document):
    """
    Find the page containing the References heading.
    """

    for page_number, page in enumerate(document):

        blocks = page.get_text("blocks")

        for block in blocks:

            if len(block) < 5:
                continue

            text = block[4].strip()

            normalized = text.lower()

            if normalized in {
                "references",
                "reference"
            }:
                return page_number

    return None


def extract_reference_pages(document):
    """
    Extract layout-aware blocks belonging to the References section.

    Important:
    The extraction starts only AFTER the actual
    'References' heading.

    This prevents preceding sections such as
    'Limitations' from being interpreted as references.
    """

    reference_blocks = []

    references_found = False
    stop_extraction = False

    for page_number, page in enumerate(document):

        blocks = page.get_text("blocks")

        page_blocks = []

        for block in blocks:

            if len(block) < 5:
                continue

            x0, y0, x1, y1, text = block[:5]

            text = text.strip()

            if not text:
                continue

            page_blocks.append(
                {
                    "page": page_number,
                    "x0": x0,
                    "y0": y0,
                    "x1": x1,
                    "y1": y1,
                    "text": text
                }
            )

        # Sort from top to bottom, then left to right
        page_blocks.sort(
            key=lambda b: (
                b["y0"],
                b["x0"]
            )
        )

        processed_page_blocks = []

        for block in page_blocks:

            text = block["text"].strip()

            normalized = text.lower()

            # -------------------------------------------------
            # Find References heading
            # -------------------------------------------------

            if not references_found:

                if normalized in {
                    "references",
                    "reference"
                }:

                    references_found = True

                    # Do not include the heading itself
                    continue

                # Ignore everything before References
                continue

            # -------------------------------------------------
            # Stop at Appendix
            # -------------------------------------------------

            if normalized in {
                "appendix",
                "appendices"
            }:

                stop_extraction = True
                break

            if normalized.startswith(
                "appendix "
            ):

                stop_extraction = True
                break

            if normalized.startswith(
                "a appendix"
            ):

                stop_extraction = True
                break

            processed_page_blocks.append(
                block
            )

        if stop_extraction:
            break

        reference_blocks.extend(
            processed_page_blocks
        )

    return reference_blocks


def group_reference_blocks(column_blocks):
    """
    Group PDF blocks into individual references.

    The paper uses a two-column layout.

    A new reference normally starts at the left edge
    of its column, while continuation lines are slightly
    indented.

    Therefore geometry is used instead of relying only
    on author/year regex detection.
    """

    if not column_blocks:
        return []

    # Sort top-to-bottom
    column_blocks = sorted(
        column_blocks,
        key=lambda b: (
            b["page"],
            b["y0"]
        )
    )

    # Determine the left-most x position
    # of this column.
    column_start_x = min(
        block["x0"]
        for block in column_blocks
    )

    references = []
    current_reference = []

    # Small tolerance for PDF floating-point differences
    start_tolerance = 5

    for block in column_blocks:

        x0 = block["x0"]

        is_new_reference = (
            x0 <= column_start_x + start_tolerance
        )

        if not current_reference:

            current_reference = [block]

        elif is_new_reference:

            references.append(
                current_reference
            )

            current_reference = [block]

        else:

            current_reference.append(
                block
            )

    if current_reference:

        references.append(
            current_reference
        )

    return references


def clean_reference_text(text):
    """
    Clean common PDF extraction artifacts from references.

    Handles words that were split across lines with
    a hyphen during PDF extraction.
    """

    # Fix words split across lines:
    # "creativ- ity" -> "creativity"
    text = re.sub(
        r"(\w)-\s+(\w)",
        r"\1\2",
        text
    )

    # Normalize multiple spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def parse_layout_references(reference_blocks):
    """
    Reconstruct references from PDF layout blocks.

    Handles:
    - Two-column papers
    - Multi-line references
    - Author-year references
    - Continuation lines
    """

    if not reference_blocks:
        return []

    # Group blocks by page
    pages = {}

    for block in reference_blocks:

        page_number = block["page"]

        if page_number not in pages:
            pages[page_number] = []

        pages[page_number].append(
            block
        )

    all_references = []

    for page_number in sorted(pages.keys()):

        page_blocks = pages[page_number]

        # Separate left and right columns
        left_column = []
        right_column = []

        for block in page_blocks:

            if block["x0"] < 300:

                left_column.append(
                    block
                )

            else:

                right_column.append(
                    block
                )

        # Process left column
        if left_column:

            left_references = group_reference_blocks(
                left_column
            )

            for reference_blocks_group in left_references:

                text = " ".join(
                    block["text"]
                    for block in reference_blocks_group
                )

                text = clean_reference_text(
                    text
                )

                if text:
                    all_references.append(
                        text
                    )

        # Process right column
        if right_column:

            right_references = group_reference_blocks(
                right_column
            )

            for reference_blocks_group in right_references:

                text = " ".join(
                    block["text"]
                    for block in reference_blocks_group
                )

                text = clean_reference_text(
                    text
                )

                if text:
                    all_references.append(
                        text
                    )

    return all_references


def analyze_citations(text):
    """
    Analyze citations from normal extracted text.
    """

    references_text = extract_references_section(
        text
    )

    references = parse_references(
        references_text
    )

    return {
        "total_references": len(references),
        "parsed_references": references
    }


def analyze_pdf_citations(pdf_path):
    """
    Analyze citations directly from a PDF file.

    Uses PyMuPDF block coordinates to handle
    two-column research papers.
    """

    document = pymupdf.open(
        pdf_path
    )

    page_count = len(document)

    reference_blocks = extract_reference_pages(
        document
    )

    references = parse_layout_references(
        reference_blocks
    )

    document.close()

    return {
        "page_count": page_count,
        "reference_blocks": len(reference_blocks),
        "total_references": len(references),

        # Keep the key expected by test_real_citations.py
        "references": references,

        # Keep this too for future code compatibility
        "parsed_references": references
    }