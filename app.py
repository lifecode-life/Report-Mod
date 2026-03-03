from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import streamlit as st

from report_tool.audit import write_audit_json
from report_tool.extraction import ExtractionResult, extract_conditions_from_text
from report_tool.filtering import apply_filters
from report_tool.pdfgen import build_client_pdf

OUTPUTS_DIR = Path("outputs")


def parse_manual_json(manual_json_text: str) -> tuple[dict[str, list[str]], str | None]:
    try:
        parsed = json.loads(manual_json_text)
        if not isinstance(parsed, dict):
            return {}, "Manual condition editor must be a JSON object of {category: [conditions]}."

        cleaned: dict[str, list[str]] = {}
        for category, conditions in parsed.items():
            if isinstance(category, str) and isinstance(conditions, list):
                cleaned[category.strip()] = [str(c).strip() for c in conditions if str(c).strip()]
        return cleaned, None
    except json.JSONDecodeError as exc:
        return {}, f"Invalid JSON: {exc}"


def main() -> None:
    st.set_page_config(page_title="Lifecode PDF Filter Tool", layout="wide")
    st.title("Lifecode Internal Genetic Report Filter")

    counselor_name = st.text_input("Counselor name", value="")
    filter_profile_name = st.selectbox("Filter profile", ["PED_PARENT_SAFE_v1", "CUSTOM"])

    uploaded_file = st.file_uploader("Upload original report PDF", type=["pdf"])
    if not uploaded_file:
        st.info("Upload a PDF to begin.")
        return

    pdf_bytes = uploaded_file.getvalue()

    import pdfplumber
    import io

    text_parts = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            text_parts.append(page.extract_text() or "")
    extracted: ExtractionResult = extract_conditions_from_text("\n".join(text_parts))

    if extracted.uncertain:
        st.warning("Extraction uncertainty detected: " + " | ".join(extracted.warnings))

    default_editor_value = json.dumps(extracted.grouped_conditions, indent=2)
    manual_json = st.text_area(
        "Manual condition/category editor (JSON). You can correct, add, or remove detections before filtering.",
        value=default_editor_value,
        height=280,
    )

    manual_grouped, parse_error = parse_manual_json(manual_json)
    if parse_error:
        st.error(parse_error)
        return

    category_names = sorted(manual_grouped.keys())
    excluded_categories = st.multiselect("Exclude entire categories", options=category_names)

    st.subheader("Condition checklist by category")
    excluded_conditions: list[str] = []
    for category in category_names:
        with st.expander(category, expanded=True):
            if category in excluded_categories:
                st.caption("Category excluded.")
                continue
            for condition in manual_grouped[category]:
                keep = st.checkbox(
                    condition,
                    value=True,
                    key=f"keep::{category}::{condition}",
                )
                if not keep:
                    excluded_conditions.append(condition)

    filtered = apply_filters(manual_grouped, excluded_categories, excluded_conditions)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Detected categories", len(manual_grouped))
    with col2:
        st.metric("Conditions in client PDF", sum(len(v) for v in filtered.values()))

    if st.button("Generate outputs", type="primary"):
        run_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        OUTPUTS_DIR.mkdir(exist_ok=True, parents=True)

        # Internal copy (unfiltered) preserved.
        internal_pdf_path = OUTPUTS_DIR / f"internal_unfiltered_{run_id}.pdf"
        internal_pdf_path.write_bytes(pdf_bytes)

        client_pdf_path = OUTPUTS_DIR / f"client_filtered_{run_id}.pdf"
        build_client_pdf(
            output_path=client_pdf_path,
            grouped_conditions=filtered,
            counselor_name=counselor_name or "Unknown",
            original_filename=uploaded_file.name,
        )

        audit_path = OUTPUTS_DIR / f"audit_{run_id}.json"
        write_audit_json(
            output_path=audit_path,
            original_filename=uploaded_file.name,
            original_pdf_bytes=pdf_bytes,
            counselor_name=counselor_name,
            filter_profile_name=filter_profile_name,
            excluded_categories=excluded_categories,
            excluded_conditions=excluded_conditions,
        )

        st.success("Outputs generated.")
        st.write(f"Client PDF: `{client_pdf_path}`")
        st.write(f"Internal PDF: `{internal_pdf_path}`")
        st.write(f"Audit JSON: `{audit_path}`")


if __name__ == "__main__":
    main()
