import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from settings import Settings
from create_pdf import PDFGenerator  # Ensure you have this module
from model import (
    csv_carre_keys_list,
    csv_hexa_keys_list,
    csv_frise_keys_list,
    csv_tapis_keys_list,
    csv_baguettes_keys_list,
    csv_baguettes_dict,
    csv_carre_dict,
    csv_frise_dict,
    csv_hexa_dict,
    csv_tapis_dict
)


from color import csv_couleur_keys_list, csv_couleur_dict
import re
from datetime import datetime
import os
import uuid
import json
from dateutil.relativedelta import relativedelta


class UserFormApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Generator")
        self.root.geometry("1300x700")

        self.model_variants = {
            "Square": csv_carre_keys_list,
            "Hexagonal": csv_hexa_keys_list,
            "Frieze": csv_frise_keys_list,
            "Berber Carpet": csv_tapis_keys_list,
            "Baguettes": csv_baguettes_keys_list
        }

        settings = self.load_settings()
        self.conversion_rates = {
            "USD": settings["invoice"]["rate_USD"],  # 1 Dinar = rate_USD
            "EUR": settings["invoice"]["rate_EUR"],  # 1 Dinar = rate_EUR
            "Dinar": 1.0  # 1 Dinar = 1 Dinar
        }

        self.variant_price_map = csv_baguettes_dict

        self.color_choices = csv_couleur_keys_list
        self.entries_data = []

        self.create_widgets()

        self.add_entry_row()  # Add one row initially

    def load_settings(self):
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                data = json.load(f)
            return data
        else:
            return None  # no settings yet
    

    def open_settings_window(self):

        settings_data = None
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                settings_data = json.load(f)
                
        Settings(self.root, settings_data)

    def create_widgets(self):
        # Title Frame (top bar)
        title_frame = tk.Frame(self.root)
        title_frame.pack(fill="x", pady=10, padx=10)

        # Title label on the left
        title_label = tk.Label(title_frame, text="PDF GENERATOR FORM", font=("Arial", 24))
        title_label.pack(side="left")

        # Settings button on the right
        settings_button = tk.Button(title_frame, text="Settings", command=self.open_settings_window)
        settings_button.pack(side="right")

        # Personal Details
        client_frame = tk.LabelFrame(self.root, text="Personal Details", padx=10, pady=10)
        client_frame.pack(fill="x", padx=20, pady=10)

        # Full Name
        tk.Label(client_frame, text="Full Name:").grid(row=0, column=0, sticky="w")
        self.full_name = tk.Entry(client_frame, width=40)
        self.full_name.grid(row=0, column=1, padx=5, pady=5)

        # Address
        tk.Label(client_frame, text="Address Line 1:").grid(row=0, column=2, sticky="w")
        self.address = tk.Entry(client_frame, width=40)
        self.address.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(client_frame, text="Address Line 2:").grid(row=0, column=4, sticky="w")
        self.address_2 = tk.Entry(client_frame, width=40)
        self.address_2.grid(row=0, column=5, padx=5, pady=5)

        # Phone Number
        def validate_phone(event):
            phone = event.widget.get().strip()
            if not phone:  # Skip validation if empty
                return
            
            # This regex matches phone numbers with optional +, digits, spaces, dashes, and parentheses
            pattern = r"^\+?[\d\s\-\(\)]{7,15}$"
            
            if not re.match(pattern, phone):
                messagebox.showerror("Invalid Phone Number", "Please enter a valid phone number.")
                event.widget.focus_set()  # Set focus back to phone entry if invalid

        tk.Label(client_frame, text="Phone Number:").grid(row=1, column=0, sticky="w")
        self.phone = tk.Entry(client_frame, width=40)
        self.phone.grid(row=1, column=1, padx=5, pady=5)
        self.phone.bind("<FocusOut>", validate_phone)


        # Email
        def validate_email(event):
            email = event.widget.get().strip()
            if not email:  # Skip validation if empty
                return
    
            # Simple email regex pattern
            pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
            if not re.match(pattern, email):
                messagebox.showerror("Invalid Email", "Please enter a valid email address.")
                event.widget.focus_set()  # Set focus back to email entry if invalid


        tk.Label(client_frame, text="Email:").grid(row=1, column=2, sticky="w")
        self.email = tk.Entry(client_frame, width=40)
        self.email.grid(row=1, column=3, padx=5, pady=5)

        self.email.bind("<FocusOut>", validate_email)

        # Nif
        tk.Label(client_frame, text="Nif:").grid(row=2, column=0, sticky="w")
        self.nif = tk.Entry(client_frame, width=40)
        self.nif.grid(row=2, column=1, padx=5, pady=5)

        # Nis
        tk.Label(client_frame, text="Nis:").grid(row=2, column=2, sticky="w")
        self.nis = tk.Entry(client_frame, width=40)
        self.nis.grid(row=2, column=3, padx=5, pady=5)

        # RC
        tk.Label(client_frame, text="RC:").grid(row=3, column=0, sticky="w")
        self.rc = tk.Entry(client_frame, width=40)
        self.rc.grid(row=3, column=1, padx=5, pady=5)

        # Article
        tk.Label(client_frame, text="Article:").grid(row=3, column=2, sticky="w")
        self.article = tk.Entry(client_frame, width=40)
        self.article.grid(row=3, column=3, padx=5, pady=5)

        # Add Entry Button
        tk.Button(self.root, text="Add Entry", command=self.add_entry_row).pack(pady=10)


        # Table Container
        table_container = tk.Frame(self.root)
        table_container.pack(padx=20, fill="both", expand=True)

        # Frame for canvas + vertical scrollbar
        canvas_frame = tk.Frame(table_container)
        canvas_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(canvas_frame)
        v_scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        h_scrollbar = tk.Scrollbar(table_container, orient="horizontal", command=canvas.xview)

        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        v_scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        h_scrollbar.pack(side="bottom", fill="x")

        self.table_frame = tk.Frame(canvas)

        self.table_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.table_frame, anchor="nw")

        #canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")


        # Table Header
        headers = ["Model", "Variant", "Qty", "Color 1", "Color 2", "Color 3", "Color 4", "Color 5", "Delete"]
        for idx, text in enumerate(headers):
            col_width = 12
            if text.startswith("Color"):
                col_width = 20  # widen Color headers to match combobox width
            tk.Label(self.table_frame, text=text, relief="ridge", width=col_width).grid(row=0, column=idx, sticky="nsew")

        # Bottom Buttons
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(pady=20)
        
        tk.Button(bottom_frame, text="Generate PDF", command=self.generate_pdf, padx=30, pady=10).pack(side="left", padx=10)
      #  tk.Button(bottom_frame, text="Close", command=self.root.quit).pack(side="left", padx=10)

    def add_entry_row(self):
        row_index = len(self.entries_data) + 1
        row_widgets = {}

        row_widgets["Variant_Price"] = 0

        model_var = tk.StringVar()
        model_cb = ttk.Combobox(self.table_frame, textvariable=model_var, state="readonly", width=12)
        model_cb['values'] = list(self.model_variants.keys())
        model_cb.grid(row=row_index, column=0, padx=1, pady=1)
        row_widgets["Model"] = model_var

        variant_var = tk.StringVar()
        variant_cb = ttk.Combobox(self.table_frame, textvariable=variant_var, state="readonly", width=12)
        variant_cb.grid(row=row_index, column=1, padx=1, pady=1)
        row_widgets["Variant"] = variant_var


        def update_variant_options(event=None):
            selected_model = model_var.get()
            variants = self.model_variants.get(selected_model, [])
            variant_cb['values'] = variants
            variant_var.set(variants[0] if variants else "")

        model_cb.bind("<<ComboboxSelected>>", update_variant_options)

        # Quantity
        qty_entry = tk.Entry(self.table_frame, width=12)
        qty_entry.insert(0, "1")
        qty_entry.grid(row=row_index, column=2)

        def on_qty_focus_out(event):
            value = qty_entry.get().strip()
            if value == "" or not value.isdigit() or int(value) < 1:
                messagebox.showwarning("Invalid Quantity", "Quantity must be a number greater than 0.")
                qty_entry.delete(0, tk.END)
                qty_entry.insert(0, "1")

        qty_entry.bind("<FocusOut>", on_qty_focus_out)

        row_widgets["Quantity"] = qty_entry
        
        # Color
        for i in range(1, 6):
            color_var = tk.StringVar()
            color_cb = ttk.Combobox(self.table_frame, textvariable=color_var, state="readonly", width=20)
            color_cb['values'] = [""] + self.color_choices
            color_cb.grid(row=row_index, column=2 + i)
            row_widgets[f"Color{i}"] = color_var
    
        delete_btn = tk.Button(self.table_frame, text="Delete",
                               command=lambda r=row_index: self.delete_entry_row(r))
        delete_btn.grid(row=row_index, column=8)
        row_widgets["Row"] = row_index

        self.entries_data.append(row_widgets)

    def delete_entry_row(self, row_index):
        row_widgets = self.entries_data[row_index - 1]
        for widget in self.table_frame.grid_slaves():
            if int(widget.grid_info()["row"]) == row_index:
                widget.destroy()
        self.entries_data[row_index - 1] = None
    
    def average_prices(self, prices):
        # Filter out None and empty strings
        valid_prices = [int(p) for p in prices if p not in (None, '')]
        
        if not valid_prices:
            return 0  # Avoid division by zero
        
        return sum(valid_prices) / len(valid_prices)

    def get_variant_price(self, selected_model, selected_variant):

        price = 0
        match selected_model:
            case "Square" :
                price = csv_carre_dict.get(selected_variant, 0)
            case "Hexagonal" :
                price = csv_hexa_dict.get(selected_variant, 0)
            case "Frieze" :
                price = csv_frise_dict.get(selected_variant, 0)
            case "Berber Carpet" :
                price = csv_tapis_dict.get(selected_variant, 0)
            case "Baguettes" :
                price = csv_baguettes_dict.get(selected_variant, 0)
            case _:
                price = 0
        return int(price)
    
    def convert_currency_to_dinar(self, amount, currency):
        """
        Converts amount from given currency to Dinar.

        Parameters:
            amount (float): The amount to convert.
            currency (str): The currency code of the amount.

        Returns:
            float: Amount in Dinar.
        """
        if amount <= 0:
            return 0

        if currency not in self.conversion_rates:
            raise ValueError(f"Unsupported currency: {currency}")

        rate = self.conversion_rates[currency]

        # Since rates are Dinar to currency, we invert it to convert back to Dinar
        amount_in_dinar = amount / rate
        return round(amount_in_dinar, 6)
    

    def collect_entry_data(self):
        data = []
        for row in self.entries_data:
            if row is None:
                continue

            color_arr = [row[f"Color{i}"].get() for i in range(1, 6)]
            # removes empty array
            filtered_color_arr = [color for color in color_arr if color]
            color_prices_arr = [csv_couleur_dict.get(row[f"Color{i}"].get()) for i in range(1, 6)]
            color_prices_average = self.average_prices(color_prices_arr)
            color_supplement_len = len(filtered_color_arr) # the number of colors selected
            qty_str = row["Quantity"].get()
            qty = int(qty_str) if qty_str.strip().isdigit() and int(qty_str) > 0 else 1
            selected_model = row["Model"].get()
            selected_variant = row["Variant"].get()
            variant_price = self.get_variant_price(selected_model, selected_variant)

            #color_supplement_in_dinar = self.convert_currency_to_dinar(amount=color_supplement, currency="Dinar")
            COLOR_SUPPLEMENT_PER_COLOR_DA_PRICE = 250 # fixed price for every color supplement
            color_supplement_in_dinar_total = color_supplement_len * COLOR_SUPPLEMENT_PER_COLOR_DA_PRICE
            unit_amount = variant_price + color_prices_average + color_supplement_in_dinar_total
            total_amount = unit_amount * qty

            print(f"Variant price: {variant_price}")
            if filtered_color_arr:
                joined_string = ', '.join(filtered_color_arr)
                print(f"joined_string {joined_string}")
            else:
                print("No color found")
            print(f"color_prices_average: {color_prices_average}")
            print(f"Number of color : {color_supplement_len}")
            print(f"color_supplement_in_dinar price: {color_supplement_in_dinar_total}")
            print(f"unit_amount: {unit_amount}")

            entry = {
                "model": row["Model"].get(),
                "variant": row["Variant"].get(),
                #"Variant_Price": variant_price,
                "qty": row["Quantity"].get(),
                "colors": filtered_color_arr,
                #"Colors_Prices": color_prices_arr,
                #"Colors_Prices_Average": color_prices_average,
                "unitPrice": unit_amount,
                "total": total_amount
            }
            
            data.append(entry)
        return data

    def generate_invoice_number(self):
        unique_id = uuid.uuid4()
        invoice_number = f"{unique_id.hex[:8].upper()}"  # Take first 12 chars of UUID
        return invoice_number

    def get_invoice_current_date(self):
        return datetime.now().strftime("%d/%m/%Y")

    
    def get_invoice_issue_date(self, months=3):
        #Default: 3 months ahead
        future_date = datetime.now() + relativedelta(months=months)
        return future_date.strftime("%d/%m/%Y")

    def get_invoice_validity(self, number = 3, duration="month"):
        #Default: 3 months ahead
        try:
            future_date = relativedelta(months=number)
            if duration == "day":
                future_date = relativedelta(days=number)
            elif duration == "week":
                future_date = relativedelta(weeks=number)
            elif duration == "month":
                future_date = relativedelta(months=number)
            else: # year
                future_date = relativedelta(years=number)
            validity_date = datetime.now() + future_date
            return validity_date.strftime("%d/%m/%Y")
        except Exception as e:
            print(f"Error in get_invoice_validity(): {e}")
            #Default: 3 months ahead when there is error
            future_date = relativedelta(months=number)
            validity_date = datetime.now() + future_date
            return validity_date.strftime("%d/%m/%Y")
        
    def has_missing_model(self, entries):
        return any(not entry.get('model') for entry in entries)

    def get_conversion_rates(self, currency_sign = "da"):
        """
        Returns the conversion rates from Dinar to USD and EUR.
        Base currency: Dinar

        Returns:
            int : The current convertion from DInar to selected currency
        """
        if currency_sign == "USD":
            return self.conversion_rates["USD"]
        elif currency_sign == "EUR":
            return self.conversion_rates["EUR"]
        else: # DA
            return 1.0

    def convert_unit_price_and_total_ht(self, entries, currency_sign):
        try:
            exchange_rate = self.get_conversion_rates(currency_sign)
            for entry in entries:
                if "unitPrice" in entry:
                    entry["unitPrice"] *= exchange_rate
                if "total" in entry:
                    entry["total"] *= exchange_rate
            return entries
        except Exception as e:
            print(f"Error in convert_unit_price_and_total_ht: {e}")

    def convert_totals(self, 
                    currency_sign, 
                    sub_total ,
                    discount_amount ,
                    tax_amount,
                    total_ttc,
                    grand_total, 
                    delivery_cost):
        try:
            exchange_rate = self.get_conversion_rates(currency_sign)

            converted_totals = {}
            converted_totals["sub_total"] = sub_total * exchange_rate
            converted_totals["discount_amount"] = discount_amount * exchange_rate
            converted_totals["tax_amount"] = tax_amount * exchange_rate
            converted_totals["total_ttc"] = total_ttc * exchange_rate
            converted_totals["grand_total"] = grand_total * exchange_rate
            converted_totals["delivery_cost"] = delivery_cost * exchange_rate
            
            return converted_totals
        except Exception as e:
            print(f"Error in convert_totals: {e}")


    def generate_pdf(self):


        # Load once when the module is imported
        settings = self.load_settings()
        # Company Section
        set_company_name = settings["company"]["companyName"]
        set_logo_path = settings["company"]["logoPath"]
        set_address_line_1 = settings["company"]["addressLine1"]
        set_address_line_2 = settings["company"]["addressLine2"]
        set_company_phone = settings["company"]["phone"]
        set_company_email = settings["company"]["email"]
        set_rc = settings["company"]["rc"]
        set_nif = settings["company"]["nif"]
        set_nis = settings["company"]["nis"]
        set_article = settings["company"]["article"]

        # Invoice Section
        set_invoice_title = settings["invoice"]["title"]
        set_validity_number = settings["invoice"]["validity"]["number"]
        set_validity_duration = settings["invoice"]["validity"]["duration"]
        set_mode_of_payment = settings["invoice"]["modeOfPayment"]
        set_currency = settings["invoice"]["currency"]
        set_decimal_point = settings["invoice"]["decimalPoint"]
        set_tax_percent = settings["invoice"]["tax"]
        set_discount_percent = settings["invoice"]["discount"]
        set_delivery_cost = settings["invoice"]["deliveryCost"]

        # Terms Section
        set_terms_label = settings["terms"]["termsLabel"]
        set_terms_line_1 = settings["terms"]["termsLine1"]
        set_terms_line_2 = settings["terms"]["termsLine2"]

        # Signature Section
        set_signature_name_cursive = settings["signature"]["nameCursive"]
        set_signature_full_name = settings["signature"]["fullName"]
        set_signature_position = settings["signature"]["position"]


        invoice_no = self.generate_invoice_number()
        invoice_date = self.get_invoice_current_date()
        invoice_issue_date = self.get_invoice_validity(set_validity_number, set_validity_duration)

        full_name = self.full_name.get().strip()
        address = self.address.get().strip()
        address_2 = self.address_2.get().strip()
        phone = self.phone.get().strip()
        email = self.email.get().strip()

        nif = self.nif.get().strip()
        nis = self.nis.get().strip()
        rc = self.rc.get().strip()
        article = self.article.get().strip()

        if not all([full_name, address, phone, email, nif, nis, rc, article]):
            messagebox.showerror("Input Error", "Please complete all personal details.")
            return

        entries = self.collect_entry_data()

        print(f"ENTRIES:{entries}")
        if not entries:
            messagebox.showerror("Input Error", "Please add at least one entry.")
            return

        is_model_missing = self.has_missing_model(entries)
        if is_model_missing:
            messagebox.showerror("Input Error", "One of entries has no selected model.")
            return
        
        def create_filepath():
            now = datetime.now()
            formatted_time = now.strftime("%Y-%m-%d_%H-%M-%S")
            default_filename = f"{full_name}_PDF_Output.pdf"

            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile=default_filename,
                title="Save PDF As"
            )

            return file_path
        
        file_path = create_filepath()
        if not file_path:
            return

        settings = self.load_settings()
        # Header details
        HEADER_COMPANY_NAME = set_company_name
        HEADER_LOGO_PATH = set_logo_path
        HEADER_ADDRESS_LINE_1 = set_address_line_1
        HEADER_ADDRESS_LINE_2 = set_address_line_2
        HEADER_PHONE = set_company_phone
        HEADER_WEBSITE = "www.yourdomain.com"
        HEADER_EMAIL = set_company_email
        HEADER_RC = set_rc
        HEADER_NIF = set_nif
        HEADER_NIS = set_nis
        HEADER_ARTICLE = set_article
        
        
        # Invoice details
        INVOICE_TITLE = set_invoice_title
        INVOICE_ACCOUNT_NO = invoice_no
        INVOICE_DATE = invoice_date
        INVOICE_ISSUE_DATE = invoice_issue_date

        BILL_TO_NAME = full_name
        BILL_TO_ADDRESS_LINE = address
        BILL_TO_ADDRESS_LINE_2 = address_2
        BILL_TO_EMAIL = email
        BILL_TO_PHONE = phone
        BILL_TO_NIF = nif
        BILL_TO_NIS = nis
        BILL_TO_RC = rc
        BILL_TO_ARTICLE = article
        
        PAYMENT_METHOD_1 = "   ".join(set_mode_of_payment)
        CURRENCY_SIGN = set_currency
        DECIMAL_POINT = set_decimal_point

        # Total computation
        DISCOUNT_PERCENT = set_discount_percent
        TAX_PERCENT = set_tax_percent
        DELIVERY_COST = set_delivery_cost

        # Thank you message
        TY_MSG_HEADING = set_terms_label
        TY_MSG_NOTES_LINE_1 = set_terms_line_1
        TY_MSG_NOTES_LINE_2 = set_terms_line_2

        SIGNATURE_NAME = set_signature_name_cursive
        SIGNATURE_FULLNAME = set_signature_full_name
        SIGNATURE_TITLE =  set_signature_position
        SIGNATURE_SIGN_IMG = ""

        invoice_data = {
            "header": {
                "companyName": HEADER_COMPANY_NAME,
                "logoPath": HEADER_LOGO_PATH, 
                "contactInfo": {
                    "addressLine1": HEADER_ADDRESS_LINE_1,
                    "addressLine2": HEADER_ADDRESS_LINE_2,
                    "phone": HEADER_PHONE,
                    "website": HEADER_WEBSITE,
                    "email": HEADER_EMAIL,
                    "rc": HEADER_RC,
                    "nif": HEADER_NIF,
                    "nis": HEADER_NIS,
                    "article": HEADER_ARTICLE
                }
            },

            "invoiceDetails": {
                "invoiceTitle": INVOICE_TITLE,
                "accountNo": INVOICE_ACCOUNT_NO,
                "invoiceDate": INVOICE_DATE,
                "issueDate": INVOICE_ISSUE_DATE
            },

            "billTo": {
                "name": BILL_TO_NAME,
                "addressLine1": f"{BILL_TO_ADDRESS_LINE}",
                "addressLine2": f"{BILL_TO_ADDRESS_LINE_2}",
                "email": f"{BILL_TO_EMAIL}",
                "phone": f"{BILL_TO_PHONE}",
                "nif": f"NIF: {BILL_TO_NIF}",
                "nis": f"NIS: {BILL_TO_NIS}",
                "rc": f"RC: {BILL_TO_RC}",
                "article": f"Article: {BILL_TO_ARTICLE}"
            },

            "items": entries,

            "paymentMethod": {
                "paymentMethod1": PAYMENT_METHOD_1
                
            },

            "totals": {
                "deliveryCost": 0, # Will be calculated dynamically
                "currencySign": CURRENCY_SIGN,
                "decimalPoint": DECIMAL_POINT,
                "subTotal": 0, # Will be calculated dynamically
                "discountPercent": DISCOUNT_PERCENT,
                "discountAmount": 0, # Will be calculated dynamically
                "taxPercent": TAX_PERCENT,
                "taxAmount": 0, # Will be calculated dynamically
                "grandTotal": 0 # Will be calculated dynamically
            },
            
            "thankYouMessage": {
                "heading": TY_MSG_HEADING,
                "notesLine1": TY_MSG_NOTES_LINE_1,
                "notesLine2": TY_MSG_NOTES_LINE_2
            },

            "signature": {
                "name": SIGNATURE_NAME,
                "fullName": SIGNATURE_FULLNAME,
                "title": SIGNATURE_TITLE
            }
        }

        # Recalculate totals based on items
        calculated_sub_total = sum(item['total'] for item in invoice_data['items'])
        #invoice_data['totals']['subTotal'] = calculated_sub_total
        calculated_discount_amount = (invoice_data['totals']['discountPercent'] / 100) * calculated_sub_total
        calculated_tax_amount = (invoice_data['totals']['taxPercent'] / 100) * calculated_sub_total
        calculated_total_ttc = calculated_sub_total + calculated_tax_amount + DELIVERY_COST
        calculated_grand_total = calculated_total_ttc - calculated_discount_amount


        # Convert the totals from DINAR to SELECTED CURRENCY
        
        invoice_data['items'] = self.convert_unit_price_and_total_ht(entries, CURRENCY_SIGN)
        #print(invoice_data['items'])
        converted_totals = self.convert_totals(currency_sign=CURRENCY_SIGN, 
                            sub_total = calculated_sub_total,
                            discount_amount = calculated_discount_amount,
                            tax_amount = calculated_tax_amount,
                            total_ttc = calculated_total_ttc,
                            grand_total = calculated_grand_total,
                            delivery_cost = DELIVERY_COST
                            )


        invoice_data['totals']['subTotal'] = converted_totals["sub_total"]
        invoice_data['totals']['discountAmount'] = converted_totals["discount_amount"]
        invoice_data['totals']['taxAmount'] = converted_totals["tax_amount"]
        invoice_data['totals']['total_ttc'] = converted_totals["total_ttc"]
        invoice_data['totals']['grandTotal'] = converted_totals["grand_total"]
        invoice_data['totals']['deliveryCost'] = converted_totals["delivery_cost"]

        try:
            pdf = PDFGenerator(file_path)
            pdf.create_pdf(invoice_data)
            messagebox.showinfo("Success", f"PDF saved successfully at:\n{file_path}")
        except Exception as e:
            messagebox.showerror("PDF Error", str(e))



if __name__ == "__main__":
    root = tk.Tk()
    app = UserFormApp(root)
    root.mainloop()
