"""
Generate PDF Report for ENGR 6311 Assignment 3
This script creates a comprehensive PDF report with all results and figures.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib import colors
from datetime import datetime
import os


def add_page_decorations(canvas, doc):
    """Draw line numbers on left margin and page number in footer."""
    canvas.saveState()

    # Line numbers (visual ruler) in left margin
    canvas.setFont('Helvetica', 6)
    canvas.setFillColor(colors.grey)
    line_spacing = 14
    usable_height = doc.height
    total_lines = int(usable_height // line_spacing)
    x_pos = doc.leftMargin - 18
    y_top = doc.bottomMargin + usable_height

    for i in range(total_lines):
        line_no = i + 1
        y = y_top - (i * line_spacing)
        canvas.drawRightString(x_pos, y, str(line_no))

    # Footer page number
    canvas.setFont('Helvetica', 9)
    canvas.setFillColor(colors.black)
    footer_text = f"Page {canvas.getPageNumber()}"
    canvas.drawCentredString(letter[0] / 2.0, 0.45 * inch, footer_text)

    canvas.restoreState()

def create_report():
    """Generate the PDF report."""
    
    # Create PDF document
    filename = "ENGR6311_Assignment3_Report.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter,
                           rightMargin=0.75*inch, leftMargin=0.75*inch,
                           topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    # Container for story
    story = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2e5894'),
        spaceAfter=10,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        leading=12,
        spaceAfter=6
    )
    
    # Title page
    story.append(Spacer(1, 1.5*inch))
    story.append(Paragraph("ENGR 6311: Vibrations in Machines and Structures", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Assignment 3", title_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("Lateral Vibrations of a String Loaded with Masses", heading1_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", 
                          ParagraphStyle('date', parent=normal_style, alignment=TA_CENTER)))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Concordia University", 
                          ParagraphStyle('uni', parent=normal_style, alignment=TA_CENTER, fontSize=12)))
    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph("Prepared by: Mukund Rajamony",
                          ParagraphStyle('author', parent=normal_style, alignment=TA_CENTER, fontSize=12, fontName='Helvetica-Bold')))
    
    story.append(PageBreak())
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", heading1_style))
    story.append(Paragraph(
        "This report presents a comprehensive analysis of lateral vibrations in a string loaded with N discrete masses. "
        "The system consists of masses attached to a taut string with one end fixed and the other end guided vertically. "
        "The analysis covers derivation of governing equations, free vibration analysis including mode shapes and natural "
        "frequencies, and forced vibration response with damping.",
        normal_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Problem Statement
    story.append(Paragraph("Problem Statement", heading1_style))
    story.append(Paragraph(
        "A string is loaded with N different masses m<sub>i</sub> at intervals L<sub>i</sub>. The left end is fixed "
        "to a wall, and the right end is secured in a vertical guide. A uniform tension T acts throughout the string. "
        "The vertical displacement of the i-th mass is denoted by u<sub>i</sub>(t). External forces f<sub>i</sub>(t) "
        "act on each mass. The string mass is negligible compared to attached masses.",
        normal_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # System Parameters
    story.append(Paragraph("System Parameters", heading2_style))
    params_data = [
        ['Parameter', 'Value', 'Units'],
        ['Mass (m)', '20', 'g'],
        ['Tension (T)', '100', 'N'],
        ['Interval Length (L)', '10', 'cm'],
        ['Damping Coefficient (α)', '0.001', '-']
    ]
    
    params_table = Table(params_data, colWidths=[2.5*inch, 1.5*inch, 1*inch])
    params_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(params_table)
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Spacer(1, 0.15*inch))
    
    # PART I
    story.append(Paragraph("PART I: Governing Equations", heading1_style))
    story.append(Paragraph(
        "The governing equations for the system are derived in matrix form as:",
        normal_style
    ))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "<b>M</b>ü + <b>K</b>u = <b>f</b>",
        ParagraphStyle('eq', parent=normal_style, alignment=TA_CENTER, fontSize=14)
    ))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "where <b>M</b> is the mass matrix (diagonal), <b>K</b> is the stiffness matrix (tridiagonal), "
        "<b>u</b> is the displacement vector, and <b>f</b> is the force vector.",
        normal_style
    ))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "<b>Mass Matrix:</b> M[i,i] = m<sub>i</sub> (diagonal elements)",
        normal_style
    ))
    story.append(Paragraph(
        "<b>Stiffness Matrix:</b> K[i,i] = T/L<sub>i</sub> + T/L<sub>i+1</sub> (main diagonal), "
        "K[i,i+1] = K[i+1,i] = -T/L<sub>i+1</sub> (off-diagonal)",
        normal_style
    ))
    
    story.append(PageBreak())
    
    # PART II
    story.append(Paragraph("PART II: Free Vibration Analysis", heading1_style))
    
    # Problem 1
    story.append(Paragraph("Problem 1: Mode Shapes (N=4, Equal Intervals)", heading2_style))
    story.append(Paragraph(
        "For a system with 4 masses at equal intervals of 10 cm, the natural frequencies are:",
        normal_style
    ))
    
    freq_data = [
        ['Mode', 'Natural Frequency (Hz)'],
        ['1', '12.36'],
        ['2', '35.59'],
        ['3', '54.52'],
        ['4', '66.88']
    ]
    freq_table = Table(freq_data, colWidths=[1.5*inch, 2.5*inch])
    freq_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5894')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue)
    ]))
    story.append(freq_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Add mode shapes figure
    if os.path.exists('HW3_Part2_Problem1_ModeShapes.png'):
        img = Image('HW3_Part2_Problem1_ModeShapes.png', width=5.8*inch, height=2.9*inch)
        story.append(img)
        story.append(Paragraph("<i>Figure 1: Mode shapes for N=4 with equal intervals</i>", 
                              ParagraphStyle('caption', parent=normal_style, alignment=TA_CENTER, fontSize=9)))
    story.append(Spacer(1, 0.1*inch))
    
    # Problem 2
    story.append(Paragraph("Problem 2: Zero Crossings", heading2_style))
    story.append(Paragraph(
        "The number of zero crossings (sign changes) for each mode shape follows the pattern: "
        "Mode 1 has 0 crossings, Mode 2 has 1 crossing, Mode 3 has 2 crossings, and Mode 4 has 3 crossings. "
        "This demonstrates the fundamental property that the number of zero crossings equals (mode number - 1).",
        normal_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    if os.path.exists('HW3_Part2_Problem2_ZeroCrossings.png'):
        img = Image('HW3_Part2_Problem2_ZeroCrossings.png', width=5.8*inch, height=2.5*inch)
        story.append(img)
        story.append(Paragraph("<i>Figure 2: Zero crossings analysis</i>", 
                              ParagraphStyle('caption', parent=normal_style, alignment=TA_CENTER, fontSize=9)))
    story.append(Spacer(1, 0.12*inch))
    
    # Problem 3
    story.append(Paragraph("Problem 3: First Natural Frequency vs N", heading2_style))
    story.append(Paragraph(
        "As the number of masses increases, the first natural frequency decreases. This occurs because adding "
        "more masses increases the total system mass while maintaining the same tension, effectively reducing "
        "the frequency of the fundamental mode.",
        normal_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    if os.path.exists('HW3_Part2_Problem3_FirstFreq.png'):
        img = Image('HW3_Part2_Problem3_FirstFreq.png', width=5.0*inch, height=2.4*inch)
        story.append(img)
        story.append(Paragraph("<i>Figure 3: First natural frequency as function of N</i>", 
                              ParagraphStyle('caption', parent=normal_style, alignment=TA_CENTER, fontSize=9)))
    story.append(Spacer(1, 0.12*inch))
    
    # Problem 4
    story.append(Paragraph("Problem 4: Last Natural Frequency vs N", heading2_style))
    story.append(Paragraph(
        "The highest natural frequency increases with N, approaching an asymptotic limit. This represents "
        "the shortest wavelength mode that can be supported by the discrete mass system.",
        normal_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    if os.path.exists('HW3_Part2_Problem4_LastFreq.png'):
        img = Image('HW3_Part2_Problem4_LastFreq.png', width=5.0*inch, height=2.4*inch)
        story.append(img)
        story.append(Paragraph("<i>Figure 4: Last natural frequency as function of N</i>", 
                              ParagraphStyle('caption', parent=normal_style, alignment=TA_CENTER, fontSize=9)))
    story.append(Spacer(1, 0.12*inch))
    
    # Problem 5
    story.append(Paragraph("Problem 5: Asymptotic Behavior", heading2_style))
    story.append(Paragraph(
        "As N approaches infinity, the first natural frequency converges to a minimum value (approximately 2.59 Hz), "
        "representing the fundamental mode of a continuous string. The last frequency continues to increase, "
        "limited by the discrete spacing between masses.",
        normal_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    if os.path.exists('HW3_Part2_Problem5_AsymptoticBehavior.png'):
        img = Image('HW3_Part2_Problem5_AsymptoticBehavior.png', width=5.8*inch, height=2.5*inch)
        story.append(img)
        story.append(Paragraph("<i>Figure 5: Asymptotic behavior of natural frequencies</i>", 
                              ParagraphStyle('caption', parent=normal_style, alignment=TA_CENTER, fontSize=9)))
    story.append(Spacer(1, 0.12*inch))
    
    # Problem 6
    story.append(Paragraph("Problem 6: Effect of Mass Variation", heading2_style))
    story.append(Paragraph(
        "When the second mass is doubled (r=2), all natural frequencies decrease. The reduction is most significant "
        "for modes with large displacement at the second mass location. This demonstrates the coupling between "
        "mass distribution and modal characteristics.",
        normal_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    if os.path.exists('HW3_Part2_Problem6_MassVariation.png'):
        img = Image('HW3_Part2_Problem6_MassVariation.png', width=5.8*inch, height=2.5*inch)
        story.append(img)
        story.append(Paragraph("<i>Figure 6: Effect of doubling mass 2 on natural frequencies</i>", 
                              ParagraphStyle('caption', parent=normal_style, alignment=TA_CENTER, fontSize=9)))
    story.append(Spacer(1, 0.12*inch))
    
    # Problem 7
    story.append(Paragraph("Problem 7: Mass Ratio Effects", heading2_style))
    story.append(Paragraph(
        "As the mass ratio r increases, all natural frequencies decrease following approximately a 1/√r relationship. "
        "This scaling law is consistent with lumped parameter vibration theory and demonstrates how localized mass "
        "changes affect global system dynamics.",
        normal_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    if os.path.exists('HW3_Part2_Problem7_MassRatio.png'):
        img = Image('HW3_Part2_Problem7_MassRatio.png', width=5.0*inch, height=2.4*inch)
        story.append(img)
        story.append(Paragraph("<i>Figure 7: Natural frequencies vs mass ratio</i>", 
                              ParagraphStyle('caption', parent=normal_style, alignment=TA_CENTER, fontSize=9)))
    story.append(PageBreak())
    
    # PART III
    story.append(Paragraph("PART III: Forced Vibration with Damping", heading1_style))
    story.append(Paragraph(
        "This section analyzes the forced response of the system with mass-proportional damping (α = 0.001) "
        "under harmonic excitation.",
        normal_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Problem 1
    story.append(Paragraph("Problem 1: Resonance at 4th Mode", heading2_style))
    story.append(Paragraph(
        "When the system is excited at the fourth natural frequency with force F = [1, 1, 0, -1]<sup>T</sup>, "
        "the response is dominated by the fourth mode shape. The steady-state amplitude is proportional to the "
        "mode shape, demonstrating resonance amplification with damping limiting the response.",
        normal_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    if os.path.exists('HW3_Part3_Problem1_Resonance.png'):
        img = Image('HW3_Part3_Problem1_Resonance.png', width=5.8*inch, height=2.5*inch)
        story.append(img)
        story.append(Paragraph("<i>Figure 8: Resonance response at fourth mode</i>", 
                              ParagraphStyle('caption', parent=normal_style, alignment=TA_CENTER, fontSize=9)))
    story.append(Spacer(1, 0.12*inch))
    
    # Problem 2
    story.append(Paragraph("Problem 2: Mode Shape Analysis", heading2_style))
    story.append(Paragraph(
        "For point force at mass 3, the response at each natural frequency is dominated by the corresponding mode. "
        "The amplitude pattern matches the mode shape, scaled by the modal participation factor. Phase relationships "
        "show that components are either in phase or 180° out of phase, following the mode shape sign pattern.",
        normal_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    if os.path.exists('HW3_Part3_Problem2_ModeAnalysis.png'):
        img = Image('HW3_Part3_Problem2_ModeAnalysis.png', width=5.8*inch, height=3.8*inch)
        story.append(img)
        story.append(Paragraph("<i>Figure 9: Mode shape analysis at different frequencies</i>", 
                              ParagraphStyle('caption', parent=normal_style, alignment=TA_CENTER, fontSize=9)))
    story.append(Spacer(1, 0.12*inch))
    
    # Problem 3
    story.append(Paragraph("Problem 3: Frequency Response (Point Force)", heading2_style))
    story.append(Paragraph(
        "The frequency response shows sharp peaks at all natural frequencies. Peak heights vary depending on "
        "modal participation - modes with significant displacement at the forcing location show larger amplitudes. "
        "Damping prevents infinite response at resonance.",
        normal_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    if os.path.exists('HW3_Part3_Problem3_FreqResponse.png'):
        img = Image('HW3_Part3_Problem3_FreqResponse.png', width=5.6*inch, height=3.1*inch)
        story.append(img)
        story.append(Paragraph("<i>Figure 10: Frequency response with force at mass 3</i>", 
                              ParagraphStyle('caption', parent=normal_style, alignment=TA_CENTER, fontSize=9)))
    story.append(Spacer(1, 0.12*inch))
    
    # Problem 4
    story.append(Paragraph("Problem 4: Frequency Response (End Force)", heading2_style))
    story.append(Paragraph(
        "When forcing at the end mass (mass 4), some resonance peaks are absent or significantly reduced. "
        "This occurs when a mode shape has a node (zero displacement) at the forcing location. The modal "
        "participation factor becomes zero, preventing excitation of that mode regardless of frequency. "
        "This demonstrates the critical importance of forcing location in structural dynamics.",
        normal_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    if os.path.exists('HW3_Part3_Problem4_FreqResponse_End.png'):
        img = Image('HW3_Part3_Problem4_FreqResponse_End.png', width=5.6*inch, height=3.1*inch)
        story.append(img)
        story.append(Paragraph("<i>Figure 11: Frequency response with force at end mass</i>", 
                              ParagraphStyle('caption', parent=normal_style, alignment=TA_CENTER, fontSize=9)))
    story.append(PageBreak())
    
    # Conclusions
    story.append(Paragraph("Conclusions", heading1_style))
    story.append(Paragraph(
        "This comprehensive analysis of string vibrations with discrete masses reveals several key insights:",
        normal_style
    ))
    story.append(Spacer(1, 0.1*inch))
    
    conclusions = [
        "The system exhibits distinct mode shapes with increasing complexity as mode number increases.",
        "Natural frequencies depend strongly on system discretization (N) and mass distribution.",
        "The first natural frequency decreases with N, approaching a continuous string limit.",
        "Higher natural frequencies increase with N, limited by mass spacing.",
        "Mass variation significantly affects all natural frequencies, with largest impact on modes having large displacement at the varied mass location.",
        "Forced response shows resonance peaks at natural frequencies, with magnitude determined by modal participation factors.",
        "Forcing location is critical - modes cannot be excited when forced at nodal points.",
        "Damping is essential for limiting resonance amplitudes in practical systems."
    ]
    
    for i, conclusion in enumerate(conclusions, 1):
        story.append(Paragraph(f"{i}. {conclusion}", normal_style))
        story.append(Spacer(1, 0.05*inch))
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(
        "These results provide valuable insights for vibration analysis and control of discrete mass-spring systems, "
        "with applications in structural dynamics, mechanical systems, and vibration isolation design.",
        normal_style
    ))
    
    # Build PDF
    doc.build(story, onFirstPage=add_page_decorations, onLaterPages=add_page_decorations)
    print(f"\n✓ PDF Report generated successfully: {filename}")
    print(f"  Location: {os.path.abspath(filename)}")
    return filename


if __name__ == "__main__":
    print("\n" + "="*80)
    print("Generating PDF Report for ENGR 6311 Assignment 3")
    print("="*80)
    create_report()
    print("\n" + "="*80)
    print("Report generation complete!")
    print("="*80 + "\n")
