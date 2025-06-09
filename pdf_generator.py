from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

class PDFGenerator:
    def __init__(self, file_path):
        self.file_path = file_path

    def create_pdf(self, data):
        doc = SimpleDocTemplate(self.file_path, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # User Information Section
        title = Paragraph("PDF Entry Summary", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))

        user_info = f"""
        <b>First Name:</b> {data['First Name']}<br/>
        <b>Last Name:</b> {data['Last Name']}<br/>
        <b>Contact:</b> {data['Contact']}<br/>
        <b>Address:</b> {data['Address']}
        """
        elements.append(Paragraph(user_info, styles['Normal']))
        elements.append(Spacer(1, 20))

        # Table Header
        table_data = [["Model", "Variant", "Colors"]]

        # Populate table rows
        for entry in data["Entries"]:
            model = entry["Model"]
            variant = entry["Variant"]
            colors_user = ", ".join(entry["Colors"])
            table_data.append([model, variant, colors_user])

        # Create the table
        table = Table(table_data, colWidths=[100, 150, 250])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(table)

        # Build the PDF
        doc.build(elements)