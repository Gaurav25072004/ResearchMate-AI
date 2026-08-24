import fitz


def extract_text_from_pdf(pdf_file):
    """
    Extract text from an uploaded PDF file.

    Parameters:
        pdf_file: Streamlit UploadedFile object

    Returns:
        full_text: Complete extracted text
        page_count: Number of pages in the PDF
    """

    pdf_bytes = pdf_file.read()

    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    full_text = ""

    for page in document:
        page_text = page.get_text()

        if page_text.strip():
            full_text += page_text + "\n"

    page_count = len(document)

    document.close()

    return full_text, page_count