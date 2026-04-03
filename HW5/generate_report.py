"""
Generate PDF report for ENGR 6311 Homework 4.

This script expects that HW4/hw4_solution.py has already been executed so that:
- HW4/figures/*.png
- HW4/results_summary.txt
are available.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def read_summary(summary_path: Path) -> dict:
    """Read key=value pairs from summary file."""
    values = {}
    if not summary_path.exists():
        return values

    for line in summary_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("["):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            values[k.strip()] = v.strip()
    return values


def build_report() -> Path:
    base_dir = Path(__file__).resolve().parent
    figure_dir = base_dir / "figures"
    summary_data = read_summary(base_dir / "results_summary.txt")

    output_file = base_dir / "ENGR6311_HW4_Report.pdf"
    doc = SimpleDocTemplate(
        str(output_file),
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleCustom",
        parent=styles["Heading1"],
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        fontSize=20,
        textColor=colors.HexColor("#16324f"),
        spaceAfter=12,
    )
    h1 = ParagraphStyle(
        "H1Custom",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=14,
        textColor=colors.HexColor("#1f4e79"),
        spaceBefore=10,
        spaceAfter=8,
    )
    h2 = ParagraphStyle(
        "H2Custom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=colors.HexColor("#2d5d7b"),
        spaceBefore=8,
        spaceAfter=6,
    )
    body = ParagraphStyle(
        "BodyCustom",
        parent=styles["Normal"],
        fontSize=10,
        leading=13,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
    )
    center = ParagraphStyle(
        "CenterCustom",
        parent=body,
        alignment=TA_CENTER,
    )

    story = []

    # Title page
    story.append(Spacer(1, 1.4 * inch))
    story.append(Paragraph("ENGR 6311: Vibrations in Machines and Structures", title_style))
    story.append(Paragraph("Homework 4", title_style))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("Detailed Analytical and Computational Solution", h1))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", center))
    story.append(Paragraph("Concordia University", center))
    story.append(Paragraph("Prepared by: Mukund Rajamony", center))

    story.append(PageBreak())

    # Problem statement
    story.append(Paragraph("Problem Statement", h1))
    story.append(
        Paragraph(
            "Part I asks for the modal equations of a uniform string fixed at both ends, "
            "with a linear viscous damper attached at an arbitrary point x_d along the string. "
            "Part II asks for a single-mode approximation of a pinned-pinned beam subjected "
            "to a harmonic point load at midspan, including the first nonlinear curvature term "
            "for finite but small rotations.",
            body,
        )
    )

    # Part I derivation
    story.append(Paragraph("Part I: String with Localized Viscous Damping", h1))
    story.append(
        Paragraph(
            "The governing PDE is:",
            body,
        )
    )
    story.append(Paragraph("rhoA y_tt + c_d delta(x-x_d) y_t - T y_xx = 0", center))
    story.append(
        Paragraph(
            "with boundary conditions y(0,t)=0 and y(L,t)=0. Using a modal expansion "
            "y(x,t)=sum(q_n(t) sin(n*pi*x/L)), and Galerkin projection yields:",
            body,
        )
    )
    story.append(Paragraph("M q_ddot + C q_dot + K q = 0", center))
    story.append(
        Paragraph(
            "where M=(rhoA*L/2)I, K_nn=T*n^2*pi^2/(2L), and C_mn=c_d sin(m*pi*x_d/L) sin(n*pi*x_d/L). "
            "The damping matrix is full (modal coupling) and rank-1 because one physical damper is used.",
            body,
        )
    )

    # Part I table with key values
    part1_table_data = [
        ["Quantity", "Value"],
        ["L", summary_data.get("L", "1.2")],
        ["tension", summary_data.get("tension", "120")],
        ["rhoA", summary_data.get("rhoA", "0.08")],
        ["c_d", summary_data.get("c_d", "0.35")],
        ["x_d", summary_data.get("x_d", "0.37")],
        ["omega_1", summary_data.get("omega_1", "N/A")],
    ]
    t1 = Table(part1_table_data, colWidths=[2.5 * inch, 2.5 * inch])
    t1.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.8, colors.black),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#edf4fb")),
            ]
        )
    )
    story.append(t1)
    story.append(Spacer(1, 0.12 * inch))

    fig1 = figure_dir / "part1_modal_damping_matrix.png"
    if fig1.exists():
        story.append(Image(str(fig1), width=5.4 * inch, height=4.0 * inch))
        story.append(Paragraph("Figure 1. Mass-normalized modal damping matrix", center))

    story.append(PageBreak())

    # Part II derivation
    story.append(Paragraph("Part II: Pinned-Pinned Beam, Single-Mode Nonlinear Model", h1))
    story.append(
        Paragraph(
            "For a pinned-pinned beam, use y(x,t)=q(t) sin(pi x/L). The curvature is approximated by "
            "kappa=y_xx/(1+y_x^2)^(3/2) ~ y_xx (1 - 1.5 y_x^2). Retaining the first nonlinear term "
            "and applying a single-mode Galerkin projection gives:",
            body,
        )
    )
    story.append(Paragraph("M q_ddot + C q_dot + K q - K3 q^3 = P cos(Omega t)", center))
    story.append(
        Paragraph(
            "with M=rhoA*L/2, K=EI*pi^4/(2L^3), K3=(3/4)EI*pi^6/L^5, and P=F0 at midspan. "
            "Because the cubic term appears with a negative sign in stiffness form, the model is softening.",
            body,
        )
    )

    part2_table_data = [
        ["Coefficient", "Value"],
        ["M", summary_data.get("M", "N/A")],
        ["C", summary_data.get("C", "N/A")],
        ["K", summary_data.get("K", "N/A")],
        ["K3", summary_data.get("K3", "N/A")],
        ["omega1", summary_data.get("omega1", "N/A")],
        ["beta=K3/M", summary_data.get("beta", "N/A")],
    ]
    t2 = Table(part2_table_data, colWidths=[2.5 * inch, 2.5 * inch])
    t2.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.8, colors.black),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#edf4fb")),
            ]
        )
    )
    story.append(t2)
    story.append(Spacer(1, 0.12 * inch))

    story.append(
        Paragraph(
            "Computed peak generalized amplitudes from the time simulation: "
            f"linear={summary_data.get('linear_peak_q', 'N/A')}, "
            f"nonlinear={summary_data.get('nonlinear_peak_q', 'N/A')}. "
            "The nonlinear response departs from the linear model as amplitude grows.",
            body,
        )
    )

    fig2 = figure_dir / "part2_time_history.png"
    if fig2.exists():
        story.append(Image(str(fig2), width=5.7 * inch, height=2.8 * inch))
        story.append(Paragraph("Figure 2. Linear vs nonlinear generalized displacement", center))

    fig3 = figure_dir / "part2_phase_portrait.png"
    if fig3.exists():
        story.append(Spacer(1, 0.08 * inch))
        story.append(Image(str(fig3), width=4.5 * inch, height=3.8 * inch))
        story.append(Paragraph("Figure 3. Late-time phase portrait", center))

    story.append(Spacer(1, 0.14 * inch))
    story.append(Paragraph("Conclusions", h1))
    story.append(
        Paragraph(
            "1) A point viscous damper on a fixed-fixed string introduces intermodal damping coupling, even though "
            "the undamped modes are orthogonal. 2) The pinned-pinned beam reduced to one mode produces a forced "
            "Duffing-type ODE with a softening cubic term when the first nonlinear curvature correction is kept. "
            "3) Numerical simulation confirms measurable divergence between linear and nonlinear responses near resonance.",
            body,
        )
    )

    doc.build(story)
    return output_file


def main() -> None:
    report_path = build_report()
    print(f"Report generated: {report_path}")


if __name__ == "__main__":
    main()
