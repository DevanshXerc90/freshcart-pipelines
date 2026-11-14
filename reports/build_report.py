"""Render assignment_report.md as a compact PDF without modifying its evidence."""

from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Flowable,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

REPORT_PATH = Path(__file__).with_name("assignment_report.md")
PDF_PATH = REPORT_PATH.with_name("RollNo_Name_Pipelines.pdf")


class ArchitectureDiagram(Flowable):
    """Draw a compact conceptual diagram for the report."""

    def __init__(self, width: float):
        super().__init__()
        self.width = width
        self.height = 92

    def draw(self):
        canvas = self.canv
        top_nodes = ["Git", "CI / pytest", "FreshCart ELT", "Snowflake gold", "Mage ML"]
        box_width = 76
        gap = (self.width - box_width * len(top_nodes)) / (len(top_nodes) - 1)
        top_y = 58

        def draw_box(x, y, label):
            canvas.setStrokeColor(colors.HexColor("#35566F"))
            canvas.setFillColor(colors.HexColor("#EDF3F7"))
            canvas.roundRect(x, y, box_width, 24, 3, stroke=1, fill=1)
            canvas.setFillColor(colors.HexColor("#182B3A"))
            canvas.setFont("Helvetica", 7.5)
            canvas.drawCentredString(x + box_width / 2, y + 9, label)

        def draw_arrow(x1, y1, x2, y2):
            canvas.setStrokeColor(colors.HexColor("#526B7C"))
            canvas.line(x1, y1, x2, y2)
            canvas.line(x2, y2, x2 - 4, y2 + 3)
            canvas.line(x2, y2, x2 - 4, y2 - 3)

        for index, label in enumerate(top_nodes):
            x = index * (box_width + gap)
            draw_box(x, top_y, label)
            if index < len(top_nodes) - 1:
                draw_arrow(x + box_width + 2, top_y + 12, x + box_width + gap - 3, top_y + 12)

        rabbit_x = self.width * 0.30
        driver_x = self.width * 0.64
        draw_box(rabbit_x, 8, "RabbitMQ events")
        draw_box(driver_x, 8, "Driver queues")
        draw_arrow(rabbit_x + box_width + 3, 20, driver_x - 4, 20)
        draw_arrow(rabbit_x + box_width / 2, 34, rabbit_x + box_width / 2, 56)
        canvas.setFont("Helvetica-Oblique", 6.5)
        canvas.setFillColor(colors.HexColor("#526B7C"))
        canvas.drawString(rabbit_x + box_width + 8, 24, "routes")


def _inline(text: str) -> str:
    escaped = html.escape(text, quote=False)
    escaped = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', escaped)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped)
    return escaped


def _table_rows(lines: list[str]) -> list[list[str]]:
    rows = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append([_inline(cell) for cell in cells])
    return rows


def build_pdf() -> Path:
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportTitle", parent=styles["Title"], alignment=TA_CENTER, textColor=colors.HexColor("#203F56"), fontSize=20, leading=24, spaceAfter=12))
    styles.add(ParagraphStyle(name="SectionHeading", parent=styles["Heading1"], textColor=colors.HexColor("#203F56"), fontSize=14, leading=17, spaceBefore=10, spaceAfter=5))
    styles.add(ParagraphStyle(name="SubHeading", parent=styles["Heading2"], textColor=colors.HexColor("#365F78"), fontSize=10.5, leading=13, spaceBefore=7, spaceAfter=4))
    styles.add(ParagraphStyle(name="BodyCompact", parent=styles["BodyText"], fontSize=8.3, leading=11, spaceAfter=5))
    styles.add(ParagraphStyle(name="BulletCompact", parent=styles["BodyCompact"], leftIndent=12, firstLineIndent=-8))
    styles.add(ParagraphStyle(name="TableText", parent=styles["BodyCompact"], fontSize=7.1, leading=9, spaceAfter=0))
    styles.add(ParagraphStyle(name="TableHeader", parent=styles["TableText"], textColor=colors.white, fontName="Helvetica-Bold"))

    document = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=15 * mm,
        bottomMargin=16 * mm,
        title="From Git to Gold - Assignment Report Draft",
        author="",
    )
    story = []
    lines = REPORT_PATH.read_text(encoding="utf-8").splitlines()
    index = 0
    code_lines = []
    in_code = False
    code_language = ""

    while index < len(lines):
        line = lines[index]
        if line.startswith("```"):
            if not in_code:
                in_code = True
                code_language = line[3:].strip()
                code_lines = []
            else:
                in_code = False
                if code_language == "mermaid":
                    story.append(ArchitectureDiagram(document.width))
                else:
                    story.append(Preformatted("\n".join(code_lines), ParagraphStyle("Code", fontName="Courier", fontSize=6.7, leading=8.4, backColor=colors.HexColor("#F3F5F6"), borderPadding=5)))
                story.append(Spacer(1, 4))
            index += 1
            continue
        if in_code:
            code_lines.append(line)
            index += 1
            continue
        if line.startswith("|"):
            table_lines = []
            while index < len(lines) and lines[index].startswith("|"):
                table_lines.append(lines[index])
                index += 1
            rows = _table_rows(table_lines)
            if rows:
                formatted = []
                for row_index, row in enumerate(rows):
                    style = styles["TableHeader"] if row_index == 0 else styles["TableText"]
                    formatted.append([Paragraph(cell, style) for cell in row])
                columns = max(len(row) for row in formatted)
                table = Table(formatted, colWidths=[document.width / columns] * columns, repeatRows=1, hAlign="LEFT")
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#35566F")),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B7C3CA")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]))
                story.extend([table, Spacer(1, 5)])
            continue
        if line.startswith("# "):
            story.append(Paragraph(_inline(line[2:]), styles["ReportTitle"]))
        elif line.startswith("## "):
            story.append(Paragraph(_inline(line[3:]), styles["SectionHeading"]))
        elif line.startswith("### "):
            story.append(Paragraph(_inline(line[4:]), styles["SubHeading"]))
        elif line.startswith("- "):
            story.append(Paragraph("&#8226; " + _inline(line[2:]), styles["BulletCompact"]))
        elif re.match(r"\d+\. ", line):
            story.append(Paragraph(_inline(line), styles["BulletCompact"]))
        elif line.strip() == "---":
            story.append(Spacer(1, 4))
        elif line.strip():
            story.append(Paragraph(_inline(line), styles["BodyCompact"]))
        index += 1

    def draw_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#667780"))
        canvas.drawString(16 * mm, 9 * mm, "From Git to Gold | Draft - service evidence pending")
        canvas.drawRightString(A4[0] - 16 * mm, 9 * mm, f"Page {doc.page}")
        canvas.restoreState()

    document.build(story, onFirstPage=draw_footer, onLaterPages=draw_footer)
    return PDF_PATH


if __name__ == "__main__":
    print(build_pdf())
