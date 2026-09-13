import os
from dotenv import load_dotenv
from google import genai


load_dotenv()


def load_gemini_model():
    """
    Create the Gemini client using the API key
    stored in the .env file.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found in .env file."
        )

    client = genai.Client(
        api_key=api_key
    )

    return client


def generate_answer(client, prompt):
    """
    Generate an answer using the Gemini model.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text
def build_rag_prompt(question, retrieved_chunks):
    """
    Build a prompt using the user's question
    and relevant chunks retrieved from the research paper.
    """

    context = "\n\n".join(
        retrieved_chunks
    )

    prompt = f"""
You are a research assistant.

Answer the user's question using only the
information provided in the research paper context below.

If the context does not contain enough information
to answer the question, clearly say that the
uploaded research paper does not provide sufficient
information.

Do not invent or assume information that is not
present in the context.

Research Paper Context:
-----------------------
{context}
-----------------------

User Question:
{question}

Answer:
"""

    return prompt