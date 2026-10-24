"""Render an A-share peer value-comparison PDF from report_data.json."""

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
from reportlab.platypus import BaseDocTemplate, Flowable, Frame, PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle


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
        "Lead": dict(fontSize=11, leading=18, textColor=NAVY, backColor=PALE,
                     borderColor=BLUE, borderWidth=0, borderPadding=9, leftIndent=2, spaceAfter=9),
        "Bul": dict(fontSize=9, leading=14, textColor=INK, leftIndent=12, firstLineIndent=-8, spaceAfter=4),
        "CardT": dict(fontSize=9.5, leading=13, textColor=NAVY, spaceAfter=3),
        "CardB": dict(fontSize=8.2, leading=12.5, textColor=INK),
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


def bullet_list(block, sheets):
    items = block.get("items", [])
    if not 1 <= len(items) <= 8:
        raise ValueError("Bullet blocks require one to eight items")
    return Table([[paragraph(f"· {item}", "Bul", sheets)] for item in items],
                 colWidths=[176 * mm], hAlign="LEFT",
                 style=[("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                        ("TOPPADDING", (0, 0), (-1, -1), 0),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 1)])


def cards(block, sheets):
    items = block.get("items", [])
    if not 1 <= len(items) <= 3:
        raise ValueError("Card blocks require one to three items")
    palette = {"positive": TEAL, "warning": AMBER, "risk": RED, "neutral": BLUE}
    cells = []
    for item in items:
        tone = palette.get(item.get("tone", "neutral"), BLUE)
        body = Table([[paragraph(item["title"], "CardT", sheets)],
                      [paragraph(item["text"], "CardB", sheets)]],
                     colWidths=[(170 / len(items)) * mm])
        body.setStyle(TableStyle([
            ("LINEABOVE", (0, 0), (-1, 0), 3, tone),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFB")),
            ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        cells.append(body)
    table = Table([cells], colWidths=[(176 / len(items)) * mm] * len(items), hAlign="LEFT")
    table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                               ("LEFTPADDING", (0, 0), (-1, -1), 2),
                               ("RIGHTPADDING", (0, 0), (-1, -1), 2)]))
    return table


class Bars(Flowable):
    def __init__(self, block):
        super().__init__()
        self.items = block.get("items", [])
        if not 1 <= len(self.items) <= 10:
            raise ValueError("Bar blocks require one to ten items")
        self.maximum = float(block.get("max_value") or max(float(i["value"]) for i in self.items) or 1)
        if self.maximum <= 0:
            raise ValueError("max_value must be positive")
        self.width = 176 * mm
        self.height = (10 + len(self.items) * 12) * mm

    def draw(self):
        palette = {"positive": TEAL, "warning": AMBER, "risk": RED, "neutral": BLUE}
        c = self.canv
        label_w, value_w = 38 * mm, 25 * mm
        bar_w = self.width - label_w - value_w - 5 * mm
        y = self.height - 9 * mm
        for item in self.items:
            value = float(item["value"])
            c.setFont("CN", 8)
            c.setFillColor(INK)
            c.drawString(0, y, str(item["label"])[:18])
            c.setFillColor(colors.HexColor("#E7EEF1"))
            c.roundRect(label_w, y - 1.5 * mm, bar_w, 5 * mm, 2 * mm, fill=1, stroke=0)
            fill_w = max(0, min(bar_w, bar_w * value / self.maximum))
            c.setFillColor(palette.get(item.get("tone", "neutral"), BLUE))
            c.roundRect(label_w, y - 1.5 * mm, fill_w, 5 * mm, 2 * mm, fill=1, stroke=0)
            c.setFillColor(NAVY)
            c.drawRightString(self.width, y, str(item.get("display", value)))
            y -= 12 * mm


def render(data_path):
    data_path = Path(data_path).resolve()
    data = json.loads(data_path.read_text(encoding="utf-8"))
    required = {"title", "topic", "as_of_date", "output", "pages"}
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
            elif kind == "lead":
                story.append(paragraph(block["text"], "Lead", sheets))
            elif kind == "bullets":
                story.append(bullet_list(block, sheets))
            elif kind == "cards":
                story.append(cards(block, sheets))
            elif kind == "bars":
                story.append(Bars(block))
            else:
                raise ValueError(f"Unknown block type: {kind}")
        if page_index < len(data["pages"]) - 1:
            story.append(PageBreak())

    def header_footer(canvas, doc):
        canvas.saveState()
        if doc.page == 1:
            canvas.setFillColor(NAVY)
            canvas.rect(0, 286 * mm, 210 * mm, 11 * mm, fill=1, stroke=0)
            canvas.setFillColor(TEAL)
            canvas.rect(0, 281 * mm, 62 * mm, 5 * mm, fill=1, stroke=0)
        canvas.setStrokeColor(LINE)
        canvas.line(18 * mm, 18 * mm, 192 * mm, 18 * mm)
        canvas.setFont("CN", 7)
        canvas.setFillColor(MUTED)
        canvas.drawString(18 * mm, 12 * mm, data.get("footer", f'{data["topic"]}｜同行价值比较｜{data["as_of_date"]}'))
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
