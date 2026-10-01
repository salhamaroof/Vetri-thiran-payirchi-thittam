from __future__ import annotations

from google import genai
from google.genai import types

from backend.config import settings


class GeminiDocumentGenerator:
    """
    Generates legal-document drafts using Gemini.
    """

    SYSTEM_INSTRUCTION = """
You are LegalEase, an AI assistant for drafting
legal-document templates.

Your task is to create a clear, professional FIRST
DRAFT based only on information supplied by the user.

Rules:

1. Never invent names, dates, addresses, amounts,
   laws, courts, registration numbers, or other facts.

2. If important information is missing, use a clear
   placeholder such as:

   [INSERT ADDRESS]

   or

   [INSERT PAYMENT AMOUNT]

3. Produce a structured document suitable for editing.

4. Use professional and easy-to-understand English.

5. Include a suitable document title.

6. Include appropriate sections for the requested
   document type.

7. Incorporate the user's terms accurately.

8. Do not claim that the document is guaranteed
   legally valid.

9. Do not use markdown code fences.

10. End with appropriate signature blocks.

11. Return only the document draft.

The output is a draft and should be reviewed by a
qualified legal professional before real-world use.
"""

    def __init__(self) -> None:

        if not settings.gemini_api_key:

            raise RuntimeError(
                "GEMINI_API_KEY is not configured. "
                "Add it to the .env file."
            )

        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

        self.model = settings.gemini_model

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
    ) -> str:

        prompt = f"""
Create a professional draft of the following
legal document.

DOCUMENT TYPE:
{document_type}

PARTIES:
{parties}

TERMS AND CONDITIONS:
{terms}

EFFECTIVE DATE:
{dates}

Create the document with the following structure
where appropriate:

1. Document title
2. Introduction or recitals
3. Parties
4. Definitions
5. Main clauses
6. User-provided terms
7. Effective date
8. General provisions
9. Termination provisions
10. Governing-law section where appropriate
11. Signature blocks

Important:

- Do not invent facts.
- Use [INSERT ...] placeholders when required.
- Keep the language professional.
- Return only the document.
"""

        try:

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.SYSTEM_INSTRUCTION,
                    temperature=0.2,
                    max_output_tokens=8000,
                ),
            )

        except Exception as exc:

            raise RuntimeError(
                f"Gemini generation failed: {exc}"
            ) from exc

        generated_text = getattr(
            response,
            "text",
            None
        )

        if not generated_text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        generated_text = generated_text.strip()

        if not generated_text:
            raise RuntimeError(
                "Gemini returned an empty document."
            )

        return generated_text