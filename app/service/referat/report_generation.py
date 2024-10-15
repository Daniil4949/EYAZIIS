import os
from io import BytesIO

import reportlab.rl_config
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


class ReportGeneration:
    @staticmethod
    def get_report_buffer(keyword_report: str, classic_report: str) -> BytesIO:
        pdf_buffer = BytesIO()

        # Configure ReportLab to use UTF-8 encoding
        reportlab.rl_config.defaultEncoding = 'UTF-8'

        # Attempt to find a system font that supports Cyrillic characters
        cyrillic_fonts = [
            'Arial', 'Times New Roman', 'Verdana', 'Tahoma', 'LiberationSans',
            'DejaVuSans', 'FreeSans'
        ]
        font_found = False
        for font_name in cyrillic_fonts:
            try:
                pdfmetrics.registerFont(TTFont(font_name, f"{font_name}.ttf"))
                font_found = True
                break
            except:
                continue
        if not font_found:
            # As a fallback, use built-in font 'Helvetica'
            font_name = 'Helvetica'

        # Create PDF document
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            leftMargin=50,
            rightMargin=50,
            topMargin=50,
            bottomMargin=50
        )
        elements = []

        # Styles for formatting using the found font
        styles = getSampleStyleSheet()
        # Base style for normal text
        base_style = ParagraphStyle(
            'BaseStyle',
            fontName=font_name,
            fontSize=12,
            leading=14,
            leftIndent=20,
            rightIndent=20,
            spaceBefore=6,
            spaceAfter=6,
            wordWrap='CJK',  # Handles wrapping for long words
        )
        # Style for headings
        style_heading = ParagraphStyle(
            'CustomHeading',
            parent=base_style,
            fontSize=16,
            leading=20,
            leftIndent=0,
            rightIndent=0,
            spaceAfter=12,
            spaceBefore=12,
            alignment=1,  # Center alignment
        )
        # Style for the reports
        style_report = ParagraphStyle(
            'ReportStyle',
            parent=base_style,
            leftIndent=20,
            rightIndent=20,
            preserve=True,  # Preserves line breaks
            spaceBefore=6,
            spaceAfter=6,
        )

        # Replace newlines with <br/> to preserve line breaks in Paragraph
        keyword_report_formatted = keyword_report.replace('\n', '<br/>')
        classic_report_formatted = classic_report.replace('\n', '<br/>')

        # Add content with preserved formatting
        elements.append(Paragraph("Keyword Report", style_heading))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(keyword_report_formatted, style_report))
        elements.append(Spacer(1, 24))
        elements.append(Paragraph("Classic Report", style_heading))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(classic_report_formatted, style_report))

        # Generate PDF
        doc.build(elements)
        pdf_buffer.seek(0)
        return pdf_buffer
