from reportlab.platypus import ( SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle ) 
from reportlab.lib import colors 
from reportlab.lib.styles import getSampleStyleSheet 
from reportlab.lib.enums import TA_CENTER 

def create_pdf(company, role, experience, result, questions):
    pdf_file = "Interview_Report.pdf"
    doc = SimpleDocTemplate(
        pdf_file, 
        rightMargin=40, 
        leftMargin=40, 
        topMargin=40, 
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    title_style.alignment = TA_CENTER
    title_style.textColor = colors.white
    
    heading_style = styles["Heading2"]
    heading_style.textColor = colors.darkblue
    
    # Custom Question Styles for high readability
    q_style = styles["Normal"].clone('QuestionStyle')
    q_style.fontSize = 11
    q_style.leading = 16
    q_style.textColor = colors.HexColor("#2C3E50")  # Charcoal for easier reading
    
    content = []
    
    # ========================== #
    # HEADER                     #
    # ========================== #
    header_table = Table([[Paragraph("<b>AI ATS INTERVIEW REPORT</b>", title_style)]], colWidths=[500])
    header_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.darkblue),
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 15),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 15),
        ])
    )
    content.append(header_table)
    content.append(Spacer(1, 20))
    
    # ========================== #
    # CANDIDATE DETAILS          #
    # ========================== #
    content.append(Paragraph("Candidate Information", heading_style))
    details_data = [
        ["Company", company],
        ["Role", role],
        ["Experience", experience]
    ]
    details_table = Table(details_data, colWidths=[150, 350])
    details_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.lightblue),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold")
        ])
    )
    content.append(details_table)
    content.append(Spacer(1, 20))
    
    # ========================== #
    # PREDICTION SUMMARY         #
    # ========================== #
    content.append(Paragraph("Prediction Summary", heading_style))
    summary_data = [
        ["Total Rounds", str(result["Total Rounds"])],
        ["Difficulty", str(result["Difficulty"])]
    ]
    summary_table = Table(summary_data, colWidths=[150, 350])
    summary_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold")
        ])
    )
    content.append(summary_table)
    content.append(Spacer(1, 20))
    
    # ========================== #
    # ROUND FLOW                 #
    # ========================== #
    content.append(Paragraph("Interview Round Flow", heading_style))
    for i, round_name in enumerate(result["Round Flow"], start=1):
        content.append(Paragraph(f"➤ Round {i}: {round_name}", styles["Normal"]))
    content.append(Spacer(1, 20))
    
    # ========================== #
    # TOPICS                     #
    # ========================== #
    content.append(Paragraph("Important Topics", heading_style))
    topic_rows = [["Topic"]]
    topics = result["Topics"]
    
    if topics is not None:
        for topic in topics.index:
            topic_rows.append([topic])
            
    topic_table = Table(topic_rows, colWidths=[500])
    topic_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")
        ])
    )
    content.append(topic_table)
    content.append(PageBreak())
    
    # ========================== #
    # QUESTIONS PAGE (UPGRADED)  #
    # ========================== #
    content.append(Paragraph("Expected Interview Questions", heading_style))
    content.append(Spacer(1, 12))
    
    # Split the input text block into individual clean lines
    question_lines = [q.strip() for q in questions.split('\n') if q.strip()]
    
    # Build beautiful card UI items for each individual question
    for idx, item in enumerate(question_lines, start=1):
        # Format strings cleanly to make sure sub-bullets display properly
        clean_item = item.lstrip('•-* ').strip()
        formatted_text = f"<b>Q{idx}.</b> {clean_item}"
        
        # Alternating background colors for cards (white vs soft grey)
        bg_color = colors.HexColor("#F8F9FA") if idx % 2 == 0 else colors.white
        
        # Wrap into a clean left-bordered table structure
        q_card = Table([[Paragraph(formatted_text, q_style)]], colWidths=[500])
        q_card.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg_color),
            ('LINELEFT', (0, 0), (0, -1), 3, colors.HexColor("#002060")), # Elegant Navy Left accent bar
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),     # Subtle light grey borders
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        content.append(q_card)
        content.append(Spacer(1, 8)) # Space between cards
        
    content.append(Spacer(1, 15))
    
    # ========================== #
    # PREPARATION TIPS           #
    # ========================== #
    content.append(Paragraph("Preparation Tips", heading_style))
    content.append(
        Paragraph(
            """
            • Practice coding daily.<br/>
            • Revise core concepts.<br/>
            • Prepare HR answers.<br/>
            • Focus on company-specific topics.<br/>
            • Attempt mock interviews.
            """, 
            styles["Normal"]
        )
    )
    content.append(Spacer(1, 25))
    
    # ========================== #
    # FOOTER                     #
    # ========================== #
    italic_style = styles["Italic"] if "Italic" in styles else styles["Normal"]
    content.append(Paragraph("<i>Generated by AI ATS Interview Predictor</i>", italic_style))
    content.append(Paragraph("<i>Developed by Yash Raygade</i>", italic_style))
    
    doc.build(content)
    return pdf_file
