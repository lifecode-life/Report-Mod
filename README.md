# Lifecode PDF Filter Tool

Streamlit internal tool to convert an original genetic report PDF into:
- a **client-facing filtered PDF** (clean, formatted), and
- an **internal unfiltered PDF** copy.

It also creates an audit JSON for traceability.

## Features

- Upload source PDF.
- Extracts candidate categories/conditions via `pdfplumber` text extraction.
- Shows conditions in category-grouped checklist.
- Exclude whole categories or individual conditions.
- Manual JSON editor to fix uncertain extraction.
- Generates:
  - `outputs/client_filtered_<runid>.pdf`
  - `outputs/internal_unfiltered_<runid>.pdf`
  - `outputs/audit_<runid>.json`
- Client PDF includes Lifecode-style header, page numbers, and required disclaimer on every page.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

Open the displayed local URL and use the UI.

## Testing

```bash
pytest -q
```

## Notes on robustness

Extraction uses permissive patterns for bullets, numbered lines, and category headers (e.g., `CATEGORY: ...`, uppercase headings). If extraction seems incomplete or uncertain, a warning is shown and the user can manually edit detected categories/conditions in JSON before generating outputs.
