import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import shutil

class Settings:
    def __init__(self, root, existing_settings=None):
        self.root = root
        self.window = tk.Toplevel(self.root)
        self.window.title("Settings")
        self.window.geometry("700x850")
        self.logo_path = ""

        self.existing_settings = existing_settings or {}
        self.create_widgets()

    def create_widgets(self):
        # Company Information Section
        company_frame = tk.LabelFrame(self.window, text="Company Information", padx=10, pady=10)
        company_frame.pack(fill="x", padx=10, pady=5)

        self.companyName = self.create_entry(company_frame, "Company Name:", 0)
        self.addressLine1 = self.create_entry(company_frame, "Address Line 1:", 1)
        self.addressLine2 = self.create_entry(company_frame, "Address Line 2:", 2)
        self.phone = self.create_entry(company_frame, "Phone:", 3)
        self.email = self.create_entry(company_frame, "Email:", 4)
        self.rc = self.create_entry(company_frame, "RC:", 5)
        self.nif = self.create_entry(company_frame, "Nif:", 6)
        self.nis = self.create_entry(company_frame, "Nis:", 7)
        self.article = self.create_entry(company_frame, "Article:", 8)
        
        tk.Label(company_frame, text="Logo:").grid(row=9, column=0, sticky="w")
        self.logo_label = tk.Label(company_frame, text="No file selected")
        self.logo_label.grid(row=9, column=1, sticky="w")
        tk.Button(company_frame, text="Upload Image", command=self.upload_logo).grid(row=9, column=2, padx=5)

        company = self.existing_settings.get("company", {})
        self.companyName.insert(0, company.get("companyName", ""))
        self.addressLine1.insert(0, company.get("addressLine1", ""))
        self.addressLine2.insert(0, company.get("addressLine2", ""))
        self.phone.insert(0, company.get("phone", ""))
        self.email.insert(0, company.get("email", ""))
        self.rc.insert(0, company.get("rc", ""))
        self.nif.insert(0, company.get("nif", ""))
        self.nis.insert(0, company.get("nis", ""))
        self.article.insert(0, company.get("article", ""))
        self.logo_path = company.get("logoPath", "")
        self.logo_label.config(text=os.path.basename(self.logo_path) if self.logo_path else "No file selected")

        # Invoice Section
        invoice_frame = tk.LabelFrame(self.window, text="Invoice", padx=10, pady=10)
        invoice_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(invoice_frame, text="Invoice Title:").grid(row=0, column=0, sticky="w")
        self.invoice_title_var = tk.StringVar(value="Proforma")
        tk.Radiobutton(invoice_frame, text="Proforma", variable=self.invoice_title_var, value="Proforma").grid(row=0, column=1)
        tk.Radiobutton(invoice_frame, text="Invoice", variable=self.invoice_title_var, value="Invoice").grid(row=0, column=2)

        tk.Label(invoice_frame, text="Invoice Validity:").grid(row=1, column=0, sticky="w")
        self.validity_number = tk.Entry(invoice_frame, width=5)
        self.validity_number.grid(row=1, column=1, sticky="w")
        self.validity_duration = ttk.Combobox(invoice_frame, values=["day", "week", "month", "year"], state="readonly", width=10)
        self.validity_duration.grid(row=1, column=2, sticky="w")

        tk.Label(invoice_frame, text="Mode of Payment:").grid(row=2, column=0, sticky="w")
        self.payment_cheque = tk.BooleanVar()
        self.payment_especes = tk.BooleanVar()
        self.payment_virement = tk.BooleanVar()
        tk.Checkbutton(invoice_frame, text="Cheque", variable=self.payment_cheque).grid(row=2, column=1, sticky="w")
        tk.Checkbutton(invoice_frame, text="espèces", variable=self.payment_especes).grid(row=2, column=2, sticky="w")
        tk.Checkbutton(invoice_frame, text="virement", variable=self.payment_virement).grid(row=2, column=3, sticky="w")

        tk.Label(invoice_frame, text="Currency:").grid(row=3, column=0, sticky="w")
        self.currency_var = tk.StringVar(value="Euro")
        tk.Radiobutton(invoice_frame, text="DA (Dinar)", variable=self.currency_var, value="DA").grid(row=3, column=1, sticky="w")
        tk.Radiobutton(invoice_frame, text="$ (US Dollar)", variable=self.currency_var, value="$",).grid(row=3, column=2, sticky="w")
        tk.Radiobutton(invoice_frame, text="€ (Euro)", variable=self.currency_var, value="EUR").grid(row=3, column=3, sticky="w")

        tk.Label(invoice_frame, text="Decimal Point:").grid(row=4, column=0, sticky="w")
        self.decimal_var = tk.StringVar(value="Period")
        tk.Radiobutton(invoice_frame, text="Period", variable=self.decimal_var, value=".").grid(row=4, column=1, sticky="w")
        tk.Radiobutton(invoice_frame, text="Comma", variable=self.decimal_var, value=",").grid(row=4, column=2, sticky="w")

        self.tax = self.create_entry(invoice_frame, "Tax Percent:", 5)
        self.discount = self.create_entry(invoice_frame, "Discount Percent:", 6)

        invoice = self.existing_settings.get("invoice", {})
        self.invoice_title_var.set(invoice.get("title", "Proforma"))
        validity = invoice.get("validity", {})
        self.validity_number.insert(0, validity.get("number", "1"))
        self.validity_duration.set(validity.get("duration", "month"))
        modes = invoice.get("modeOfPayment", [])
        self.payment_cheque.set("cheque" in modes)
        self.payment_especes.set("espèces" in modes)
        self.payment_virement.set("virement" in modes)
        self.currency_var.set(invoice.get("currency", "Euro"))
        self.decimal_var.set(invoice.get("decimalPoint", "Period"))
        self.tax.insert(0, str(invoice.get("tax", "19")))
        self.discount.insert(0, str(invoice.get("discount", "10")))

        # Terms Section
        terms_frame = tk.LabelFrame(self.window, text="Terms and Condition", padx=10, pady=10)
        terms_frame.pack(fill="x", padx=10, pady=5)
        
        self.termsLabel = self.create_entry(terms_frame, "Terms Label:", 0)
        self.termsLine1 = self.create_entry(terms_frame, "Terms Line 1:", 1)
        self.termsLine2 = self.create_entry(terms_frame, "Terms Line 2:", 2)

        terms = self.existing_settings.get("terms", {})
        self.termsLabel.insert(0, terms.get("termsLabel", ""))
        self.termsLine1.insert(0, terms.get("termsLine1", ""))
        self.termsLine2.insert(0, terms.get("termsLine2", ""))

        # Signature Section
        signature_frame = tk.LabelFrame(self.window, text="Signature", padx=10, pady=10)
        signature_frame.pack(fill="x", padx=10, pady=5)

        self.nameCursive = self.create_entry(signature_frame, "Name Cursive:", 0)
        self.fullName = self.create_entry(signature_frame, "Full Name:", 1)
        self.position = self.create_entry(signature_frame, "Position:", 2)

        signature = self.existing_settings.get("signature", {})
        self.nameCursive.insert(0, signature.get("nameCursive", ""))
        self.fullName.insert(0, signature.get("fullName", ""))
        self.position.insert(0, signature.get("position", ""))

        # Save Button
        tk.Button(self.window, text="Save", command=self.save_settings).pack(pady=20)

    def create_entry(self, parent, label_text, row):
        tk.Label(parent, text=label_text).grid(row=row, column=0, sticky="w")
        entry = tk.Entry(parent, width=50)
        entry.grid(row=row, column=1, columnspan=3, sticky="w")
        return entry

    def upload_logo(self):
        filepath = filedialog.askopenfilename(
            title="Select Logo Image",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")]
        )
        if filepath:
            # Create logos folder if not exist
            os.makedirs("images", exist_ok=True)

            filename = os.path.basename(filepath)
            dest_path = os.path.join("images", filename)

            # Copy the file
            shutil.copy2(filepath, dest_path)

            self.logo_path = dest_path  # store relative local path
            self.logo_label.config(text=filename)

    def save_settings(self):
        data = {
            "company": {
                "companyName": self.companyName.get(),
                "logoPath": self.logo_path,
                "addressLine1": self.addressLine1.get(),
                "addressLine2": self.addressLine2.get(),
                "phone": self.phone.get(),
                "email": self.email.get(),
                "rc": self.rc.get(),
                "nif": self.nif.get(),
                "nis": self.nis.get(),
                "article": self.article.get()
            },
            "invoice": {
                "title": self.invoice_title_var.get(),
                "validity": {
                    "number": int(self.validity_number.get()),
                    "duration": self.validity_duration.get()
                },
                "modeOfPayment": self.get_mode_of_payment(),
                "currency": self.currency_var.get(),
                "decimalPoint": self.decimal_var.get(),
                "tax": float(self.tax.get()),
                "discount": float(self.discount.get())
            },
            "terms": {
                "termsLabel": self.termsLabel.get(),
                "termsLine1": self.termsLine1.get(),
                "termsLine2": self.termsLine2.get()
            },
            "signature": {
                "nameCursive": self.nameCursive.get(),
                "fullName": self.fullName.get(),
                "position": self.position.get()
            }
        }

        # Save to file
        with open("settings.json", "w") as f:
            json.dump(data, f, indent=4)

        messagebox.showinfo("Settings Saved", "Settings successfully saved!")
        self.window.destroy()

    def get_mode_of_payment(self):
        modes = []
        if self.payment_cheque.get():
            modes.append("cheque")
        if self.payment_especes.get():
            modes.append("espèces")
        if self.payment_virement.get():
            modes.append("virement")
        return modes
