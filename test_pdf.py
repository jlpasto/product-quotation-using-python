from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import os
from datetime import datetime
import uuid
import json
from PIL import Image
import io
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class PDFGenerator:
    def __init__(self, file_path):
        self.file_path = file_path
        self.c = None # Canvas object will be initialized in create_pdf
        self.page_width, self.page_height = A4
        self.left_margin = 11 * mm
        self.right_margin = 11 * mm
        self.top_margin = 19 * mm
        self.bottom_margin = 19 * mm
        self.content_width = self.page_width - self.left_margin - self.right_margin
        self.current_y = self.page_height - self.top_margin # Y-coordinate for drawing down the page
        self.DEFAULT_LINE_HEIGHT_MM = 12 # Approximate line height for 10pt font

        # Define styles (used for text drawing parameters)
        self._set_styles()
        self._register_fonts()

    def _set_styles(self):
        # Fonts are typically set per drawing operation with canvas, not as predefined ParagraphStyles
        pass

    def _register_fonts(self):
        try:
            pdfmetrics.registerFont(TTFont("Georgia", "fonts/georgia.TTF"))
            pdfmetrics.registerFont(TTFont("Georgia-Bold", "fonts/georgiab.TTF"))
            pdfmetrics.registerFont(TTFont("Charter", "fonts/Charter Regular.ttf"))
            pdfmetrics.registerFont(TTFont("Charter-Bold", "fonts/Charter Bold.ttf"))
            pdfmetrics.registerFont(TTFont("Times-Roman-Bold", "fonts/timesbd.ttf"))
            pdfmetrics.registerFont(TTFont("Kunstler", "fonts/KUNSTLER.ttf"))
            #pdfmetrics.registerFont(TTFont("Signature", "fonts/ITCEDSCR.ttf"))
            
        except Exception as e: 
            print(f"Font registration failed: {e}")

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


    def hex_to_rgb(self, hex_color):
        """Convert hex color like '#RRGGBB' to (R, G, B) tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def remove_transparency_with_hex(self, png_path, hex_bg="#FFFFFF"):
        img = Image.open(png_path)
        if img.mode in ('RGBA', 'LA'):
            bg_color = self.hex_to_rgb(hex_bg)
            background = Image.new('RGB', img.size, bg_color)
            background.paste(img, mask=img.split()[-1])  # Use alpha channel
            byte_io = io.BytesIO()
            background.save(byte_io, format='PNG')
            byte_io.seek(0)
            return ImageReader(byte_io)  # ✅ THIS is what drawImage needs
        else:
            return ImageReader(png_path)  # No alpha, use path directly
        

    def _draw_header(self, data):
        header_height_percentage = 0.19
        header_background_height = self.page_height * header_height_percentage
        header_top_y = self.page_height # Top of the page

        # Draw the background rectangle (x, y, width, height)
        # It starts from (0, page_height - background_height) and goes up to page_height
        self.c.setFillColor(colors.HexColor('#313B4B')) # Dark grey background color
        self.c.rect(0, header_top_y - header_background_height, self.page_width, header_background_height, fill=1)

        # --- Header Content (Logo, Company Name, Contact Info) ---
        # Adjust Y for content within the header
        content_header_start_y = header_top_y - (10 * mm) # 10mm from top of the page

        # 1. Logo
        logo_path = data.get('header', {}).get('logoPath')
        logo_width = 27 * mm
        logo_height = 27 * mm

        logo_x = self.left_margin + (20 * mm)
        logo_y = content_header_start_y - logo_height # Position logo

        if logo_path and os.path.exists(logo_path):
            try:
                #self.c.drawImage(logo_path, logo_x, logo_y, width=logo_width, height=logo_height)
                image_data = self.remove_transparency_with_hex(logo_path, hex_bg="#313B4B") 
                self.c.drawImage(image_data, logo_x, logo_y, width=logo_width, height=logo_height)
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
        #self._draw_text(data['header']['companyName'], company_name_x, company_name_y,
        #                font_name='Helvetica-Bold', font_size=20, color=colors.white)

        # 3. Contact Info
        self.c.setFillColor(colors.HexColor('#D5D5D5'))
        self.c.setStrokeColor(colors.HexColor('#D5D5D5'))
        self.c.rect(128 * mm, self.page_height - (40 *mm) , 0.2 * mm , header_background_height / 2, fill=1)

        contact_info_x = self.page_width - self.right_margin - (65 * mm)
        contact_info_y_start = header_top_y - (15 * mm)
        line_height = self.DEFAULT_LINE_HEIGHT_MM # Approximate line height for 10pt font

        contact_lines = [
            data['header']['companyName'],
            data['header']['contactInfo']['addressLine1'],
            data['header']['contactInfo']['addressLine2'],
            data['header']['contactInfo']['phone'],
            #data['header']['contactInfo']['website'],
            data['header']['contactInfo']['email']

        ]

        """ 
        data['header']['contactInfo']['rc'],
        data['header']['contactInfo']['nis'],
        data['header']['contactInfo']['nif'],
        data['header']['contactInfo']['article']
        """
        font_charter_bold = "Charter-Bold"
        for i, line in enumerate(contact_lines):
            contact_info_x = self.page_width - self.right_margin - (65 * mm)
            if i == 3: # equals to phone
                line = "      " + line
                phone_icon_path = "phone1.png"
                phone_data = self.remove_transparency_with_hex(phone_icon_path, hex_bg="#313B4B") 
                self.c.drawImage(phone_data, contact_info_x, contact_info_y_start - (i * line_height)  - (0.5 *mm), width=3.5 * mm, height=3.5 * mm)
            if i == 4: # equals to emnail
                line = "      " + line
                email_icon_path = "email1.png"
                email_data = self.remove_transparency_with_hex(email_icon_path, hex_bg="#313B4B") 
                self.c.drawImage(email_data, contact_info_x, contact_info_y_start - (i * line_height) - (0.5 *mm), width=3.5 * mm, height=3.5 * mm)

            self._draw_text(line, contact_info_x, contact_info_y_start - (i * line_height),
                            font_name=font_charter_bold, font_size=10, color=colors.HexColor('#D5D5D5'), alignment='left')

        self._draw_text(f"RC    {data['header']['contactInfo']['rc']}", contact_info_x, contact_info_y_start - (5 * line_height),
                            font_name=font_charter_bold, font_size=7, color=colors.HexColor('#D5D5D5'), alignment='left')
        
        self._draw_text(f"Nis       {data['header']['contactInfo']['nis']}", contact_info_x + (32 * mm), contact_info_y_start - (5 * line_height),
                            font_name=font_charter_bold, font_size=7, color=colors.HexColor('#D5D5D5'), alignment='left')
        
        self._draw_text(f"Nif     {data['header']['contactInfo']['nif']}", contact_info_x, contact_info_y_start - (6 * line_height) + (1 *mm),
                            font_name=font_charter_bold, font_size=7, color=colors.HexColor('#D5D5D5'), alignment='left')
        
        self._draw_text(f"Article  {data['header']['contactInfo']['article']}", contact_info_x + (32 * mm), contact_info_y_start - (6 * line_height) + (1 *mm),
                            font_name=font_charter_bold, font_size=7, color=colors.HexColor('#D5D5D5'), alignment='left')
        # Update current_y after header
        self.current_y = header_top_y - header_background_height - (10 * mm) # 10mm space below header

    def _draw_bill_to_and_invoice_details(self, data):

        font_charter = "Charter"
        font_charter_bold = "Charter-Bold"
        # Bill To section (left column)
        bill_to_x = self.left_margin
        current_y_bill_to = self.current_y - (15 * mm)

        # Bill To Name
        self._draw_text(f"DESTINATAIRE:", bill_to_x, current_y_bill_to,
                        font_name=font_charter, font_size=12, color=colors.HexColor('#C9B7A1'))
        self._draw_text(f"{data['billTo']['name']}", bill_to_x + (33 * mm), current_y_bill_to,
                        font_name=font_charter_bold, font_size=12, color=colors.HexColor('#666666'))
        current_y_bill_to -= (4.5 * mm) # Space after Bill To Name

        self._draw_text(data['billTo']['addressLine1'], bill_to_x, current_y_bill_to,
                            font_name=font_charter, font_size=10, color=colors.HexColor('#666666'))
        
        current_y_bill_to -= self.DEFAULT_LINE_HEIGHT_MM + (0.5 * mm)

        self._draw_text(data['billTo']['addressLine2'], bill_to_x, current_y_bill_to,
                            font_name=font_charter, font_size=10, color=colors.HexColor('#666666'))
        
        current_y_bill_to -= self.DEFAULT_LINE_HEIGHT_MM + (5 * mm)
        
        phone_icon_path = "phone.png"
        phone_data = self.remove_transparency_with_hex(phone_icon_path, hex_bg="#FFFFFF") 
        self.c.drawImage(phone_data, bill_to_x, current_y_bill_to - (0.5 *mm), width=3.5 * mm, height=3.5 * mm)

        self._draw_text(f"      {data['billTo']['phone']}", bill_to_x, current_y_bill_to,
                            font_name=font_charter, font_size=10, color=colors.HexColor('#666666'))
        current_y_bill_to -= self.DEFAULT_LINE_HEIGHT_MM - (0.2 * mm)

        email_icon_path = "email.png"
        email_data = self.remove_transparency_with_hex(email_icon_path, hex_bg="#FFFFFF") 
        self.c.drawImage(email_data, bill_to_x, current_y_bill_to - (0.5 *mm), width=3.5 * mm, height=3.5 * mm)
        self._draw_text(f"      {data['billTo']['email']}", bill_to_x, current_y_bill_to,
                            font_name=font_charter, font_size=10, color=colors.HexColor('#666666'))
        current_y_bill_to -= self.DEFAULT_LINE_HEIGHT_MM - (0.2 * mm)


        #line_height = self.DEFAULT_LINE_HEIGHT_MM
        self._draw_text(f"RC    {data['header']['contactInfo']['rc']}", bill_to_x, current_y_bill_to,
                            font_name=font_charter, font_size=7, color=colors.HexColor('#5E5E5E'), alignment='left')
        
        self._draw_text(f"Nis       {data['header']['contactInfo']['nis']}", bill_to_x + (32 * mm), current_y_bill_to ,
                            font_name=font_charter, font_size=7, color=colors.HexColor('#5E5E5E'), alignment='left')
        
        self._draw_text(f"Nif     {data['header']['contactInfo']['nif']}", bill_to_x , current_y_bill_to - ( 3 * mm) ,
                            font_name=font_charter, font_size=7, color=colors.HexColor('#5E5E5E'), alignment='left')
        
        self._draw_text(f"Article  {data['header']['contactInfo']['article']}", bill_to_x + (32 * mm), current_y_bill_to - ( 3 * mm) ,
                            font_name=font_charter, font_size=7, color=colors.HexColor('#5E5E5E'), alignment='left')

        """
            data['billTo']['nif'],
            data['billTo']['nis'],
            data['billTo']['rc'],
            data['billTo']['article'],
            
        """

        # Invoice Title (Right-aligned)
        invoice_title_y = self.current_y - (20 * mm)
        invoice_title_x = self.page_width - (self.page_width * 0.5) + (7 * mm)
        self._draw_text("P R O F O R M A", invoice_title_x, invoice_title_y,
                        font_name='Times-Roman', font_size=21, color=colors.HexColor('#313B4B'), alignment='left')
        self.current_y -= (10 * mm) # Space after title

        self.c.setFillColor(colors.HexColor('#313B4B'))
        self.c.setStrokeColor(colors.HexColor('#313B4B'))
        self.c.rect(invoice_title_x -  (1 * mm) , invoice_title_y  - (7 * mm) , 70 * mm , 0.2 * mm, fill=1)

        invoice_date_lines = [
            ("Ref", data['invoiceDetails']['accountNo']),
            ("Date d’édition:", data['invoiceDetails']['invoiceDate']),
            ("Validité:", data['invoiceDetails']['issueDate'])
        ]
        current_y_invoice_details = invoice_title_y - (15 * mm) # Aligned a bit below Invoice title
        invoice_x_pos = self.page_width - (self.page_width * 0.5) + (10 * mm)
        invoice_x_pos = invoice_title_x
        invoice_y_pos = invoice_title_y - (18.5 * mm)

        font_times = "Times-Roman"
        font_times_bold = "Times-Roman-Bold"
        for label, value in invoice_date_lines:
            self._draw_text(label, invoice_x_pos, current_y_invoice_details,
                            font_name=font_times, font_size=8, color=colors.HexColor('#666666'), alignment='left')
            self._draw_text(value, invoice_x_pos, invoice_y_pos,
                            font_name=font_times_bold, font_size=8, color=colors.HexColor('#666666'))
            if label == "Date d’édition:":
                invoice_x_pos += 30 * mm
            else:
                invoice_x_pos += 23 * mm


            #current_y_invoice_details -= self.DEFAULT_LINE_HEIGHT_MM

        # vertical line
            
        self.c.setFillColor(colors.HexColor("#949393"))
        self.c.setStrokeColor(colors.HexColor('#949393'))
        self.c.rect(130 * mm, current_y_invoice_details - ( 3 * mm), 0.25 * mm , 7 * mm , fill=1)
        self.c.rect(158 * mm, current_y_invoice_details - ( 3 * mm), 0.25 * mm , 7 * mm , fill=1)
        # Update self.current_y to the lowest point of either column plus some space
        self.current_y = min(current_y_bill_to, current_y_invoice_details) - (18 * mm)

    def _draw_items_table(self, items_data):
        # Table headers
        headers = ["NOM MODELE", "COULEURS", "PRIX UNITAIRE", "QUANTINTE", "TOTAL HT"]
        #col_widths = [self.content_width * 0.15, self.content_width * 0.25,
        #              self.content_width * 0.35, self.content_width * 0.08,
        #              self.content_width * 0.18]
        col_widths = [ 35 * mm, 36 * mm, 35 * mm, 35 * mm, 35* mm]
        min_row_height = 8 * mm # Minimum height for a row
        header_height = 8 * mm

        table_start_y = self.current_y
        table_start_x = self.left_margin

        # Draw header background
        #self.c.setFillColor(colors.HexColor('#F0F0F0'))
        #self.c.rect(table_start_x, table_start_y - header_height, self.content_width, header_height, fill=1)
        
        # Table line above
        self.c.setFillColor(colors.HexColor('#5E5E5E'))
        self.c.setStrokeColor(colors.HexColor('#5E5E5E'))
        self.c.rect(table_start_x , table_start_y , self.page_width - ( 40 * mm) , 0.3 * mm, fill=1)

        self.c.rect(table_start_x , table_start_y  -  header_height , self.page_width - ( 40 * mm) , 0.3 * mm, fill=1)



        # Draw header text
        current_x_header = table_start_x
        for i, header in enumerate(headers):
            # Center header text within its column
            self._draw_text(header, current_x_header , table_start_y - (header_height / 2) - (1 * mm),
                            font_name='Georgia-Bold', font_size=10, color=colors.HexColor('#5E5E5E'), alignment='left')
            current_x_header += col_widths[i]

        # Draw header bottom line
        self.c.setStrokeColor(colors.HexColor("#5E5E5E"))
        self.c.setLineWidth(0.5)
        #self.c.line(table_start_x, table_start_y - header_height, table_start_x + self.content_width, table_start_y - header_height)

        self.current_y -= header_height # Move Y pointer below header

        # Draw item rows
        for i, item in enumerate(items_data):

            # remove the line at the very bottom


            color_lines = item['colors']
            #color_lines = item['description'].split('\n')
            # Calculate height for this row based on description lines. Add extra padding.
            actual_desc_height = len(color_lines) * self.DEFAULT_LINE_HEIGHT_MM
            calculated_row_height = max(min_row_height, actual_desc_height + (7 * mm)) # 4mm top/bottom padding
            
            # Draw row bottom line for the current row's calculated height
            if i != (len(items_data) - 1 ):
                self.c.setFillColor(colors.HexColor('#717070'))    
                self.c.line(table_start_x, self.current_y - calculated_row_height, self.page_width - ( 30 * mm), self.current_y - calculated_row_height)
            else:
                self.c.setFillColor(colors.HexColor("#717070"))    
                self.c.rect(table_start_x , self.current_y - calculated_row_height - (10 * mm), self.page_width - ( 40 * mm) , 0.5 * mm, fill=1)
                    
            # Calculate y for single-line cells: vertically centered in the row
            #y_single_line_cells = self.current_y - (calculated_row_height / 2) - (1.5 * mm) # Adjust for font baseline
            y_single_line_cells = self.current_y - (5.6 * mm) # Adjust for font baseline
            
            font_charter = "Charter"
            font_charter_bold = "Charter-Bold"
            # Draw text for single-line cells (Date, Unit Price, Qty, Total)
            self._draw_text(item['model'], table_start_x, y_single_line_cells,
                            font_name=font_charter, font_size=10, color=colors.HexColor('#333333'), alignment='left')
            # replace with prix unitaire
            self._draw_text(f"{item['unitPrice']}", table_start_x + col_widths[0] +  col_widths[1] + col_widths[2] - (5*mm), y_single_line_cells,
                            font_name=font_charter, font_size=10, color=colors.HexColor('#333333'), alignment='right')
            self._draw_text(str(item['qty']), table_start_x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3] - (5*mm) , y_single_line_cells,
                            font_name=font_charter, font_size=10, color=colors.HexColor('#333333'), alignment='right')
            self._draw_text(f"{item['total']}", table_start_x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3] + col_widths[4]- (8*mm) , y_single_line_cells,
                            font_name=font_charter, font_size=10, color=colors.HexColor('#333333'), alignment='right')
            
            # Draw multiline description
            # Start drawing from the top of the content area for description cell, with a small top padding
            desc_y_start = self.current_y - (5.6 * mm) 
            
            for j, line in enumerate(color_lines):
                text_to_draw = line.strip()
                #col_widths[0] + col_widths[1] + col_widths[2] - (3 * mm)
                #line_x_pos = table_start_x + col_widths[0] + col_widths[1] + (3 * mm) # Base X for description column
                line_x_pos = table_start_x + col_widths[0] # Base X for description column

                if text_to_draw:
                    # Draw bullet character slightly to the left, then the rest of the text indented
                    #bullet_char = text_to_draw[0]
                    bullet_char = "•"
                    #main_text = text_to_draw[1:].strip()
                    self._draw_text(bullet_char, line_x_pos, desc_y_start - (j * self.DEFAULT_LINE_HEIGHT_MM),
                                    font_name=font_charter, font_size=10, color=colors.HexColor('#333333'))
                    self._draw_text(text_to_draw, line_x_pos + (4 * mm), desc_y_start - (j * self.DEFAULT_LINE_HEIGHT_MM),
                                    font_name=font_charter, font_size=10, color=colors.HexColor('#333333'))
                else:
                    # Not used
                    self._draw_text(text_to_draw, line_x_pos, desc_y_start - (j * self.DEFAULT_LINE_HEIGHT_MM),
                                    font_name=font_charter, font_size=10, color=colors.HexColor('#333333'))

            self.current_y -= calculated_row_height # Move Y pointer down by the height of this row

        # Draw remaining vertical lines for the grid (from header bottom to current_y)
             
        #self.c.rect(current_x_vertical , table_start_y  -  header_height , self.page_width - ( 40 * mm) , 0.3 * mm, fill=1)
        self.c.setLineWidth(0.5)
        current_x_vertical = table_start_x
        for width in col_widths:
            #self.c.line(current_x_vertical, table_start_y, current_x_vertical, self.current_y)
            current_x_vertical += width
        #self.c.line(table_start_x + self.content_width, table_start_y, table_start_x + self.content_width, self.current_y)

        self.current_y -= (10 * mm) # Space after table

    def _draw_totals_and_payment_method(self, data):
        section_start_y = self.current_y - (22 * mm) # Overall space before this section starts

        # --- Left Column: Payment Method ---
        payment_method_x = self.left_margin
        current_y_left = section_start_y - (15 *mm) # Start Y for payment method block

        font_georgia_bold = "Georgia-Bold"
        font_charter = "Charter"
        font_charter_bold = "Charter-Bold"
        self._draw_text("MOYEN DE PAIEMENT", payment_method_x, current_y_left,
                        font_name=font_charter, font_size=10, color=colors.HexColor('#C9B7A1'))
        
        self.c.setFillColor(colors.HexColor('#333333'))
        self.c.setStrokeColor(colors.HexColor('#333333'))
        self.c.rect(payment_method_x , current_y_left - ( 3 * mm) , 60 * mm , 0.2 * mm, fill=1)
        current_y_left -= (8* mm) # Space after title
        #self._draw_text(data['paymentMethod']['paypal'], payment_method_x, current_y_left,
        #                font_name='Helvetica', font_size=9, color=colors.HexColor('#666666'))
        #current_y_left -= (self.DEFAULT_LINE_HEIGHT_MM)
        self._draw_text(data['paymentMethod']['cardAccept'], payment_method_x, current_y_left,
                        font_name=font_charter_bold, font_size=11, color=colors.HexColor('#666666'))
        
        # --- Right Column: Totals ---
        total_label_x = self.page_width - (100 * mm) # Adjusted for label width
        total_value_x = self.page_width - (35 * mm)
        current_y_right = section_start_y + (10 * mm) # Start Y for totals block, not align with payment method title

        # Sub-Total
        self._draw_text("Sous Total HT", total_label_x, current_y_right,
                        font_name=font_georgia_bold, font_size=10, color=colors.HexColor('#717070'), alignment='left')
        self._draw_text(f"{data['totals']['subTotal']}", total_value_x, current_y_right,
                        font_name=font_charter, font_size=10, color=colors.HexColor('#717070'), alignment='right')
        current_y_right -= (8 * mm) # Line spacing for totals

        # Tax
        self._draw_text(f"TVA", total_label_x, current_y_right,
                        font_name=font_georgia_bold, font_size=10, color=colors.HexColor('#717070'), alignment='left')
        self._draw_text(f"{data['totals']['taxAmount']}", total_value_x, current_y_right,
                        font_name=font_charter, font_size=10, color=colors.HexColor('#717070'), alignment='right')
        current_y_right -= (8 * mm)

        # Total TTC
        self._draw_text(f"Total TTC", total_label_x, current_y_right,
                        font_name=font_georgia_bold, font_size=10, color=colors.HexColor('#717070'), alignment='left')
        self._draw_text(f"{data['totals']['total_ttc']}", total_value_x, current_y_right,
                        font_name=font_charter, font_size=10, color=colors.HexColor('#717070'), alignment='right')
        current_y_right -= (8 * mm)

        # Discount
        self._draw_text(f"Acompte", total_label_x, current_y_right,
                        font_name=font_georgia_bold, font_size=10, color=colors.HexColor('#717070'), alignment='left')
        self._draw_text(f"{data['totals']['discountAmount']}", total_value_x, current_y_right,
                        font_name=font_charter, font_size=10, color=colors.HexColor('#717070'), alignment='right')
        current_y_right -= (5 * mm)

        # Grand Total Background
        grand_total_rect_height = 10 * mm
        self.c.setFillColor(colors.HexColor('#C9B7A1'))
        self.c.setStrokeColor(colors.HexColor('#C9B7A1'))
        rect_x_start = total_label_x - (2 *mm) # Small left padding for the rect
        rect_width = 70 * mm # Extend to right margin + padding
        self.c.rect(rect_x_start, current_y_right - grand_total_rect_height,
                    rect_width, grand_total_rect_height, fill=1)

        # Grand Total Text
        grand_total_text_y = current_y_right - (grand_total_rect_height / 2) - (0 * mm) # Vertically center in rect
        self._draw_text("A PAYER", rect_x_start + (2 * mm), grand_total_text_y,
                        font_name=font_georgia_bold, font_size=10, color=colors.HexColor('#FFFFFF'), alignment='left')
        self._draw_text(f"{data['totals']['grandTotal']}", total_value_x, grand_total_text_y,
                        font_name=font_charter, font_size=10, color=colors.HexColor('#FFFFFF'), alignment='right')
        current_y_right -= (grand_total_rect_height + 10 * mm) # Space after grand total

        # Update self.current_y to the lower of the two columns' ending positions
        self.current_y = min(current_y_left, current_y_right) - (10 * mm) # Add general space after section
        # Added
        self.current_y =  current_y_left 
    def _draw_footer(self, data):
        self.current_y -= (10 * mm) # Small space before "Thank You" section

        # "Thank You For Your Business!"
        footer_current_y =  self.bottom_margin + (20 * mm)

        self._draw_text("Merc i Pour Vo tre Con f iance", self.left_margin, footer_current_y,
                        font_name='Charter-Bold', font_size=13, color=colors.HexColor('#C9B7A1'))
        #self.current_y -= (6 * mm) + (20 * mm)

        # Thank You & Conditions (left column)
        ty_conditions_x = self.left_margin
        footer_current_y -= 8 * mm
        self._draw_text(data['thankYouMessage']['heading'], ty_conditions_x, footer_current_y,
                        font_name='Charter-Bold', font_size=10, color=colors.HexColor('#666666'))
        footer_current_y -= (self.DEFAULT_LINE_HEIGHT_MM)
        self._draw_text(data['thankYouMessage']['notesLine1'], ty_conditions_x, footer_current_y,
                        font_name='Charter', font_size=10, color=colors.HexColor('#666666'))
        footer_current_y -= (self.DEFAULT_LINE_HEIGHT_MM)
        self._draw_text(data['thankYouMessage']['notesLine2'], ty_conditions_x, footer_current_y,
                        font_name='Charter', font_size=10, color=colors.HexColor('#666666'))

        # Signature (right-aligned, center within its potential area)
        signature_center_x = self.page_width - self.right_margin - (50 *mm) # Approximate center of right half
        signature_y_start = self.bottom_margin + (18 * mm) # Adjust for vertical alignment with 'Thank You' text

        self._draw_text(data['signature']['name'], signature_center_x, signature_y_start,
                        font_name='Kunstler', font_size=16, color=colors.HexColor('#333333'), alignment='center')
        #self._draw_text(data['signature']['title'], signature_center_x, signature_y_start - (5 * mm),
        #                font_name='Helvetica', font_size=10, color=colors.HexColor('#666666'), alignment='center')
        
        self.c.setFillColor(colors.HexColor('#333333'))
        self.c.setStrokeColor(colors.HexColor('#333333'))
        self.c.rect(signature_center_x - (40*mm) , signature_y_start - (4 *mm) , 70 * mm , 0.1 * mm, fill=1)

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
            "companyName": "SARL Floor and Design",
            "logoPath": dummy_logo_path, # <--- IMPORTANT: Change this to your actual logo image path
            "contactInfo": {
                "addressLine1": f"Zone d’activité El Kseur",
                "addressLine2": "06310 El Kseur Béjaia, Algérie",
                "phone": "+33661161864",
                "website": "www.yourdomain.com",
                "email": "contact.floor.design@gmail.com",
                "rc": "06/00-0191144 B 22",
                "nif": "00220601911446",
                "nis": "00 22 06 40 00 27 8 52",
                "article": "06400135411",
            }
        },
        "invoiceDetails": {
            "accountNo": "0820Z829",
            "invoiceDate": "09/02/2026",
            "issueDate": "09/08/2026"
        },
        "billTo": {
            "name": "SARL Client Bis",
            "accountManager": "Account manager",
            "addressLine1": "Zone d’activité El Kseur",
            "addressLine2": "06310 El Kseur Béjaia, Algérie",
            "email": "contact.floor.design@gmail.com",
            "phone": "+33661161864",
            "nif": "00220601911446",
            "nis": "00 22 06 40 00 27 8 52",
            "rc": "06/00-0191144 B 22",
            "article": "06400135411"
        },
        "items": [
            {   
                "model": "Damia",
                "variant": "Phanes",
                "colors": ["Gris anthracite", "Jaune indien", "Gris Etain", "Bleu kossoghol"],
                "unitPrice": 10,
                "qty": 5,
                "total": 50
            },
        
            {   
                "model": "Eros",
                "variant": "Phanes",
                "colors": ["Rouge Ercolano", "Jaune 960", "Bleu charette"],
                "unitPrice": 12,
                "qty": 6,
                "total": 72
            }

        ],
        "paymentMethod": {
            "paypal": "paypal.username@outlook.com",
            "cardAccept": "Cheque   espèces   virement"
        },
        "totals": {
            "subTotal": 0, # Will be calculated dynamically
            "discountPercent": 10,
            "discountAmount": 0, # Will be calculated dynamically
            "taxPercent": 19,
            "taxAmount": 0, # Will be calculated dynamically
            "grandTotal": 0 # Will be calculated dynamically
        },
        "thankYouMessage": {
            "heading": "Termes & conditions",
            "notesLine1": "• Je dois remplir ça plus tard, voir ce qu’on doit écrire ici",
            "notesLine2": "• Il est tout a fait idiot de choisir à l’avance puisque les"
        },
        "signature": {
            "name": "A.K. YESSAD",
            "title": "Assistant Manager"
        }
    }

    # Recalculate totals based on items
    calculated_sub_total = sum(item['total'] for item in invoice_data['items'])
    invoice_data['totals']['subTotal'] = 122 #calculated_sub_total
    invoice_data['totals']['discountAmount'] = 10 # (invoice_data['totals']['discountPercent'] / 100) * calculated_sub_total
    invoice_data['totals']['taxAmount'] = "23,18" #(invoice_data['totals']['taxPercent'] / 100) * calculated_sub_total
    invoice_data['totals']['total_ttc'] = "145,18" # fix for now
    invoice_data['totals']['grandTotal'] = "135,18"
    """ 
    invoice_data['totals']['grandTotal'] = (
        calculated_sub_total -
        invoice_data['totals']['discountAmount'] +
        invoice_data['totals']['taxAmount']
    )
    """
    output_pdf_path = "replicated_invoice_canvas_final.pdf"
    pdf_gen = PDFGenerator(output_pdf_path)
    pdf_gen.create_pdf(invoice_data)