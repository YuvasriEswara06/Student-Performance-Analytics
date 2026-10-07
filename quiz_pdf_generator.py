"""
quiz_pdf_generator.py - Academic PDF Assessment Sheet Generator
Uses ReportLab to create formatted printable PDF quiz questionnaires for proctees.
"""

import io
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_quiz_pdf(
    student_name: str,
    student_id: str,
    course_code: str,
    topic_title: str,
    quiz_id: str,
    questions: List[Dict[str, Any]]
) -> bytes:
    """
    Generates a professional academic assessment PDF containing the VIT header,
    student metadata, 10 MCQ question items, and an answer sheet bubble grid.
    Returns raw PDF bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0f172a'),
        alignment=1  # Center
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569'),
        alignment=1
    )
    section_heading = ParagraphStyle(
        'SecHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1e3a8a')
    )
    q_stem_style = ParagraphStyle(
        'QStem',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#0f172a')
    )
    opt_style = ParagraphStyle(
        'OptStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#334155')
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph("VELLORE INSTITUTE OF TECHNOLOGY", title_style))
    story.append(Paragraph("OFFICE OF THE ACADEMIC PROCTORING CELL — CONTINUOUS EVALUATION QUIZ", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e3a8a'), spaceAfter=12))

    # 2. Student Metadata Box
    meta_data = [
        [
            Paragraph(f"<b>Proctee Name:</b> {student_name}", opt_style),
            Paragraph(f"<b>Reg No:</b> {student_id}", opt_style)
        ],
        [
            Paragraph(f"<b>Course Code:</b> {course_code}", opt_style),
            Paragraph(f"<b>Assessment Quiz ID:</b> {quiz_id}", opt_style)
        ],
        [
            Paragraph(f"<b>Topic Scope:</b> {topic_title}", opt_style),
            Paragraph(f"<b>Total Marks:</b> 10.0 Marks", opt_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))

    story.append(Paragraph("PART A: ACTIVE-RECALL MULTIPLE CHOICE QUESTIONS", section_heading))
    story.append(Paragraph("<i>Instructions: Read each question stem carefully and mark your chosen answer on the response sheet below.</i>", subtitle_style))
    story.append(Spacer(1, 10))

    # 3. Question Items
    for idx, q in enumerate(questions, start=1):
        prompt_text = q.get("prompt", f"Question {idx}")
        options = q.get("options", ["A", "B", "C", "D"])

        story.append(Paragraph(f"<b>Q{idx}. {prompt_text}</b>", q_stem_style))
        story.append(Spacer(1, 4))

        opt_letters = ["A", "B", "C", "D"]
        for o_idx, opt_text in enumerate(options):
            l_code = opt_letters[o_idx] if o_idx < len(opt_letters) else str(o_idx+1)
            story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;[{l_code}] {opt_text}", opt_style))

        story.append(Spacer(1, 8))

    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceAfter=12))

    # 4. Answer Bubble Grid for Proctor Evaluation
    story.append(Paragraph("PROCTEE ANSWER SHEET & BUBBLE RESPONSE GRID", section_heading))
    story.append(Spacer(1, 6))

    grid_data = [["Q#", "[ A ]", "[ B ]", "[ C ]", "[ D ]", "Evaluator Score"]]
    for i in range(1, len(questions) + 1):
        grid_data.append([f"Q{i}", "[  ]", "[  ]", "[  ]", "[  ]", "___ / 1.0"])

    grid_table = Table(grid_data, colWidths=[40, 90, 90, 90, 90, 100])
    grid_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#94a3b8')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(grid_table)

    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>Proctor Signature:</b> ___________________________ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Date:</b> ______________", opt_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
