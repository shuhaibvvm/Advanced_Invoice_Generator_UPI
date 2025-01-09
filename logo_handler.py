from tkinter import filedialog
import os

def upload_logo(logo_path_label):
    logo_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if logo_path:
        logo_filename = os.path.basename(logo_path)
        logo_path_label.configure(text="Logo uploaded: " + logo_filename)
        return logo_path
    return None