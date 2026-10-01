from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from backend.ai_core.gemini_generator import (
    GeminiDocumentGenerator
)

from backend.schemas import (
    DocumentRequest,
    DocumentResponse
)

from backend.services.document_formatter import (
    format_docx,
    format_pdf,
    format_txt
)

from backend.utils.text_utils import (
    sanitize_text
)


router = APIRouter()

_generator = None


def get_generator():

    global _generator

    if _generator is None:

        _generator = (
            GeminiDocumentGenerator()
        )

    return _generator


# ============================================================
# AI DOCUMENT GENERATION
# ============================================================

@router.post(
    "/generate",
    response_model=DocumentResponse
)
def generate_document(
    payload: DocumentRequest
):

    try:

        generated_text = (
            get_generator()
            .generate_document(
                document_type=payload.document_type,
                parties=payload.parties,
                terms=payload.terms,
                dates=payload.dates,
            )
        )

        generated_text = sanitize_text(
            generated_text
        )

        return DocumentResponse(
            success=True,
            document_type=payload.document_type,
            text=generated_text
        )

    except RuntimeError as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Unexpected generation error: "
                f"{exc}"
            )
        ) from exc


# ============================================================
# TXT EXPORT
# ============================================================

@router.post(
    "/export/txt"
)
def export_txt(
    document_type: str,
    text: str
):

    content = format_txt(
        text
    )

    filename = (
        document_type
        .replace(" ", "_")
        + ".txt"
    )

    return Response(
        content=content,
        media_type="text/plain; charset=utf-8",
        headers={
            "Content-Disposition":
                f'attachment; filename="{filename}"'
        }
    )


# ============================================================
# DOCX EXPORT
# ============================================================

@router.post(
    "/export/docx"
)
def export_docx(
    document_type: str,
    text: str
):

    try:

        content = format_docx(
            text,
            document_type
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                f"DOCX generation failed: "
                f"{exc}"
            )
        ) from exc

    filename = (
        document_type
        .replace(" ", "_")
        + ".docx"
    )

    return Response(
        content=content,
        media_type=(
            "application/vnd.openxmlformats-"
            "officedocument.wordprocessingml.document"
        ),
        headers={
            "Content-Disposition":
                f'attachment; filename="{filename}"'
        }
    )


# ============================================================
# PDF EXPORT
# ============================================================

@router.post(
    "/export/pdf"
)
def export_pdf(
    document_type: str,
    text: str
):

    try:

        content = format_pdf(
            text,
            document_type
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                f"PDF generation failed: "
                f"{exc}"
            )
        ) from exc

    filename = (
        document_type
        .replace(" ", "_")
        + ".pdf"
    )

    return Response(
        content=content,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'attachment; filename="{filename}"'
        }
    )