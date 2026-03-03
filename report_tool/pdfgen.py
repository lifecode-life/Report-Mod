from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

DISCLAIMER = (
    "This content is for educational and lifestyle awareness only. "
    "Reports are not diagnostic tools. Always consult a qualified medical "
    "professional before making health decisions."
)


def _header(canvas, doc):
    canvas.saveState()
    w, h = LETTER
    canvas.setFillColor(colors.HexColor("#1B4D89"))
    canvas.rect(0, h - 0.9 * inch, w, 0.9 * inch, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawString(0.7 * inch, h - 0.55 * inch, "Lifecode Genetic Insights")
    canvas.setFont("Helvetica", 9)
    canvas.drawString(0.7 * inch, h - 0.75 * inch, f"Generated: {datetime.utcnow().isoformat()}Z")

    canvas.setFillColor(colors.black)
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(w - 0.7 * inch, 0.45 * inch, f"Page {doc.page}")
    canvas.setFont("Helvetica-Oblique", 8)
    canvas.drawString(0.7 * inch, 0.45 * inch, DISCLAIMER)
    canvas.restoreState()


def build_client_pdf(
    output_path: Path,
    grouped_conditions: Dict[str, List[str]],
    counselor_name: str,
    original_filename: str,
):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=LETTER,
        topMargin=1.1 * inch,
        bottomMargin=0.9 * inch,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
    )
    styles = getSampleStyleSheet()
    heading = styles["Heading2"]
    body = styles["BodyText"]
    body.spaceAfter = 5
    meta = ParagraphStyle("meta", parent=styles["BodyText"], textColor=colors.HexColor("#444444"))

    story = [
        Paragraph("Client-Facing Filtered Report", styles["Title"]),
        Paragraph(f"Counselor: {counselor_name}", meta),
        Paragraph(f"Source file: {original_filename}", meta),
        Spacer(1, 0.2 * inch),
    ]

    for category in sorted(grouped_conditions.keys()):
        conditions = grouped_conditions[category]
        story.append(Paragraph(category, heading))
        data = [["Condition"]] + [[c] for c in conditions]
        table = Table(data, colWidths=[6.8 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEF3FB")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1B4D89")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 0.12 * inch))

    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("Disclaimer", heading))
    story.append(Paragraph(DISCLAIMER, body))

    doc.build(story, onFirstPage=_header, onLaterPages=_header)
