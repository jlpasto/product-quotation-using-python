from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import os
from datetime import datetime
import uuid
import json

# Import Pillow for dummy logo creation if needed
try:
    from PIL import Image as PILImage
except ImportError:
    PILImage = None

class PDFGenerator:
    def __init__(self, file_path):
        self.file_path = file_path
        self.c = None # Canvas object will be initialized in create_pdf
        self.page_width, self.page_height = A4
        self.left_margin = 15 * mm
        self.right_margin = 15 * mm
        self.top_margin = 15 * mm
        self.bottom_margin = 15 * mm
        self.content_width = self.page_width - self.left_margin - self.right_margin
        self.current_y = self.page_height - self.top_margin # Y-coordinate for drawing down the page
        self.DEFAULT_LINE_HEIGHT_MM = 12 # Approximate line height for 10pt font

        # Define styles (used for text drawing parameters)
        self._set_styles()

    def _set_styles(self):
        # Fonts are typically set per drawing operation with canvas, not as predefined ParagraphStyles
        pass

    def _draw_text(self, text, x, y, font_name='Helvetica', font_size=10, color=colors.black, alignment='left'):
        """Helper to draw text with specified properties."""
        self.c.setFont(font_name, font_size)
        self.c.setFillColor(color)
        if alignment == 'left':
            self.c.drawString(x, y, text)
        elif alignment == 'right':
            self.c.drawRightString(x, y, text)
        elif alignment == 'center':
            self.c.drawCentredString(x, y, text)

    def _draw_header(self, data):
        header_height_percentage = 0.12
        header_background_height = self.page_height * header_height_percentage
        header_top_y = self.page_height # Top of the page

        # Draw the background rectangle (x, y, width, height)
        # It starts from (0, page_height - background_height) and goes up to page_height
        self.c.setFillColor(colors.HexColor('#333333')) # Dark grey background color
        self.c.rect(0, header_top_y - header_background_height, self.page_width, header_background_height, fill=1)

        # --- Header Content (Logo, Company Name, Contact Info) ---
        # Adjust Y for content within the header
        content_header_start_y = header_top_y - (7 * mm) # 10mm from top of the page

        # 1. Logo
        logo_path = data.get('header', {}).get('logoPath')
        logo_width = 25 * mm
        logo_height = 20 * mm

        logo_x = self.left_margin
        logo_y = content_header_start_y - logo_height # Position logo

        if logo_path and os.path.exists(logo_path):
            try:
                self.c.drawImage(logo_path, logo_x, logo_y, width=logo_width, height=logo_height)
            except Exception as e:
                print(f"Error drawing logo image: {e}")
                self._draw_text("[LOGO]", logo_x, logo_y + (logo_height / 2) - (8 * mm),
                                 font_name='Helvetica-Bold', font_size=20, color=colors.white)
        else:
            self._draw_text("[LOGO]", logo_x, logo_y + (logo_height / 2) - (8 * mm),
                             font_name='Helvetica-Bold', font_size=20, color=colors.white)

        # 2. Company Name
        company_name_x = logo_x + logo_width + (5 * mm) # 5mm space after logo
        company_name_y = logo_y + (logo_height / 2) - (5 * mm) # Roughly vertically center with logo
        self._draw_text(data['header']['companyName'], company_name_x, company_name_y,
                        font_name='Helvetica-Bold', font_size=20, color=colors.white)

        # 3. Contact Info (Right-aligned)
        contact_info_x = self.page_width - self.right_margin
        contact_info_y_start = header_top_y - (10 * mm)
        line_height = self.DEFAULT_LINE_HEIGHT_MM + 4 # Approximate line height for 10pt font

        contact_lines = [
            data['header']['contactInfo']['addressLine1'],
            #data['header']['contactInfo']['addressLine2'],
            data['header']['contactInfo']['phone'],
            data['header']['contactInfo']['website'],
            data['header']['contactInfo']['email']
        ]

        for i, line in enumerate(contact_lines):
            self._draw_text(line, contact_info_x, contact_info_y_start - (i * line_height),
                            font_name='Helvetica', font_size=11, color=colors.HexColor('#FFFFFF'), alignment='right')

        # Update current_y after header
        self.current_y = header_top_y - header_background_height - (10 * mm) # 10mm space below header

    def _draw_bill_to_and_invoice_details(self, data):
        # Invoice Title (Right-aligned)
        invoice_title_y = self.current_y - (15 * mm)
        invoice_title_x = self.page_width - (self.page_width * 0.5) + (10 * mm)
        self._draw_text("INVOICE", invoice_title_x, invoice_title_y,
                        font_name='Times-Roman', font_size=35, color=colors.HexColor('#333333'), alignment='left')
        self.current_y -= (10 * mm) # Space after title

        # Bill To section (left column)
        bill_to_x = self.left_margin
        current_y_bill_to = self.current_y

        # Bill To Name
        self._draw_text(f"Bill To: {data['billTo']['name']}", bill_to_x, current_y_bill_to,
                        font_name='Helvetica-Bold', font_size=14, color=colors.HexColor('#333333'))
        current_y_bill_to -= (8 * mm) # Space after Bill To Name

        bill_detail_lines = [
            #data['billTo']['accountManager'],
            data['billTo']['addressLine1'],
            #data['billTo']['addressLine2'],
            data['billTo']['email'],
            data['billTo']['phone'],
            data['billTo']['nif'],
            data['billTo']['nis'],
            data['billTo']['rc'],
            data['billTo']['article'],
            
        ]

        for i, line in enumerate(bill_detail_lines):
            self._draw_text(line, bill_to_x, current_y_bill_to,
                            font_name='Helvetica', font_size=9, color=colors.HexColor('#666666'))
            current_y_bill_to -= self.DEFAULT_LINE_HEIGHT_MM

        # Invoice Details section (right column)
        #invoice_details_label_x = self.left_margin + (self.content_width * 0.5)
        invoice_details_label_x = self.page_width - self.right_margin
        invoice_details_value_x = self.left_margin + (self.content_width * 0.5) + (30 * mm)
        
        # Start invoice details at the same Y as "Bill To: Name" or slightly above.
        # Let's align it with the top of the "Bill To" name.
        current_y_invoice_details = invoice_title_y - (10 * mm) # Aligned a bit below Invoice title

        # Invoice A/C No
        #self._draw_text("A/C No:", invoice_x_pos, current_y_invoice_details,
        #                font_name='Helvetica', font_size=9, color=colors.HexColor('#666666'), alignment='left')
        #self._draw_text(data['invoiceDetails']['accountNo'], invoice_x_pos, current_y_invoice_details,
        #                font_name='Helvetica', font_size=9, color=colors.HexColor('#666666'))
        #current_y_invoice_details -= self.DEFAULT_LINE_HEIGHT_MM

        # Invoice Date & Issue Date
        invoice_date_lines = [
            ("A/C No:", data['invoiceDetails']['accountNo']),
            ("Invoice Date:", data['invoiceDetails']['invoiceDate']),
            ("Issue Date:", data['invoiceDetails']['issueDate'])
        ]
        
        invoice_x_pos = self.page_width - (self.page_width * 0.5) + (10 * mm)
        invoice_y_pos = invoice_title_y - (15 * mm)

        for label, value in invoice_date_lines:
            self._draw_text(label, invoice_x_pos, current_y_invoice_details,
                            font_name='Helvetica', font_size=9, color=colors.HexColor('#666666'), alignment='left')
            self._draw_text(value, invoice_x_pos, invoice_y_pos,
                            font_name='Helvetica-Bold', font_size=10, color=colors.HexColor('#666666'))
            #current_y_invoice_details -= self.DEFAULT_LINE_HEIGHT_MM
            invoice_x_pos += 30 * mm
            

        # Update self.current_y to the lowest point of either column plus some space
        self.current_y = min(current_y_bill_to, current_y_invoice_details) - (10 * mm)

    def _draw_items_table(self, items_data):
        # Table headers
        headers = ["NOM MODELE", "VARIANT", "COULEURS", "QTY", "TOTAL HT"]
        col_widths = [self.content_width * 0.15, self.content_width * 0.25,
                      self.content_width * 0.35, self.content_width * 0.08,
                      self.content_width * 0.18]
        
        min_row_height = 8 * mm # Minimum height for a row
        header_height = 7 * mm

        table_start_y = self.current_y
        table_start_x = self.left_margin

        # Draw header background
        self.c.setFillColor(colors.HexColor('#F0F0F0'))
        self.c.rect(table_start_x, table_start_y - header_height, self.content_width, header_height, fill=1)

        # Draw header text
        current_x_header = table_start_x
        for i, header in enumerate(headers):
            # Center header text within its column
            self._draw_text(header, current_x_header + (col_widths[i] / 2), table_start_y - (header_height / 2) - (2 * mm),
                            font_name='Helvetica-Bold', font_size=10, color=colors.HexColor('#333333'), alignment='center')
            current_x_header += col_widths[i]

        # Draw header bottom line
        self.c.setStrokeColor(colors.HexColor('#DDDDDD'))
        self.c.setLineWidth(0.5)
        self.c.line(table_start_x, table_start_y - header_height, table_start_x + self.content_width, table_start_y - header_height)

        self.current_y -= header_height # Move Y pointer below header

        # Draw item rows
        for i, item in enumerate(items_data):
            color_lines = item['colors']
            #color_lines = item['description'].split('\n')
            # Calculate height for this row based on description lines. Add extra padding.
            actual_desc_height = len(color_lines) * self.DEFAULT_LINE_HEIGHT_MM
            calculated_row_height = max(min_row_height, actual_desc_height + (7 * mm)) # 4mm top/bottom padding
            
            # Draw row bottom line for the current row's calculated height
            self.c.line(table_start_x, self.current_y - calculated_row_height, self.content_width + self.left_margin, self.current_y - calculated_row_height)

            # Calculate y for single-line cells: vertically centered in the row
            y_single_line_cells = self.current_y - (calculated_row_height / 2) - (1.5 * mm) # Adjust for font baseline

            # Draw text for single-line cells (Date, Unit Price, Qty, Total)
            self._draw_text(item['model'], table_start_x + (col_widths[0] / 2), y_single_line_cells,
                            font_name='Helvetica', font_size=10, color=colors.HexColor('#333333'), alignment='center')
            self._draw_text(f"{item['variant']}", table_start_x + col_widths[0] + ((col_widths[1]) / 2) , y_single_line_cells,
                            font_name='Helvetica', font_size=10, color=colors.HexColor('#333333'), alignment='center')
            self._draw_text(str(item['qty']), table_start_x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3] - (3 * mm), y_single_line_cells,
                            font_name='Helvetica', font_size=10, color=colors.HexColor('#333333'), alignment='right')
            self._draw_text(f"${item['total']:.2f}", table_start_x + self.content_width - (3 * mm), y_single_line_cells,
                            font_name='Helvetica', font_size=10, color=colors.HexColor('#333333'), alignment='right')
            
            # Draw multiline description
            # Start drawing from the top of the content area for description cell, with a small top padding
            desc_y_start = self.current_y - (7 * mm) 
            
            for j, line in enumerate(color_lines):
                text_to_draw = line.strip()
                #col_widths[0] + col_widths[1] + col_widths[2] - (3 * mm)
                line_x_pos = table_start_x + col_widths[0] + col_widths[1] + (3 * mm) # Base X for description column

                if text_to_draw:
                    # Draw bullet character slightly to the left, then the rest of the text indented
                    #bullet_char = text_to_draw[0]
                    bullet_char = "•"
                    #main_text = text_to_draw[1:].strip()
                    self._draw_text(bullet_char, line_x_pos, desc_y_start - (j * self.DEFAULT_LINE_HEIGHT_MM),
                                    font_name='Helvetica', font_size=10, color=colors.HexColor('#333333'))
                    self._draw_text(text_to_draw, line_x_pos + (4 * mm), desc_y_start - (j * self.DEFAULT_LINE_HEIGHT_MM),
                                    font_name='Helvetica', font_size=10, color=colors.HexColor('#333333'))
                else:
                    # Not used
                    self._draw_text(text_to_draw, line_x_pos, desc_y_start - (j * self.DEFAULT_LINE_HEIGHT_MM),
                                    font_name='Helvetica', font_size=10, color=colors.HexColor('#333333'))

            self.current_y -= calculated_row_height # Move Y pointer down by the height of this row

        # Draw remaining vertical lines for the grid (from header bottom to current_y)
        self.c.setLineWidth(0.5)
        current_x_vertical = table_start_x
        for width in col_widths:
            self.c.line(current_x_vertical, table_start_y, current_x_vertical, self.current_y)
            current_x_vertical += width
        self.c.line(table_start_x + self.content_width, table_start_y, table_start_x + self.content_width, self.current_y)

        self.current_y -= (10 * mm) # Space after table

    def _draw_totals_and_payment_method(self, data):
        section_start_y = self.current_y - (20 * mm) # Overall space before this section starts

        # --- Left Column: Payment Method ---
        payment_method_x = self.left_margin
        current_y_left = section_start_y # Start Y for payment method block

        self._draw_text("PAYMENT METHOD", payment_method_x, current_y_left,
                        font_name='Helvetica-Bold', font_size=12, color=colors.HexColor('#333333'))
        current_y_left -= (5 * mm) # Space after title

        self._draw_text(data['paymentMethod']['paypal'], payment_method_x, current_y_left,
                        font_name='Helvetica', font_size=9, color=colors.HexColor('#666666'))
        current_y_left -= (self.DEFAULT_LINE_HEIGHT_MM)
        self._draw_text(data['paymentMethod']['cardAccept'], payment_method_x, current_y_left,
                        font_name='Helvetica', font_size=9, color=colors.HexColor('#666666'))
        
        # --- Right Column: Totals ---
        total_label_x = self.page_width - self.right_margin - (50 * mm) # Adjusted for label width
        total_value_x = self.page_width - self.right_margin
        current_y_right = section_start_y + (20 * mm) # Start Y for totals block, not align with payment method title

        # Sub-Total
        self._draw_text("Sub-Total", total_label_x, current_y_right,
                        font_name='Helvetica-Bold', font_size=10, color=colors.HexColor('#333333'), alignment='right')
        self._draw_text(f"${data['totals']['subTotal']:.2f}", total_value_x, current_y_right,
                        font_name='Helvetica-Bold', font_size=12, color=colors.HexColor('#333333'), alignment='right')
        current_y_right -= (8 * mm) # Line spacing for totals

        # Discount
        self._draw_text(f"Discount ({data['totals']['discountPercent']}%)", total_label_x, current_y_right,
                        font_name='Helvetica-Bold', font_size=10, color=colors.HexColor('#333333'), alignment='right')
        self._draw_text(f"-${data['totals']['discountAmount']:.2f}", total_value_x, current_y_right,
                        font_name='Helvetica-Bold', font_size=12, color=colors.HexColor('#333333'), alignment='right')
        current_y_right -= (8 * mm)

        # Tax
        self._draw_text(f"Tax ({data['totals']['taxPercent']}%)", total_label_x, current_y_right,
                        font_name='Helvetica-Bold', font_size=10, color=colors.HexColor('#333333'), alignment='right')
        self._draw_text(f"${data['totals']['taxAmount']:.2f}", total_value_x, current_y_right,
                        font_name='Helvetica-Bold', font_size=12, color=colors.HexColor('#333333'), alignment='right')
        current_y_right -= (8 * mm)

        # Grand Total Background
        grand_total_rect_height = 10 * mm
        self.c.setFillColor(colors.HexColor('#333333'))
        rect_x_start = total_label_x - (35 * mm) # Small left padding for the rect
        rect_width = self.page_width - self.right_margin - rect_x_start + (5 * mm) # Extend to right margin + padding
        self.c.rect(rect_x_start, current_y_right - grand_total_rect_height,
                    rect_width, grand_total_rect_height, fill=1)

        # Grand Total Text
        grand_total_text_y = current_y_right - (grand_total_rect_height / 2) - (2 * mm) # Vertically center in rect
        self._draw_text("GRAND TOTAL", rect_x_start + (4 * mm), grand_total_text_y,
                        font_name='Helvetica-Bold', font_size=12, color=colors.HexColor('#FFFFFF'), alignment='left')
        self._draw_text(f"${data['totals']['grandTotal']:.2f}", total_value_x, grand_total_text_y,
                        font_name='Helvetica-Bold', font_size=12, color=colors.HexColor('#FFFFFF'), alignment='right')
        current_y_right -= (grand_total_rect_height + 10 * mm) # Space after grand total

        # Update self.current_y to the lower of the two columns' ending positions
        self.current_y = min(current_y_left, current_y_right) - (10 * mm) # Add general space after section
        # Added
        self.current_y =  current_y_left 
    def _draw_footer(self, data):
        self.current_y -= (10 * mm) # Small space before "Thank You" section

        # "Thank You For Your Business!"
        footer_current_y =  self.bottom_margin + (20 * mm)

        self._draw_text("Thank You For Your Business!", self.left_margin, footer_current_y,
                        font_name='Helvetica-Bold', font_size=12, color=colors.HexColor('#333333'))
        #self.current_y -= (6 * mm) + (20 * mm)

        # Thank You & Conditions (left column)
        ty_conditions_x = self.left_margin
        footer_current_y -= 10 * mm
        self._draw_text(data['thankYouMessage']['heading'], ty_conditions_x, footer_current_y,
                        font_name='Helvetica', font_size=10, color=colors.HexColor('#666666'))
        footer_current_y -= (self.DEFAULT_LINE_HEIGHT_MM)
        self._draw_text(data['thankYouMessage']['notesLine1'], ty_conditions_x, footer_current_y,
                        font_name='Helvetica', font_size=10, color=colors.HexColor('#666666'))
        footer_current_y -= (self.DEFAULT_LINE_HEIGHT_MM)
        self._draw_text(data['thankYouMessage']['notesLine2'], ty_conditions_x, footer_current_y,
                        font_name='Helvetica', font_size=10, color=colors.HexColor('#666666'))

        # Signature (right-aligned, center within its potential area)
        signature_center_x = self.page_width - self.right_margin - (self.content_width * 0.225) # Approximate center of right half
        signature_y_start = self.bottom_margin + (20 * mm) # Adjust for vertical alignment with 'Thank You' text

        self._draw_text(data['signature']['name'], signature_center_x, signature_y_start,
                        font_name='Helvetica-Bold', font_size=12, color=colors.HexColor('#333333'), alignment='center')
        self._draw_text(data['signature']['title'], signature_center_x, signature_y_start - (5 * mm),
                        font_name='Helvetica', font_size=10, color=colors.HexColor('#666666'), alignment='center')

    def create_pdf(self, data):
        self.c = canvas.Canvas(self.file_path, pagesize=A4)

        # Draw each section
        self._draw_header(data)
        self._draw_bill_to_and_invoice_details(data)
        self._draw_items_table(data['items'])
        self._draw_totals_and_payment_method(data)
        self._draw_footer(data)

        self.c.save()
        print(f"PDF generated successfully at {self.file_path}")

