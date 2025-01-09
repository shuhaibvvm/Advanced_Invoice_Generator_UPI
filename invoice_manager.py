import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv

def open_invoice_manager():
    # Create a new window
    invoice_window = ctk.CTkToplevel()
    invoice_window.title("Invoice Manager")
    invoice_window.geometry("1000x600")

    # Create a frame for the Treeview
    frame = ctk.CTkFrame(invoice_window)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Create a Treeview to display the invoices
    columns = ("Invoice Number", "Invoice Date", "Customer Name", "Address Line 1", "Address Line 2",
               "Pin Code", "Contact", "Total Amount")
    treeview = ttk.Treeview(frame, columns=columns, show="headings", height=20)
    treeview.pack(fill="both", expand=True)

    # Define column headings
    for col in columns:
        treeview.heading(col, text=col)

    # Define column width
    column_widths = [100, 100, 200, 200, 200, 100, 150, 100]
    for col, width in zip(columns, column_widths):
        treeview.column(col, width=width, anchor="center")

    # Fetch data from the SQLite database
    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute("SELECT invoice_number, invoice_date, customer_name, customer_address_line1, customer_address_line2, customer_pin_code, contact, total_amount FROM invoices")
    for row in cursor.fetchall():
        treeview.insert("", "end", values=row)
    conn.close()

    # Bind the Delete key to the delete_selected_row function
    treeview.bind("<Delete>", lambda event: delete_selected_row(treeview))

    # Create an export button
    export_button = ctk.CTkButton(invoice_window, text="Export", command=lambda: export_data(treeview))
    export_button.pack(pady=10)

def export_data(treeview):
    # Ask the user where to save the CSV file
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return  # User canceled the save dialog

    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow([treeview.heading(col)["text"] for col in treeview["columns"]])
        # Write the data
        for row in treeview.get_children():
            writer.writerow(treeview.item(row)["values"])

    messagebox.showinfo("Export", "Data exported successfully to " + file_path)

def delete_selected_row(treeview):
    selected_item = treeview.selection()
    if not selected_item:
        messagebox.showwarning("Delete", "No item selected")
        return

    # Get the invoice number of the selected row
    invoice_number = treeview.item(selected_item, "values")[0]

    # Confirm deletion
    confirm = messagebox.askyesno("Delete", f"Are you sure you want to delete the invoice {invoice_number}?")
    if not confirm:
        return

    # Delete from the database
    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM invoices WHERE invoice_number = ?", (invoice_number,))
    conn.commit()
    conn.close()

    # Delete from the Treeview
    treeview.delete(selected_item)
    messagebox.showinfo("Delete", f"Invoice {invoice_number} deleted successfully")

# Example usage: open_invoice_manager()
# Run the following function in your main script to open the invoice manager window.
# open_invoice_manager()