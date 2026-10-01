from __future__ import annotations

import html
import os

from datetime import date

import requests

import streamlit as st

from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        text-align: center;
        font-size: 2.7rem;
        font-weight: 800;
        margin-bottom: 0.1rem;
    }

    .subtitle {
        text-align: center;
        color: #6b7280;
        margin-bottom: 1.5rem;
    }

    .legal-card {
        background: #111827;
        color: #f9fafb;
        border-radius: 14px;
        padding: 28px;
        border: 1px solid #374151;
        max-height: 650px;
        overflow-y: auto;
        line-height: 1.65;
        white-space: pre-wrap;
    }

    .notice {
        padding: 12px 15px;
        border-radius: 10px;
        background: #fff7ed;
        border: 1px solid #fed7aa;
        color: #7c2d12;
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">⚖️ LegalEase</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-Powered Legal Document Generator'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="notice">'
    'LegalEase creates editable legal-document drafts. '
    'Review generated content before real-world use.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "document" not in st.session_state:

    st.session_state.document = ""


if "generated_type" not in st.session_state:

    st.session_state.generated_type = ""


if "editing" not in st.session_state:

    st.session_state.editing = False


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header(
        "Document Details"
    )

    document_type = st.selectbox(
        "Document Type",

        [
            "Non-Disclosure Agreement",
            "Employment Contract",
            "Lease Agreement",
            "Service Agreement",
            "Freelance Work Contract",
            "Employment Offer Letter",
            "General Agreement",
            "Custom Legal Document"
        ]
    )

    if (
        document_type
        == "Custom Legal Document"
    ):

        document_type = st.text_input(
            "Custom document type",

            placeholder=(
                "e.g. Partnership Agreement"
            )
        )

    parties = st.text_area(
        "Parties Involved",

        placeholder=(
            "Jane Doe (Service Provider), "
            "TechNova Inc. (Client)"
        ),

        height=120
    )

    terms = st.text_area(
        "Terms & Conditions",

        placeholder=(
            "Payment within 30 days;\n"
            "Confidentiality must be maintained;\n"
            "Either party may terminate "
            "with 15 days notice"
        ),

        height=180
    )

    effective_date = st.date_input(
        "Effective Date",

        value=date.today()
    )

    generate = st.button(
        "Generate Document",

        type="primary",

        use_container_width=True
    )

    clear = st.button(
        "Clear",

        use_container_width=True
    )


# ============================================================
# CLEAR BUTTON
# ============================================================

if clear:

    st.session_state.document = ""

    st.session_state.generated_type = ""

    st.session_state.editing = False

    st.rerun()


# ============================================================
# TERM NORMALIZATION
# ============================================================

def normalize_terms(
    value: str
) -> str:

    value = value.replace(
        "\n",
        ";"
    )

    parts = [
        part.strip()
        for part in value.split(";")
        if part.strip()
    ]

    return "; ".join(parts)


# ============================================================
# GENERATE DOCUMENT
# ============================================================

if generate:

    if not document_type.strip():

        st.error(
            "Please enter a document type."
        )

        st.stop()

    if not parties.strip():

        st.error(
            "Please enter the parties involved."
        )

        st.stop()

    if not terms.strip():

        st.error(
            "Please enter at least one "
            "term or condition."
        )

        st.stop()

    payload = {

        "document_type":
            document_type.strip(),

        "parties":
            parties.strip(),

        "terms":
            normalize_terms(terms),

        "dates":
            effective_date.strftime(
                "%B %d, %Y"
            )
    }

    with st.spinner(
        "Generating your legal-document draft..."
    ):

        try:

            response = requests.post(

                f"{BACKEND_URL}/generate",

                json=payload,

                timeout=180
            )

        except requests.RequestException as exc:

            st.error(
                "Could not connect to FastAPI.\n\n"
                f"Error: {exc}"
            )

        else:

            if response.ok:

                data = response.json()

                st.session_state.document = (
                    data["text"]
                )

                st.session_state.generated_type = (
                    data["document_type"]
                )

                st.session_state.editing = False

                st.success(
                    "Document generated successfully!"
                )

            else:

                try:

                    detail = (
                        response
                        .json()
                        .get(
                            "detail",
                            response.text
                        )
                    )

                except Exception:

                    detail = response.text

                st.error(
                    f"Backend error: {detail}"
                )


# ============================================================
# DOCUMENT PREVIEW
# ============================================================

st.subheader(
    "Document Preview"
)


if not st.session_state.document:

    st.info(
        'Enter your document details '
        'in the sidebar and click '
        '"Generate Document".'
    )

else:

    left, right = st.columns(
        [1, 2]
    )

    with left:

        edit_button_text = (
            "Finish Editing"
            if st.session_state.editing
            else "Edit Document"
        )

        if st.button(
            edit_button_text,
            use_container_width=True
        ):

            st.session_state.editing = (
                not st.session_state.editing
            )

            st.rerun()

    with right:

        st.caption(
            "Document type: "
            + st.session_state.generated_type
        )


    # ========================================================
    # EDIT MODE
    # ========================================================

    if st.session_state.editing:

        edited_document = st.text_area(

            "Editable Document",

            value=st.session_state.document,

            height=600
        )

        st.session_state.document = (
            edited_document
        )


    # ========================================================
    # PREVIEW
    # ========================================================

    safe_text = html.escape(
        st.session_state.document
    )

    st.markdown(
        f'<div class="legal-card">'
        f'{safe_text}'
        f'</div>',

        unsafe_allow_html=True
    )


    # ========================================================
    # DOWNLOAD
    # ========================================================

    st.subheader(
        "Download"
    )

    export_params = {

        "document_type":
            st.session_state.generated_type,

        "text":
            st.session_state.document
    }


    # TXT
    try:

        txt_response = requests.post(
            f"{BACKEND_URL}/export/txt",
            params=export_params,
            timeout=60
        )

    except requests.RequestException:

        txt_response = None


    # DOCX
    try:

        docx_response = requests.post(
            f"{BACKEND_URL}/export/docx",
            params=export_params,
            timeout=60
        )

    except requests.RequestException:

        docx_response = None


    # PDF
    try:

        pdf_response = requests.post(
            f"{BACKEND_URL}/export/pdf",
            params=export_params,
            timeout=60
        )

    except requests.RequestException:

        pdf_response = None


    filename_base = (
        st.session_state
        .generated_type
        .lower()
        .replace(" ", "_")
        .replace("/", "_")
    )


    d1, d2, d3 = st.columns(3)


    # TXT
    with d1:

        if (
            txt_response
            and txt_response.ok
        ):

            st.download_button(

                "Download TXT",

                txt_response.content,

                f"{filename_base}.txt",

                "text/plain",

                use_container_width=True
            )

        else:

            st.error(
                "TXT export failed."
            )


    # DOCX
    with d2:

        if (
            docx_response
            and docx_response.ok
        ):

            st.download_button(

                "Download DOCX",

                docx_response.content,

                f"{filename_base}.docx",

                "application/"
                "vnd.openxmlformats-officedocument."
                "wordprocessingml.document",

                use_container_width=True
            )

        else:

            st.error(
                "DOCX export failed."
            )


    # PDF
    with d3:

        if (
            pdf_response
            and pdf_response.ok
        ):

            st.download_button(

                "Download PDF",

                pdf_response.content,

                f"{filename_base}.pdf",

                "application/pdf",

                use_container_width=True
            )

        else:

            st.error(
                "PDF export failed."
            )