# Example Usage:
if __name__ == "__main__":
    # Create a dummy logo file for testing if it doesn't exist
    dummy_logo_path = "logo.png"
    if not os.path.exists(dummy_logo_path):
        if PILImage:
            try:
                # Create a simple red rectangle image as a dummy logo
                img = PILImage.new('RGB', (100, 80), color = 'red')
                img.save(dummy_logo_path)
                print(f"Created a dummy logo file at: {dummy_logo_path}")
            except Exception as e:
                print(f"Pillow found but could not create dummy logo: {e}")
                print("PDF will be generated without a logo image but with background.")
        else:
            print("Pillow not installed. Cannot create dummy logo. Please install with 'pip install Pillow' or provide your own 'logo.png'.")
            print("PDF will be generated without a logo image but with background.")

    invoice_data = {
        "header": {
            "companyName": "MAINSTREAM",
            "logoPath": dummy_logo_path, # <--- IMPORTANT: Change this to your actual logo image path
            "contactInfo": {
                "addressLine1": "1377 Maxwell Farm Road",
                "addressLine2": "Reno, CA 89503",
                "phone": "+01-252-555-0099",
                "website": "www.yourdomain.com",
                "email": "info@yourmail.com"
            }
        },
        "invoiceDetails": {
            "accountNo": "625 212 512",
            "invoiceDate": "20 Jan, 2018",
            "issueDate": "10 Feb, 2018"
        },
        "billTo": {
            "name": "Richard H. Jonas",
            "accountManager": "Account manager",
            "addressLine1": "Address: A- 5031 West Street, Andong, IA 50022",
            #"addressLine2": "P- 00 200-01-02",
            "email": "Email: info@yourmail.com",
            "phone": "Phone: +00 200-01-02",
            "nif": "NIF: 123456",
            "nis": "NIS: 23444",
            "rc": "RC: 123455356",
            "article": "Article: Sample"
        },
        "items": [
            {   
                "model": "Square",
                "variant": "Phanes",
                "colors": ["BI 5g + N318 1g CB", "BLEU CANARD 5 g CB", "Bleu Berin CB 5g"],
                "date": "10 Feb, 2018",
                "description": "BI 5g + N318 1g CB\n• BLEU CANARD 5 g CB\n• Bleu Berin CB 5g", # Example of multiline description
                "unitPrice": 2000.00,
                "qty": 2,
                "total": 4000.00
            }
        ],
        "paymentMethod": {
            "paypal": "paypal.username@outlook.com",
            "cardAccept": "Visa, Mastercard, Paypal"
        },
        "totals": {
            "subTotal": 0, # Will be calculated dynamically
            "discountPercent": 20,
            "discountAmount": 0, # Will be calculated dynamically
            "taxPercent": 25,
            "taxAmount": 0, # Will be calculated dynamically
            "grandTotal": 0 # Will be calculated dynamically
        },
        "thankYouMessage": {
            "heading": "Terms & Conditions:",
            "notesLine1": "• Above magna aliquarn erat volulpat ad minim veniam, quis nostrud",
            "notesLine2": "• Exercitation ullamco laboris nisi ut aliquip ex ea commodo"
        },
        "signature": {
            "name": "Thomas B. Speicher",
            "title": "Assistant Manager"
        }
    }

    # Recalculate totals based on items
    calculated_sub_total = sum(item['total'] for item in invoice_data['items'])
    invoice_data['totals']['subTotal'] = calculated_sub_total
    invoice_data['totals']['discountAmount'] = (invoice_data['totals']['discountPercent'] / 100) * calculated_sub_total
    invoice_data['totals']['taxAmount'] = (invoice_data['totals']['taxPercent'] / 100) * calculated_sub_total
    invoice_data['totals']['grandTotal'] = (
        calculated_sub_total -
        invoice_data['totals']['discountAmount'] +
        invoice_data['totals']['taxAmount']
    )

    output_pdf_path = "replicated_invoice_canvas_final.pdf"
    pdf_gen = PDFGenerator(output_pdf_path)
    pdf_gen.create_pdf(invoice_data)