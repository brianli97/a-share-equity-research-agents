"""Render an A-share filing review PDF from a company-specific JSON file."""

import argparse
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Frame, PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle


NAVY = colors.HexColor("#102A43")
BLUE = colors.HexColor("#1976A3")
TEAL = colors.HexColor("#168C80")
AMBER = colors.HexColor("#D38B18")
RED = colors.HexColor("#B24B45")
INK = colors.HexColor("#243746")
MUTED = colors.HexColor("#667985")
PALE = colors.HexColor("#EDF5F6")
LINE = colors.HexColor("#CFDCE2")
WHITE = colors.white


def styles():
    sheets = getSampleStyleSheet()
    specs = {
        "T": dict(fontSize=27, leading=37, textColor=NAVY, spaceAfter=10),
        "Sub": dict(fontSize=12, leading=19, textColor=MUTED, spaceAfter=5),
        "H1": dict(fontSize=19, leading=27, textColor=NAVY, spaceAfter=10, keepWithNext=True),
        "H2": dict(fontSize=11.5, leading=17, textColor=BLUE, spaceBefore=8, spaceAfter=4, keepWithNext=True),
        "B": dict(fontSize=9, leading=13.8, textColor=INK, spaceAfter=5),
        "S": dict(fontSize=7.5, leading=10.8, textColor=MUTED, spaceAfter=3),
        "K": dict(fontSize=14, leading=18, textColor=NAVY, alignment=TA_CENTER),
        "KL": dict(fontSize=7.1, leading=10, textColor=MUTED, alignment=TA_CENTER),
        "Q": dict(fontSize=9.6, leading=15.5, textColor=NAVY, leftIndent=8, borderColor=TEAL,
                  borderWidth=2, borderPadding=7, spaceAfter=8),
    }
    for name, values in specs.items():
        sheets.add(ParagraphStyle(name=name, fontName="CN", **values))
    return sheets


def paragraph(text, style, sheets):
    return Paragraph(str(text), sheets[style])


def standard_table(block, sheets):
    widths = block["widths_mm"]
    if not widths or sum(widths) > 176:
        raise ValueError("Table widths must total no more than 176 mm")
    if not block["rows"] or any(len(row) != len(widths) for row in block["rows"]):
        raise ValueError("Every table row must match widths_mm")
    rows = [[paragraph(value, "S", sheets) for value in row] for row in block["rows"]]
    table = Table(rows, colWidths=[value * mm for value in widths], repeatRows=1,
                  hAlign="LEFT", splitByRow=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, colors.HexColor("#F4F7F8")]),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def kpis(block, sheets):
    items = block["items"]
    if not 1 <= len(items) <= 4:
        raise ValueError("KPI blocks require one to four items")
    width = 176 * mm / len(items)
    table = Table(
        [[paragraph(item["value"], "K", sheets) for item in items],
         [paragraph(item["label"], "KL", sheets) for item in items]],
        colWidths=[width] * len(items), rowHeights=[18 * mm, 10 * mm],
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE),
        ("GRID", (0, 0), (-1, -1), 0.5, WHITE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return table


def callout(block, sheets):
    palette = {"positive": TEAL, "warning": AMBER, "risk": RED}
    color = palette.get(block.get("tone", "positive"), TEAL)
    table = Table([[paragraph(block["title"], "H2", sheets), paragraph(block["text"], "B", sheets)]],
                  colWidths=[34 * mm, 142 * mm])
    table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.7, color),
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#F0F7F7")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


def render(data_path):
    data_path = Path(data_path).resolve()
    data = json.loads(data_path.read_text(encoding="utf-8"))
    required = {"title", "company", "code", "output", "pages"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"Missing report fields: {sorted(missing)}")
    if not data["pages"]:
        raise ValueError("Report must contain at least one page")

    font = Path(data.get("font", r"C:\Windows\Fonts\simhei.ttf"))
    if not font.exists():
        raise FileNotFoundError(f"Chinese font not found: {font}")
    pdfmetrics.registerFont(TTFont("CN", str(font)))
    sheets = styles()
    output = (data_path.parent / data["output"]).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    story = []
    for page_index, page in enumerate(data["pages"]):
        for block in page:
            kind = block["type"]
            if kind == "paragraph":
                story.append(paragraph(block["text"], block.get("style", "B"), sheets))
            elif kind == "spacer":
                story.append(Spacer(1, block["mm"] * mm))
            elif kind == "table":
                story.append(standard_table(block, sheets))
            elif kind == "kpis":
                story.append(kpis(block, sheets))
            elif kind == "callout":
                story.append(callout(block, sheets))
            else:
                raise ValueError(f"Unknown block type: {kind}")
        if page_index < len(data["pages"]) - 1:
            story.append(PageBreak())

    def header_footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(LINE)
        canvas.line(18 * mm, 18 * mm, 192 * mm, 18 * mm)
        canvas.setFont("CN", 7)
        canvas.setFillColor(MUTED)
        canvas.drawString(18 * mm, 12 * mm, data.get("footer", f'{data["company"]}（{data["code"]}）｜招股书与财报解读'))
        canvas.drawRightString(192 * mm, 12 * mm, str(doc.page))
        canvas.restoreState()

    doc = BaseDocTemplate(str(output), pagesize=A4, rightMargin=17 * mm, leftMargin=17 * mm,
                          topMargin=17 * mm, bottomMargin=23 * mm, title=data["title"], author="Codex")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="report", frames=[frame], onPage=header_footer)])
    doc.build(story)
    if not output.exists() or output.stat().st_size == 0:
        raise RuntimeError("PDF generation failed")
    print(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", help="Path to report_data.json")
    render(parser.parse_args().data)
