import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pdf_generator import PDFGenerator
from model import (
    csv_carre_keys_list,
    csv_hexa_keys_list,
    csv_frise_keys_list,
    csv_tapis_keys_list,
    csv_baguettes_keys_list
)

from color import csv_couleur_keys_list

print(csv_couleur_keys_list)

class UserFormApp:
    """Main application class for the user form."""
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Generator")
        self.root.geometry("600x1000")
        self.root.resizable(False, False)

        # Model to Variants mapping
        self.model_variants = {
            "Square": csv_carre_keys_list,
            "Hexagonal": csv_hexa_keys_list,
            "Frieze": csv_frise_keys_list,
            "Berber Carpet": csv_tapis_keys_list,
            "Baguettes": csv_baguettes_keys_list
        }

        self.color_choices = csv_couleur_keys_list
        self.entries = []  # Store all added model/variant/color entries

        self.create_widgets()

    def create_widgets(self):
        """Create and layout the widgets."""
        # First Name
        tk.Label(self.root, text="First Name:").pack(pady=(10, 0))
        self.entry_first_name = tk.Entry(self.root, width=50)
        self.entry_first_name.pack()

        # Last Name
        tk.Label(self.root, text="Last Name:").pack(pady=(10, 0))
        self.entry_last_name = tk.Entry(self.root, width=50)
        self.entry_last_name.pack()

        # Contact Details
        tk.Label(self.root, text="Contact Details:").pack(pady=(10, 0))
        self.entry_contact = tk.Entry(self.root, width=50)
        self.entry_contact.pack()

        # Address
        tk.Label(self.root, text="Address:").pack(pady=(10, 0))
        self.entry_address = tk.Entry(self.root, width=50)
        self.entry_address.pack()

        # Section for adding model/variant/color entries
        self.entry_section = tk.LabelFrame(self.root, text="Add Entry", padx=10, pady=10)
        self.entry_section.pack(pady=(20, 0), fill="x")

        # Model Dropdown
        tk.Label(self.entry_section, text="Model:").grid(row=0, column=0, sticky="w")
        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(self.entry_section, textvariable=self.model_var, state="readonly", width=20)
        self.model_combo['values'] = list(self.model_variants.keys())
        self.model_combo.grid(row=0, column=1, padx=5, pady=5)
        self.model_combo.bind("<<ComboboxSelected>>", self.update_variant_dropdown)

        # Variant Dropdown
        tk.Label(self.entry_section, text="Variant:").grid(row=1, column=0, sticky="w")
        self.variant_var = tk.StringVar()
        self.variant_combo = ttk.Combobox(self.entry_section, textvariable=self.variant_var, state="readonly", width=20)
        self.variant_combo.grid(row=1, column=1, padx=5, pady=5)

        # Color Selection
        tk.Label(self.entry_section, text="Select up to 5 Colors:").grid(row=2, column=0, sticky="w", pady=(10, 0), columnspan=2)
        color_frame = tk.Frame(self.entry_section)
        color_frame.grid(row=3, column=0, columnspan=2)

        self.color_listbox = tk.Listbox(color_frame, selectmode="multiple", height=6, width=30, exportselection=False)
        self.color_listbox.pack(side="left", fill="y")

        color_scrollbar = tk.Scrollbar(color_frame, orient="vertical")
        color_scrollbar.pack(side="right", fill="y")

        self.color_listbox.config(yscrollcommand=color_scrollbar.set)
        color_scrollbar.config(command=self.color_listbox.yview)

        for color in self.color_choices:
            self.color_listbox.insert(tk.END, color)

        self.color_status_var = tk.StringVar()
        self.color_status_label = tk.Label(self.entry_section, textvariable=self.color_status_var)
        self.color_status_label.grid(row=4, column=0, columnspan=2)
        self.color_listbox.bind("<<ListboxSelect>>", self.on_color_select)

        # Add Entry Button
        tk.Button(self.entry_section, text="Add Entry", command=self.add_entry).grid(row=5, column=0, columnspan=2, pady=(10, 0))

        # Preview of added entries
        tk.Label(self.root, text="Added Entries:").pack(pady=(20, 0))
        self.entries_preview = tk.Listbox(self.root, height=6, width=70)
        self.entries_preview.pack()

        # Generate PDF Button
        tk.Button(self.root, text="Generate PDF", command=self.generate_pdf).pack(pady=20)

    def update_variant_dropdown(self, event):
        selected_model = self.model_var.get()
        variants = self.model_variants.get(selected_model, [])
        self.variant_combo['values'] = variants
        if variants:
            self.variant_combo.current(0)
        else:
            self.variant_combo.set('')

    def on_color_select(self, event):
        selected_indices = self.color_listbox.curselection()
        if len(selected_indices) > 5:
            self.color_listbox.selection_clear(selected_indices[-1])
            messagebox.showwarning("Limit Reached", "You can select up to 5 colors only.")
        self.update_color_status()

    def update_color_status(self):
        count = len(self.color_listbox.curselection())
        self.color_status_var.set(f"Selected Colors: {count} / 5")

    def add_entry(self):
        model = self.model_var.get().strip()
        variant = self.variant_var.get().strip()
        selected_colors = [self.color_choices[i] for i in self.color_listbox.curselection()]

        if not model or not variant:
            messagebox.showerror("Input Error", "Please select both model and variant.")
            return

        if not (1 <= len(selected_colors) <= 5):
            messagebox.showerror("Input Error", "Please select between 1 and 5 colors.")
            return

        entry = {
            "Model": model,
            "Variant": variant,
            "Colors": selected_colors
        }

        self.entries.append(entry)
        color_str = ", ".join(selected_colors)
        self.entries_preview.insert(tk.END, f"{model} - {variant} - {color_str}")

        # Reset inputs
        self.model_var.set("")
        self.variant_var.set("")
        self.variant_combo['values'] = []
        self.color_listbox.selection_clear(0, tk.END)
        self.update_color_status()

    def generate_pdf(self):
        first_name = self.entry_first_name.get().strip()
        last_name = self.entry_last_name.get().strip()
        contact = self.entry_contact.get().strip()
        address = self.entry_address.get().strip()

        if not all([first_name, last_name, contact, address]):
            messagebox.showerror("Input Error", "Please fill in all personal details.")
            return

        if not self.entries:
            messagebox.showerror("Input Error", "Please add at least one model entry.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save PDF"
        )

        if not file_path:
            return  # User cancelled

        data = {
            "First Name": first_name,
            "Last Name": last_name,
            "Contact": contact,
            "Address": address,
            "Entries": self.entries  # List of dicts: Model, Variant, Colors
        }

        pdf_generator = PDFGenerator(file_path)
        try:
            pdf_generator.create_pdf(data)
            messagebox.showinfo("Success", f"PDF saved successfully at:\n{file_path}")
        except IOError as e:
            messagebox.showerror("Error", str(e))


# Only run this if this file is run directly (not imported)
if __name__ == "__main__":
    root = tk.Tk()
    app = UserFormApp(root)
    root.mainloop()
