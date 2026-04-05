"""Generate a print-friendly PDF from ENGR6311 project markdown report.

This converter is intentionally lightweight and focused on the report format used
in this repository (headings, paragraphs, equation blocks, markdown tables,
bullet lists, and inline images).
"""

from __future__ import annotations

import io
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    HRFlowable,
    Image,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def image_with_max_width(image_path: Path, max_width: float) -> Image:
    """Create a reportlab Image preserving aspect ratio up to max_width."""
    reader = ImageReader(str(image_path))
    w_px, h_px = reader.getSize()
    scale = min(1.0, max_width / float(w_px))
    width = w_px * scale
    height = h_px * scale
    img = Image(str(image_path), width=width, height=height)
    img.hAlign = "CENTER"
    return img


def table_from_markdown(table_lines: list[str], body_style: ParagraphStyle, max_width: float) -> Table:
    """Parse a simple markdown table into a reportlab Table."""
    rows: list[list[str]] = []
    for raw in table_lines:
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        # Skip markdown separator row like |---|---:|
        if all(set(c).issubset({"-", ":"}) for c in cells):
            continue
        rows.append(cells)

    if not rows:
        return Table([[" "]])

    col_count = max(len(r) for r in rows)
    rows = [r + [""] * (col_count - len(r)) for r in rows]

    table_cell_style = ParagraphStyle("TableBody", parent=body_style, fontSize=9, leading=11)
    cell_paragraphs = [[Paragraph(format_inline_math(cell), table_cell_style) for cell in row] for row in rows]
    col_width = max_width / float(col_count)
    table = Table(cell_paragraphs, repeatRows=1, colWidths=[col_width] * col_count)
    table.setStyle(
        TableStyle(
            [
                # Pure black-and-white style for photocopy clarity.
                ("BACKGROUND", (0, 0), (-1, 0), colors.white),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.6),
                ("GRID", (0, 0), (-1, -1), 0.7, colors.black),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    return table


def latex_line_to_flowable(latex_line: str, max_width: float) -> Image:
    """Render one LaTeX/mathtext line to an Image flowable.

    This uses matplotlib mathtext so equations appear formally typeset in the PDF.
    """
    # Replace \tag{...} which mathtext does not support.
    cleaned = re.sub(r"\\tag\{[^}]*\}", "", latex_line).strip()
    fig = plt.figure(figsize=(8, 0.6), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()

    text_artist = ax.text(0.5, 0.5, f"${cleaned}$", ha="center", va="center", fontsize=10.5)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bbox = text_artist.get_window_extent(renderer=renderer).expanded(1.04, 1.25)
    bbox_inches = bbox.transformed(fig.dpi_scale_trans.inverted())

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=300, transparent=True, bbox_inches=bbox_inches, pad_inches=0.02)
    plt.close(fig)
    buffer.seek(0)

    reader = ImageReader(buffer)
    w_px, h_px = reader.getSize()
    max_height = 0.36 * inch
    scale = min(1.0, max_width / float(w_px), max_height / float(h_px))
    img = Image(buffer, width=w_px * scale, height=h_px * scale)
    img.hAlign = "CENTER"
    # Keep stream alive until PDF build completes.
    img._buffer_ref = buffer
    return img


def latex_inline_to_rl_markup(expr: str) -> str:
    """Convert limited inline LaTeX math to reportlab paragraph markup."""
    s = expr.strip()

    # Common LaTeX cleanup for inline symbols.
    s = s.replace(r"\left", "").replace(r"\right", "")
    s = s.replace(r"\,", " ")
    s = s.replace(r"\%", "%")
    s = s.replace(r"\times", "×")
    s = s.replace(r"\pm", "+/-")
    s = s.replace(r"\to", "to")
    s = s.replace(r"\max", "max")
    s = s.replace(r"\mathbb{E}", "E")
    s = s.replace(r"\mathbb{V}", "V")

    # Replace simple commands with plain scientific names to keep font consistent.
    replacements = {
        r"\omega": "omega",
        r"\Omega": "Omega",
        r"\delta": "delta",
        r"\sigma": "sigma",
        r"\tau": "tau",
        r"\Re": "Re",
    }
    for old, new in replacements.items():
        s = s.replace(old, new)

    # Remove style commands while preserving content.
    s = re.sub(r"\\mathbf\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\text\{([^}]*)\}", r"\1", s)

    # Convert fractions and roots to readable inline forms.
    while re.search(r"\\(?:d)?frac\{([^{}]+)\}\{([^{}]+)\}", s):
        s = re.sub(r"\\(?:d)?frac\{([^{}]+)\}\{([^{}]+)\}", r"(\1)/(\2)", s)
    while re.search(r"\\sqrt\{([^{}]+)\}", s):
        s = re.sub(r"\\sqrt\{([^{}]+)\}", r"sqrt(\1)", s)

    # Subscripts/superscripts to reportlab markup.
    s = re.sub(r"_\{([^}]+)\}", r"<sub>\1</sub>", s)
    s = re.sub(r"\^\{([^}]+)\}", r"<super>\1</super>", s)
    s = re.sub(r"_([A-Za-z0-9])", r"<sub>\1</sub>", s)
    s = re.sub(r"\^([A-Za-z0-9+-])", r"<super>\1</super>", s)

    return s


def format_inline_math(text: str) -> str:
    """Convert inline $...$ math spans into reportlab markup."""
    def repl(match: re.Match) -> str:
        return latex_inline_to_rl_markup(match.group(1))

    return re.sub(r"\$([^$]+)\$", repl, text)


def build_pdf_from_markdown(markdown_path: Path, output_pdf: Path) -> None:
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "TitleCustom",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        spaceAfter=10,
    )
    h2 = ParagraphStyle("H2Custom", parent=styles["Heading2"], fontSize=15, leading=18)
    h3 = ParagraphStyle("H3Custom", parent=styles["Heading3"], fontSize=12, leading=14)
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=10.3, leading=13)
    eq = ParagraphStyle("Eq", parent=styles["Code"], fontSize=9.5, leading=12)
    bullet = ParagraphStyle("Bullet", parent=body, leftIndent=14, firstLineIndent=-10)

    doc = SimpleDocTemplate(
        str(output_pdf),
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title="ENGR 6311 Project Report",
        author="Mukund Rajamony",
    )

    lines = markdown_path.read_text(encoding="utf-8").splitlines()
    story = []

    in_code = False
    in_equation = False
    equation_lines: list[str] = []
    code_lines: list[str] = []
    table_lines: list[str] = []

    def flush_table() -> None:
        nonlocal table_lines
        if table_lines:
            story.append(table_from_markdown(table_lines, body, max_width=6.7 * inch))
            story.append(Spacer(1, 0.08 * inch))
            table_lines = []

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        if stripped.startswith("|"):
            table_lines.append(line)
            continue
        flush_table()

        if stripped.startswith("```"):
            if not in_code:
                in_code = True
                code_lines = []
            else:
                in_code = False
                story.append(Preformatted("\n".join(code_lines), eq))
                story.append(Spacer(1, 0.08 * inch))
            continue

        if in_code:
            code_lines.append(line)
            continue

        if stripped == "$$":
            if not in_equation:
                in_equation = True
                equation_lines = []
                story.append(Spacer(1, 0.03 * inch))
            else:
                in_equation = False
                for eq_line in equation_lines:
                    if not eq_line.strip():
                        continue
                    try:
                        story.append(latex_line_to_flowable(eq_line.strip(), max_width=6.7 * inch))
                        story.append(Spacer(1, 0.015 * inch))
                    except Exception:
                        # Fallback for unsupported mathtext commands.
                        story.append(Preformatted(eq_line, eq))
                story.append(Spacer(1, 0.045 * inch))
            continue

        if in_equation:
            equation_lines.append(line)
            continue

        if not stripped:
            story.append(Spacer(1, 0.035 * inch))
            continue

        if stripped == "---":
            story.append(HRFlowable(width="100%", thickness=0.8, color=colors.lightgrey))
            story.append(Spacer(1, 0.1 * inch))
            continue

        image_match = re.match(r"!\[[^\]]*\]\(([^)]+)\)", stripped)
        if image_match:
            rel = image_match.group(1)
            image_path = (markdown_path.parent / rel).resolve()
            if image_path.exists():
                story.append(image_with_max_width(image_path, max_width=6.7 * inch))
                story.append(Spacer(1, 0.1 * inch))
            continue

        if stripped.startswith("# "):
            story.append(Paragraph(stripped[2:].strip(), title))
            continue
        if stripped.startswith("## "):
            story.append(Paragraph(stripped[3:].strip(), h2))
            continue
        if stripped.startswith("### "):
            story.append(Paragraph(stripped[4:].strip(), h3))
            continue

        if re.match(r"^\d+\.\s+", stripped):
            story.append(Paragraph(format_inline_math(stripped), body))
            continue

        if stripped.startswith("- "):
            story.append(Paragraph(format_inline_math(f"• {stripped[2:]}"), bullet))
            continue

        story.append(Paragraph(format_inline_math(stripped), body))

    flush_table()
    doc.build(story)


def main() -> None:
    base = Path(__file__).resolve().parent
    markdown_path = base / "ENGR6311_Project_Report.md"
    output_pdf = base / "ENGR6311_Project_Report.pdf"
    build_pdf_from_markdown(markdown_path, output_pdf)
    print(f"Saved: {output_pdf}")


if __name__ == "__main__":
    main()
