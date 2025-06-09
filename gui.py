import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pdf_generator import PDFGenerator  # Ensure you have this module
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
        tk.Label(client_frame, text="Phone Number:").grid(row=1, column=0, sticky="w")
        self.phone = tk.Entry(client_frame, width=40)
        self.phone.grid(row=1, column=1, padx=5, pady=5)

        # Email
        tk.Label(client_frame, text="Email:").grid(row=1, column=2, sticky="w")
        self.email = tk.Entry(client_frame, width=40)
        self.email.grid(row=1, column=3, padx=5, pady=5)

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
        headers = ["Model", "Variant", "Qty", "Color 1", "Color 2", "Color 3", "Color 4", "Color 5", "Amount", "Delete"]
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

        qty_entry = tk.Entry(self.table_frame, width=12)
        qty_entry.grid(row=row_index, column=2)
        row_widgets["Quantity"] = qty_entry

        for i in range(1, 6):
            color_var = tk.StringVar()
            color_cb = ttk.Combobox(self.table_frame, textvariable=color_var, state="readonly", width=20)
            color_cb['values'] = self.color_choices
            color_cb.grid(row=row_index, column=2 + i)
            row_widgets[f"Color{i}"] = color_var

        amount_var = tk.StringVar()
        amount_entry = tk.Entry(self.table_frame, textvariable=amount_var, state="readonly", width=12)
        amount_entry.grid(row=row_index, column=8)
        row_widgets["Amount"] = amount_var

        # Bind the variant dropdown to get the Amount automatically
        #variant_cb.bind("<<ComboboxSelected>>", lambda e, var_cb=variant_cb, amt_var=amount_entry: self.update_amount(var_cb, amt_var))
        def update_amount(event=None):
            selected_model = model_var.get()
            selected_variant = variant_var.get()

            # refactor thsi later, use enums
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
                    print("Invalid model")
            
            row_widgets["Variant_Price"] = price
            #amount_var.set(str(price))

        variant_cb.bind("<<ComboboxSelected>>", update_amount)
    
        delete_btn = tk.Button(self.table_frame, text="Delete", bg="red", fg="white",
                               command=lambda r=row_index: self.delete_entry_row(r))
        delete_btn.grid(row=row_index, column=9)
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


    def collect_entry_data(self):
        data = []
        for row in self.entries_data:
            if row is None:
                continue

            color_arr = [row[f"Color{i}"].get() for i in range(1, 6)]
            color_prices_arr = [csv_couleur_dict.get(row[f"Color{i}"].get()) for i in range(1, 6)]
            color_prices_average = self.average_prices(color_prices_arr)
            qty_str = row["Quantity"].get()
            qty = int(qty_str) if qty_str.strip().isdigit() else 1
            variant_price = row["Variant_Price"]
            unit_amount = int(variant_price) + color_prices_average
            total_amount = unit_amount * qty

            entry = {
                "Model": row["Model"].get(),
                "Variant": row["Variant"].get(),
                "Variant_Price": row["Variant_Price"],
                "Quantity": row["Quantity"].get(),
                "Colors": color_arr,
                "Colors_Prices": color_prices_arr,
                "Colors_Prices_Average": color_prices_average,
                "Unit_Amount": unit_amount,
                "Total_Amount": total_amount
            }
            
            data.append(entry)
        return data

    def generate_pdf(self):
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
        if not entries:
            messagebox.showerror("Input Error", "Please add at least one entry.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            return

        data = {
            "Full Name": full_name,
            "Address": address,
            "Phone": phone,
            "Email": email,
            "Nif": nif,
            "Nis": nis,
            "RC": rc,
            "Article": article,
            "Entries": entries
        }
        
        print(data)

        try:
            pdf = PDFGenerator(file_path)
            pdf.create_pdf(data)
            messagebox.showinfo("Success", f"PDF saved successfully at:\n{file_path}")
        except Exception as e:
            messagebox.showerror("PDF Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = UserFormApp(root)
    root.mainloop()
