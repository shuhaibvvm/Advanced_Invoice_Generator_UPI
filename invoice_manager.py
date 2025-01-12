import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
import re

# Global variable to keep track of the Invoice Manager window
invoice_manager_window = None

def get_next_invoice_number():
    conn = sqlite3.connect('invoices.db')
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT invoice_number FROM invoices")
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            cursor.execute("""
                CREATE TABLE invoices (
                    invoice_number TEXT PRIMARY KEY,
                    invoice_date TEXT,
                    customer_name TEXT,
                    customer_address_line1 TEXT,
                    customer_address_line2 TEXT,
                    customer_pin_code TEXT,
                    contact TEXT,
                    total_amount REAL,
                    items TEXT
                )
            """)
            conn.commit()
            invoices = []
        else:
            raise
    else:
        invoices = cursor.fetchall()

    conn.close()

    if not invoices:
        return '001'

    invoice_numbers = [invoice[0] for invoice in invoices]
    max_number = 0
    max_custom_invoice = None

    for invoice in invoice_numbers:
        match = re.match(r'(\D*)(\d+)', invoice)
        if match:
            prefix, number = match.groups()
            number = int(number)
            if prefix == '':
                max_number = max(max_number, number)
            else:
                if max_custom_invoice is None or (prefix == max_custom_invoice[0] and number > max_custom_invoice[1]):
                    max_custom_invoice = (prefix, number)

    if max_custom_invoice:
        prefix, number = max_custom_invoice
        next_invoice = f"{prefix}{number + 1:03d}"
    else:
        next_invoice = f"{max_number + 1:03d}"

    return next_invoice


def open_invoice_manager():
    global invoice_manager_window

    if invoice_manager_window is not None and invoice_manager_window.winfo_exists():
        # If the window is already open, bring it to the front
        invoice_manager_window.focus_force()
        return

    # Create the window
    invoice_manager_window = ctk.CTkToplevel()
    invoice_manager_window.title("Invoice Manager")
    invoice_manager_window.geometry("1200x700")  # Larger default size
    invoice_manager_window.resizable(True, True)  # Allow resizing (normal window behavior)

    # Frame for the main content
    frame = ctk.CTkFrame(invoice_manager_window)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Treeview columns
    columns = ("Invoice Number", "Invoice Date", "Customer Name", "Address Line 1", "Address Line 2",
               "Pin Code", "Contact", "Total Amount", "Items")
    treeview = ttk.Treeview(frame, columns=columns, show="headings")
    treeview.pack(fill="both", expand=True)

    # Configure column headings
    for col in columns:
        treeview.heading(col, text=col)

    # Set column widths (adjust as needed)
    column_widths = [100, 100, 200, 200, 200, 100, 150, 100, 200]
    for col, width in zip(columns, column_widths):
        treeview.column(col, width=width, anchor="center")

    # Add data to the Treeview
    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT invoice_number, invoice_date, customer_name, customer_address_line1, customer_address_line2, customer_pin_code, contact, total_amount, items FROM invoices"
    )

    total_value = 0
    for index, row in enumerate(cursor.fetchall()):
        tag = 'evenrow' if index % 2 == 0 else 'oddrow'
        invoice_number, invoice_date, customer_name, address_line1, address_line2, pin_code, contact, total_amount, items = row

        # Handle None for total_amount
        total_amount = float(total_amount) if total_amount is not None else 0.0

        # Format items
        try:
            item_list = eval(items)
            formatted_items = ', '.join([str(item[1]) for item in item_list])
        except Exception:
            formatted_items = items

        # Insert into Treeview
        treeview.insert("", "end", values=(invoice_number, invoice_date, customer_name, address_line1,
                                           address_line2, pin_code, contact, total_amount, formatted_items), tags=(tag,))
        total_value += total_amount
    conn.close()

    # Style Treeview rows
    treeview.tag_configure('evenrow', background='#E8F0FE')  # Light blue for even rows
    treeview.tag_configure('oddrow', background='#FFFFFF')   # White for odd rows

    # Add Total Value and Export Button in a bottom frame
    bottom_frame = ctk.CTkFrame(invoice_manager_window)
    bottom_frame.pack(fill="x", pady=10, padx=20)

    # Align Total Value and Export Button using grid
    bottom_frame.grid_columnconfigure(0, weight=0)  # Left side for Total Value
    bottom_frame.grid_columnconfigure(1, weight=1)  # Spacer
    bottom_frame.grid_columnconfigure(2, weight=0)  # Right side for Export Button

    # Total Value Label (aligned to the left)
    total_label = ctk.CTkLabel(
        bottom_frame,
        text=f"Total Value: ₹{total_value:.2f}",
        font=("Arial", 14),
        fg_color="#1E3A8A",
        text_color="white",
        corner_radius=6,
        width=200
    )
    total_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")  # Align left

    # Export Button (aligned to the right)
    export_button = ctk.CTkButton(
        bottom_frame,
        text="Export",
        command=lambda: export_data(treeview, invoice_manager_window),
        fg_color="#1E3A8A",
        text_color="white",
        corner_radius=6
    )
    export_button.grid(row=0, column=2, padx=10, pady=10, sticky="e")  # Align right

    # Treeview delete row on key press
    treeview.bind("<Delete>", lambda event: delete_selected_row(treeview))

def export_data(treeview, invoice_window):
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        parent=invoice_window  # Set the parent window
    )
    if not file_path:
        return

    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([treeview.heading(col)["text"] for col in treeview["columns"]])
        for row in treeview.get_children():
            writer.writerow(treeview.item(row)["values"])

    messagebox.showinfo(
        "Export",
        "Data exported successfully to " + file_path,
        parent=invoice_window  # Set the parent window
    )

def delete_selected_row(treeview):
    selected_item = treeview.selection()
    if not selected_item:
        messagebox.showwarning("Delete", "No item selected", parent=treeview)
        return

    invoice_number = treeview.item(selected_item, "values")[0]
    confirm = messagebox.askyesno(
        "Delete",
        f"Are you sure you want to delete the invoice {invoice_number}?",
        parent=treeview
    )
    if not confirm:
        return

    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM invoices WHERE invoice_number = ?", (invoice_number,))
    conn.commit()
    conn.close()

    treeview.delete(selected_item)
    messagebox.showinfo("Delete", f"Invoice {invoice_number} deleted successfully", parent=treeview)