from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.units import inch
from datetime import datetime
import uuid


class PDFGenerator:
    def __init__(self, file_path):
        self.file_path = file_path

    def create_pdf(self, data):
        doc = SimpleDocTemplate(self.file_path, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Title (centered)
        title = Paragraph("PDF Entry Summary", styles['Title'])
        elements.append(title)

        # Right-aligned Date and Quotation No. in the next line
        today = datetime.today().strftime("%Y-%m-%d")
        quote_number = str(uuid.uuid4())[:8].upper()

        date_para = Paragraph(f"<b>Date:</b> {today}", styles['Normal'])
        quote_para = Paragraph(f"<b>Quotation No.:</b> {quote_number}", styles['Normal'])

        info_table = Table([[date_para], [quote_para]], colWidths=[450])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))

        elements.append(info_table)

        elements.append(Spacer(1, 20))

        # User Info
        user_info = f"""
        <b>Full Name:</b> {data['Full Name']}<br/>
        <b>Address:</b> {data['Address']}<br/>
        <b>Phone:</b> {data['Phone']}<br/>
        <b>Email:</b> {data['Email']}<br/>
        <b>NIF:</b> {data.get('NIF', '')}<br/>
        <b>NIS:</b> {data.get('NIS', '')}<br/>
        <b>RC:</b> {data.get('RC', '')}<br/>
        <b>Article:</b> {data.get('Article', '')}
        """
        elements.append(Paragraph(user_info, styles['Normal']))
        elements.append(Spacer(1, 20))

        # Table Header
        table_data = [["Model", "Variant", "Colors", "Quantity", "Amount"]]

        # Table Body
        sub_total = 0
        for entry in data["Entries"]:
            model = entry["Model"]
            variant = entry["Variant"]
            quantity = entry["Quantity"]
            amount = entry["Total_Amount"]
            sub_total += amount

            color_list = "<br/>".join([f"• {color}" for color in entry["Colors"] if color])
            color_paragraph = Paragraph(color_list, styles['Normal'])

            table_data.append([model, variant, color_paragraph, quantity, f"{amount:.2f} DA"])

        table = Table(table_data, colWidths=[80, 100, 180, 60, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 1), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))

        # Summary section
        tax_rate = 0.19  # 19% tax
        #discount = data.get("Discount", 0)  # Optional
        discount = 0  # Optional
        tax = sub_total * tax_rate
        grand_total = sub_total + tax - discount

        summary_data = [
            ["", "", "Sub Total", f"{sub_total:.2f}"],
            ["", "", "Tax (19%)", f"{tax:.2f}"],
            ["", "", "Discount", f"-{discount:.2f}"],
            ["", "", "Grand Total", f"{grand_total:.2f}"],
        ]

        summary_table = Table(summary_data, colWidths=[80, 100, 200, 80])
        summary_table.setStyle(TableStyle([
            ('LINEBELOW', (2, 0), (3, 0), 0.75, colors.black),
            ('LINEBELOW', (2, 1), (3, 1), 0.75, colors.black),
            ('LINEBELOW', (2, 2), (3, 2), 0.75, colors.black),
            ('LINEBELOW', (2, 3), (3, 3), 1.0, colors.black),
            ('ALIGN', (2, 0), (3, -1), 'RIGHT'),
            ('FONTNAME', (2, 0), (3, -1), 'Helvetica-Bold'),
        ]))

        elements.append(summary_table)

        # Build PDF
        doc.build(elements)
