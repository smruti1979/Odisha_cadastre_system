import io
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect, String, Line

def build_pdf_binary_manifest(active_df: pd.DataFrame, history_df: pd.DataFrame) -> io.BytesIO:
    """Compiles tabular registers and geometric lineage flow lines into a PDF bytes array."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=45, leftMargin=45, topMargin=45, bottomMargin=45)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=22, leading=26, textColor=colors.HexColor('#002B49'), spaceAfter=5)
    section_style = ParagraphStyle('Sec', parent=styles['Heading2'], fontSize=12, leading=16, textColor=colors.HexColor('#005A9C'), spaceBefore=12, spaceAfter=8)
    
    story.append(Paragraph("ODISHA CADASTRAL PROPERTY MANIFEST", title_style))
    story.append(Paragraph("Official Legal Record of Rights Manifest generated under Modular PoC Architecture", styles['Normal']))
    story.append(Spacer(1, 15))
    
    # SECTION 1: Active Registry Table
    story.append(Paragraph("Current Active Record-of-Rights (RoR)", section_style))
    t1_data = [['Khatiyan Code', 'Current Registered Owner', 'Plot Ref', 'Village ID', 'Extents (Acres)']]
    for _, row in active_df.iterrows():
        t1_data.append([str(row['khatiyan_no']), str(row['tenant_name_en']), str(row['plot_no']), str(row['village_code']), f"{row['area_acres']:.2f}"])

    # Explicit layout column widths assigned (Sum = 520 pt, fitting margins)   
    t1 = Table(t1_data, colWidths=[90, 190, 70, 90, 80])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#002B49')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F4F6F9')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('FONTSIZE', (0,0), (-1,-1), 9)
    ]))
    story.append(t1)
    
    # SECTION 2: Vector Ancestral Tree Graphic Flow
    if not history_df.empty:
        story.append(Spacer(1, 15))
        story.append(Paragraph("Traceable Ancestral Succession Timeline", section_style))
        
        draw_width = 520
        d = Drawing(draw_width, 80)
        d.add(Line(30, 40, draw_width-30, 40, strokeColor=colors.HexColor('#94A3B8'), strokeWidth=2))
        
        num_nodes = len(history_df)
        spacing = (draw_width - 100) / max((num_nodes - 1), 1)
        
        for idx, row in history_df.iterrows():
            x_pos = 50 + (idx * spacing)
            d.add(Rect(x_pos - 8, 32, 16, 16, fillColor=colors.HexColor('#005A9C'), strokeColor=colors.white))
            d.add(String(x_pos, 55, str(row['transfer_year']), fontName='Helvetica-Bold', fontSize=9, textAnchor='middle', fillColor=colors.HexColor('#0F172A')))
            d.add(String(x_pos, 18, str(row['owner_name']).split()[0], fontName='Helvetica', fontSize=8, textAnchor='middle', fillColor=colors.HexColor('#334155')))
            d.add(String(x_pos, 6, f"({row['relationship_tier']})", fontName='Helvetica-Oblique', fontSize=7, textAnchor='middle', fillColor=colors.HexColor('#64748B')))
            
        story.append(d)
        story.append(Spacer(1, 15))
        
        # SECTION 3: Detailed Historical Logs Table
        story.append(Paragraph("Historical Mutation Log Book Details", section_style))
        t2_data = [['Year', 'Historical Landholder', 'Lineage Relation', 'Legal Instrument / Action']]
        for _, h_row in history_df.iterrows():
            t2_data.append([str(h_row['transfer_year']), str(h_row['owner_name']), str(h_row['relationship_tier']), str(h_row['mutation_reason'])])

        # Explicit layout column widths assigned (Sum = 520 pt, fitting margins)   
        t2 = Table(t2_data, colWidths=[50, 140, 100, 230])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#475569')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 5),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F8FAFC')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('FONTSIZE', (0,0), (-1,-1), 8)
        ]))
        story.append(t2)

    doc.build(story)
    buffer.seek(0)
    return buffer