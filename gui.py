import tkinter as tk
from tkinter import ttk, messagebox, filedialog
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
from dateutil.relativedelta import relativedelta


class UserFormApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Generator")
        self.root.geometry("1200x700")

        self.model_variants = {
            "Square": csv_carre_keys_list,
            "Hexagonal": csv_hexa_keys_list,
            "Frieze": csv_frise_keys_list,
            "Berber Carpet": csv_tapis_keys_list,
            "Baguettes": csv_baguettes_keys_list
        }

        self.variant_price_map = csv_baguettes_dict

        self.color_choices = csv_couleur_keys_list
        self.entries_data = []

        self.create_widgets()

        self.add_entry_row()  # Add one row initially

    def create_widgets(self):
        # Title
        title = tk.Label(self.root, text="PDF GENERATOR FORM", font=("Arial", 24))
        title.pack(pady=10)

        # Personal Details
        client_frame = tk.LabelFrame(self.root, text="Personal Details", padx=10, pady=10)
        client_frame.pack(fill="x", padx=20, pady=10)

        # Full Name
        tk.Label(client_frame, text="Full Name:").grid(row=0, column=0, sticky="w")
        self.full_name = tk.Entry(client_frame, width=40)
        self.full_name.grid(row=0, column=1, padx=5, pady=5)

        # Address
        tk.Label(client_frame, text="Address:").grid(row=0, column=2, sticky="w")
        self.address = tk.Entry(client_frame, width=40)
        self.address.grid(row=0, column=3, padx=5, pady=5)

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
        tk.Button(self.root, text="Add Entry", bg="green", fg="white", command=self.add_entry_row).pack(pady=10)

        # Table Frame
        table_container = tk.Frame(self.root)
        table_container.pack(padx=20, fill="both", expand=True)

        canvas = tk.Canvas(table_container)
        scrollbar = tk.Scrollbar(table_container, orient="vertical", command=canvas.yview)
        self.table_frame = tk.Frame(canvas)

        self.table_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.table_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

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

        tk.Button(bottom_frame, text="Generate PDF", bg="green", fg="white", command=self.generate_pdf).pack(side="left", padx=10)
        tk.Button(bottom_frame, text="Close", bg="red", fg="white", command=self.root.quit).pack(side="left", padx=10)

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
            color_cb['values'] = self.color_choices
            color_cb.grid(row=row_index, column=2 + i)
            row_widgets[f"Color{i}"] = color_var
    
        delete_btn = tk.Button(self.table_frame, text="Delete", bg="red", fg="white",
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
            qty_str = row["Quantity"].get()
            qty = int(qty_str) if qty_str.strip().isdigit() and int(qty_str) > 0 else 1
            selected_model = row["Model"].get()
            selected_variant = row["Variant"].get()
            variant_price = self.get_variant_price(selected_model, selected_variant)
            unit_amount = variant_price + color_prices_average
            total_amount = unit_amount * qty

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
        invoice_number = f"INV-{unique_id.hex[:9].upper()}"  # Take first 12 chars of UUID
        return invoice_number

    def get_invoice_current_date(self):
        return datetime.now().strftime("%d %b, %Y")

    
    def get_invoice_issue_date(self, months=3):
        #Default: 3 months ahead
        future_date = datetime.now() + relativedelta(months=months)
        return future_date.strftime("%d %b, %Y")

    def has_missing_model(self, entries):
        return any(not entry.get('model') for entry in entries)
    

    def generate_pdf(self):

        invoice_no = self.generate_invoice_number()
        invoice_date = self.get_invoice_current_date()
        invoice_issue_date = self.get_invoice_issue_date()

        full_name = self.full_name.get().strip()
        address = self.address.get().strip()
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

        # Header details
        HEADER_COMPANY_NAME = "COMPANY NAME"
        HEADER_LOGO_PATH = "logo.png"
        HEADER_ADDRESS_LINE_1 = "1377 Maxwell Farm Road" 
        HEADER_ADDRESS_LINE_2 = "Reno, CA 89503"
        HEADER_PHONE = "+01-252-555-0099"
        HEADER_WEBSITE = "www.yourdomain.com"
        HEADER_EMAIL = "info@yourmail.com"

        # Invoice details
        INVOICE_ACCOUNT_NO = invoice_no
        INVOICE_DATE = invoice_date
        INVOICE_ISSUE_DATE = invoice_issue_date

        BILL_TO_NAME = full_name
        BILL_TO_ADDRESS_LINE = address
        BILL_TO_EMAIL = email
        BILL_TO_PHONE = phone
        BILL_TO_NIF = nif
        BILL_TO_NIS = nis
        BILL_TO_RC = rc
        BILL_TO_ARTICLE = article
        
        PAYMENT_METHOD_1 = "paypal.username@outlook.com"
        PAYMENT_METHOD_2 = "Visa, Mastercard, Paypal"
        
        # Total computation
        DISCOUNT_PERCENT = 10
        TAX_PERCENT = 17

        # Thank you message
        TY_MSG_HEADING = "Terms & Conditions:"
        TY_MSG_NOTES_LINE_1 = "• Above magna aliquarn erat volulpat ad minim veniam, quis nostrud"
        TY_MSG_NOTES_LINE_2 = "• Exercitation ullamco laboris nisi ut aliquip ex ea commodo"

        SIGNATURE_NAME = "Anne-Kahina Yessad"
        SIGNATURE_TITLE =  "Manager"
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
                    "email": HEADER_EMAIL
                }
            },

            "invoiceDetails": {
                "accountNo": INVOICE_ACCOUNT_NO,
                "invoiceDate": INVOICE_DATE,
                "issueDate": INVOICE_ISSUE_DATE
            },

            "billTo": {
                "name": BILL_TO_NAME,
                "addressLine1": f"Address: {BILL_TO_ADDRESS_LINE}",
                "email": f"Email: {BILL_TO_EMAIL}",
                "phone": f"Phone:{BILL_TO_PHONE}",
                "nif": f"NIF: {BILL_TO_NIF}",
                "nis": f"NIS: {BILL_TO_NIS}",
                "rc": f"RC: {BILL_TO_RC}",
                "article": f"Article: {BILL_TO_ARTICLE}"
            },

            "items": entries,

            "paymentMethod": {
                "paymentMethod1": PAYMENT_METHOD_1,
                "paymentMethod2": PAYMENT_METHOD_2
            },

            "totals": {
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
                "title": SIGNATURE_TITLE
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
