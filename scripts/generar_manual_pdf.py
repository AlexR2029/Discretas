"""Genera el manual PDF desde docs/manual_usuario.md usando ReportLab."""

from __future__ import annotations

import re
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "manual_usuario.md"
OUTPUT = ROOT / "docs" / "manual_usuario.pdf"


def inline_markup(text: str) -> str:
    """Convierte negrita y código inline a markup seguro para ReportLab."""
    parts = re.split(r"(`[^`]+`|\*\*[^*]+\*\*)", text)
    converted = []
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            converted.append(f"<b>{escape(part[2:-2])}</b>")
        elif part.startswith("`") and part.endswith("`"):
            converted.append(
                f'<font name="Courier" color="#1d4ed8">{escape(part[1:-1])}</font>'
            )
        else:
            converted.append(escape(part))
    return "".join(converted).replace("–", "-").replace("—", "-")


def build_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "ManualTitle", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=25, leading=31, textColor=colors.HexColor("#172554"),
            alignment=TA_CENTER, spaceAfter=9 * mm,
        ),
        "h1": ParagraphStyle(
            "ManualH1", parent=base["Heading1"], fontName="Helvetica-Bold",
            fontSize=17, leading=21, textColor=colors.HexColor("#1d4ed8"),
            spaceBefore=5 * mm, spaceAfter=3 * mm, keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "ManualH2", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=12, leading=15, textColor=colors.HexColor("#172554"),
            spaceBefore=3 * mm, spaceAfter=2 * mm, keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "ManualBody", parent=base["BodyText"], fontName="Helvetica",
            fontSize=9.4, leading=14, textColor=colors.HexColor("#263449"),
            spaceAfter=2.5 * mm,
        ),
        "bullet": ParagraphStyle(
            "ManualBullet", parent=base["BodyText"], fontName="Helvetica",
            fontSize=9.2, leading=13.5, textColor=colors.HexColor("#263449"),
            spaceAfter=1.5 * mm,
        ),
        "code": ParagraphStyle(
            "ManualCode", parent=base["Code"], fontName="Courier",
            fontSize=8.2, leading=11, textColor=colors.HexColor("#15345b"),
            backColor=colors.HexColor("#eef4fb"), borderColor=colors.HexColor("#d7e3f4"),
            borderWidth=0.5, borderPadding=7, leftIndent=5, rightIndent=5,
            spaceBefore=2 * mm, spaceAfter=3 * mm,
        ),
    }


def markdown_to_story(markdown: str):
    styles = build_styles()
    lines = markdown.splitlines()
    story = []
    paragraph_lines = []
    index = 0
    first_heading = True

    def flush_paragraph():
        if paragraph_lines:
            content = " ".join(line.strip() for line in paragraph_lines)
            story.append(Paragraph(inline_markup(content), styles["body"]))
            paragraph_lines.clear()

    while index < len(lines):
        line = lines[index].strip()
        if not line:
            flush_paragraph()
            index += 1
            continue
        if line.startswith("```"):
            flush_paragraph()
            code_lines = []
            index += 1
            while index < len(lines) and not lines[index].strip().startswith("```"):
                code_lines.append(lines[index].replace("–", "-").replace("—", "-"))
                index += 1
            story.append(Preformatted("\n".join(code_lines), styles["code"]))
            index += 1
            continue
        if line == "---":
            flush_paragraph()
            story.append(HRFlowable(width="100%", thickness=0.8,
                                    color=colors.HexColor("#d8e1ee"),
                                    spaceBefore=2 * mm, spaceAfter=3 * mm))
            index += 1
            continue
        if line.startswith("# "):
            flush_paragraph()
            if first_heading:
                story.append(Spacer(1, 28 * mm))
                story.append(Paragraph(inline_markup(line[2:]), styles["title"]))
                story.append(HRFlowable(width="35%", thickness=2,
                                        color=colors.HexColor("#2563eb"),
                                        hAlign="CENTER", spaceAfter=8 * mm))
                first_heading = False
            else:
                story.append(Paragraph(inline_markup(line[2:]), styles["h1"]))
            index += 1
            continue
        if line.startswith("## "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(line[3:]), styles["h1"]))
            index += 1
            continue
        if line.startswith("### "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(line[4:]), styles["h2"]))
            index += 1
            continue
        if line.startswith("| "):
            flush_paragraph()
            table_lines = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index].strip())
                index += 1
            data = []
            for table_line in table_lines:
                cells = [cell.strip() for cell in table_line.strip("|").split("|")]
                if cells and all(re.fullmatch(r":?-{2,}:?", cell) for cell in cells):
                    continue
                data.append([Paragraph(inline_markup(cell), styles["bullet"]) for cell in cells])
            if data:
                table = Table(data, repeatRows=1, hAlign="LEFT")
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e7edf6")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#172554")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d8e1ee")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                     [colors.white, colors.HexColor("#f7f9fc")]),
                ]))
                story.append(table)
                story.append(Spacer(1, 3 * mm))
            continue
        if line.startswith("- "):
            flush_paragraph()
            bullet_lines = []
            while index < len(lines) and lines[index].strip().startswith("- "):
                bullet_lines.append(lines[index].strip()[2:])
                index += 1
            story.append(ListFlowable(
                [ListItem(Paragraph(inline_markup(item), styles["bullet"]),
                          leftIndent=4 * mm) for item in bullet_lines],
                bulletType="bullet", start="circle", leftIndent=6 * mm,
                bulletFontName="Helvetica", bulletFontSize=6,
                bulletColor=colors.HexColor("#2563eb"),
            ))
            story.append(Spacer(1, 1.5 * mm))
            continue
        if re.match(r"^\d+\.\s", line):
            flush_paragraph()
            list_lines = []
            while index < len(lines) and re.match(r"^\d+\.\s", lines[index].strip()):
                item = re.sub(r"^\d+\.\s", "", lines[index].strip())
                index += 1
                while index < len(lines):
                    continuation = lines[index].strip()
                    if (not continuation or continuation.startswith(("#", "```", "|", "- "))
                            or re.match(r"^\d+\.\s", continuation)):
                        break
                    item += " " + continuation
                    index += 1
                list_lines.append(item)
            story.append(ListFlowable(
                [ListItem(Paragraph(inline_markup(item), styles["bullet"]),
                          leftIndent=4 * mm) for item in list_lines],
                bulletType="1", leftIndent=7 * mm,
                bulletFontName="Helvetica-Bold", bulletFontSize=8,
                bulletColor=colors.HexColor("#2563eb"),
            ))
            story.append(Spacer(1, 1.5 * mm))
            continue
        paragraph_lines.append(line)
        index += 1

    flush_paragraph()
    return story


def draw_page(canvas, document):
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(colors.HexColor("#172554"))
    canvas.rect(0, height - 9 * mm, width, 9 * mm, fill=1, stroke=0)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawString(18 * mm, 12 * mm, "Manual de usuario - Normalizador de Esquemas")
    canvas.drawRightString(width - 18 * mm, 12 * mm, f"Página {document.page}")
    canvas.restoreState()


def main():
    if not SOURCE.is_file():
        raise FileNotFoundError(f"No se encuentra el manual fuente: {SOURCE}")
    markdown = SOURCE.read_text(encoding="utf-8").replace("→", "->")
    document = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4,
        rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=17 * mm, bottomMargin=20 * mm,
        title="Manual de usuario - Normalizador de Esquemas",
        author="Equipo del proyecto",
    )
    document.build(markdown_to_story(markdown), onFirstPage=draw_page,
                   onLaterPages=draw_page)
    print(OUTPUT)


if __name__ == "__main__":
    main()
