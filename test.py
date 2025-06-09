import tkinter as tk

class PlaceholderText(tk.Text):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey', **kwargs):
        super().__init__(master, **kwargs)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._show_placeholder)

        self._show_placeholder()

    def _show_placeholder(self, event=None):
        if not self.get("1.0", "end-1c"):
            self.insert("1.0", self.placeholder)
            self['fg'] = self.placeholder_color

    def _clear_placeholder(self, event=None):
        if self['fg'] == self.placeholder_color:
            self.delete("1.0", "end")
            self['fg'] = self.default_fg_color

    def get_content(self):
        # Returns content, excluding placeholder
        if self['fg'] == self.placeholder_color:
            return ''
        return self.get("1.0", "end-1c")


# Example usage
root = tk.Tk()
placeholder_text = PlaceholderText(root, placeholder="Enter your message here...", width=40, height=10)
placeholder_text.pack(padx=10, pady=10)

root.mainloop()