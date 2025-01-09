import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import customtkinter as ctk
from profile import open_profile_form, is_profile_filled
from pdf_generator import generate_pdf
import re
import datetime
import sqlite3
from tkcalendar import DateEntry
from shared import items
from invoice_manager import get_next_invoice_number, open_invoice_manager  # Add this import

# Configure the custom theme for a professional look
ctk.set_appearance_mode("light")  # Modes: "light", "dark"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue", "green", "dark-blue"

# Create a window for the application
app = ctk.CTk()
app.iconbitmap("my_icon.ico")
app.title("GST Invoice Generator")
app.geometry("1300x800")
app.resizable(True, True)

# Add a frame for the input and preview sections
main_frame = ctk.CTkFrame(app, corner_radius=15, fg_color="#EAEDED")
main_frame.pack(fill="both", expand=True, padx=20, pady=20)

# Adjust the width of the input_frame
input_frame = ctk.CTkFrame(main_frame, width=600, corner_radius=10, fg_color="#D5DBDB")  # Increased width from 400 to 600
input_frame.pack(side="left", fill="y", padx=15, pady=15)

# Right section for preview (scrollable)
preview_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color="#FFFFFF")
preview_frame.pack(side="right", fill="both", expand=True, padx=15, pady=15)

# Title for the application
header_label = ctk.CTkLabel(input_frame, text="Invoice Generator", font=("Helvetica", 22, "bold"),
                            text_color="#1F618D")
header_label.grid(row=0, column=0, columnspan=2, pady=20)

# Invoice details input
invoice_number_label = ctk.CTkLabel(input_frame, text="Invoice Number", anchor="w", font=("Helvetica", 16))
invoice_number_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
invoice_number_entry = ctk.CTkEntry(input_frame, placeholder_text="Enter Invoice Number", height=30)
invoice_number_entry.grid(row=1, column=1, padx=10, pady=5)

# Set the next invoice number automatically
invoice_number_entry.insert(0, get_next_invoice_number())

# Replace the original invoice date entry with a DateEntry
invoice_date_label = ctk.CTkLabel(input_frame, text="Invoice Date", anchor="w", font=("Helvetica", 16))
invoice_date_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
invoice_date_entry = DateEntry(input_frame, date_pattern='dd/MM/yyyy', font=("Helvetica", 12),
                               width=16, background='darkblue', foreground='white',
                               borderwidth=2, justify='center')
invoice_date_entry.grid(row=2, column=1, padx=10, pady=5, ipady=5)

# Customer details input
customer_name_label = ctk.CTkLabel(input_frame, text="Customer Name", anchor="w", font=("Helvetica", 16))
customer_name_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
customer_name_entry = ctk.CTkEntry(input_frame, placeholder_text="Enter Customer Name", height=30)
customer_name_entry.grid(row=3, column=1, padx=10, pady=5)

customer_address_line1_label = ctk.CTkLabel(input_frame, text="Address Line 1", anchor="w", font=("Helvetica", 16))
customer_address_line1_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
customer_address_line1_entry = ctk.CTkEntry(input_frame, placeholder_text="Enter Address Line 1", height=30)
customer_address_line1_entry.grid(row=4, column=1, padx=10, pady=5)

customer_address_line2_label = ctk.CTkLabel(input_frame, text="Address Line 2", anchor="w", font=("Helvetica", 16))
customer_address_line2_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")
customer_address_line2_entry = ctk.CTkEntry(input_frame, placeholder_text="Enter Address Line 2", height=30)
customer_address_line2_entry.grid(row=5, column=1, padx=10, pady=5)

# Add pin code input
pin_code_label = ctk.CTkLabel(input_frame, text="Pin Code", anchor="w", font=("Helvetica", 16))
pin_code_label.grid(row=6, column=0, padx=10, pady=5, sticky="w")
pin_code_entry = ctk.CTkEntry(input_frame, placeholder_text="Enter Pin Code", height=30)
pin_code_entry.grid(row=6, column=1, padx=10, pady=5)

contact_label = ctk.CTkLabel(input_frame, text="Contact", anchor="w", font=("Helvetica", 16))
contact_label.grid(row=7, column=0, padx=10, pady=5, sticky="w")
contact_entry = ctk.CTkEntry(input_frame, placeholder_text="Enter Contact Number", height=30)
contact_entry.grid(row=7, column=1, padx=10, pady=5)

item_description_label = ctk.CTkLabel(input_frame, text="Item Description", anchor="w", font=("Helvetica", 16))
item_description_label.grid(row=8, column=0, padx=10, pady=5, sticky="w")
item_description_entry = ctk.CTkEntry(input_frame, placeholder_text="Enter Item Description", height=30)
item_description_entry.grid(row=8, column=1, padx=10, pady=5)

quantity_label = ctk.CTkLabel(input_frame, text="Quantity", anchor="w", font=("Helvetica", 16))
quantity_label.grid(row=9, column=0, padx=10, pady=5, sticky="w")
quantity_entry = ctk.CTkEntry(input_frame, placeholder_text="Enter Quantity", height=30)
quantity_entry.grid(row=9, column=1, padx=10, pady=5)

rate_label = ctk.CTkLabel(input_frame, text="Rate", anchor="w", font=("Helvetica", 16))
rate_label.grid(row=10, column=0, padx=10, pady=5, sticky="w")
rate_entry = ctk.CTkEntry(input_frame, placeholder_text="Enter Rate", height=30)
rate_entry.grid(row=10, column=1, padx=10, pady=5)

# Add item button
add_item_button = ctk.CTkButton(input_frame, text="Add Item", fg_color="#2980B9", text_color="#ffffff", height=35,
                                command=lambda: add_item_entry(item_description_entry, quantity_entry, rate_entry,
                                                                treeview))
add_item_button.grid(row=12, column=0, columnspan=2, pady=15)

def on_entry_return(event, next_widget):
    next_widget.focus_set()

# Add this function to handle keyboard shortcuts
def handle_shortcut(event, button):
    button.invoke()

# Bind the Enter key to navigate to the next field
invoice_number_entry.bind("<Return>", lambda event: on_entry_return(event, invoice_date_entry))
invoice_date_entry.bind("<Return>", lambda event: on_entry_return(event, customer_name_entry))
customer_name_entry.bind("<Return>", lambda event: on_entry_return(event, customer_address_line1_entry))
customer_address_line1_entry.bind("<Return>", lambda event: on_entry_return(event, customer_address_line2_entry))
customer_address_line2_entry.bind("<Return>", lambda event: on_entry_return(event, pin_code_entry))
pin_code_entry.bind("<Return>", lambda event: on_entry_return(event, contact_entry))
contact_entry.bind("<Return>", lambda event: on_entry_return(event, item_description_entry))
item_description_entry.bind("<Return>", lambda event: on_entry_return(event, quantity_entry))
quantity_entry.bind("<Return>", lambda event: on_entry_return(event, rate_entry))
rate_entry.bind("<Return>", lambda event: on_entry_return(event, add_item_button))


# Add the shortcut key bindings
app.bind("<Control-a>", lambda event: handle_shortcut(event, add_item_button))
app.bind("<Control-g>", lambda event: handle_shortcut(event, generate_pdf_button))
app.bind("<Control-c>", lambda event: handle_shortcut(event, clear_all_button))
app.bind("<Control-i>", lambda event: handle_shortcut(event, profile_button))
app.bind("<Control-q>", lambda event: open_invoice_manager())  # Add this binding

def is_valid_date(date):
    # Regex pattern for validating date in DD/MM/YYYY format
    pattern = r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$"
    return re.match(pattern, date) is not None

def is_valid_pin_code(pin_code):
    # Remove any leading or trailing spaces
    pin_code = pin_code.strip()
    # Regex pattern for validating pin code (assuming a 6-digit pin code)
    pattern = r"^\d{6}$"
    return re.match(pattern, pin_code) is not None

def is_valid_contact(contact):
    # Check if contact is a valid 10-digit phone number
    if re.match(r'^\d{10}$', contact):
        return True
    # Check if contact is a valid email address ending with @gmail.com
    elif re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', contact):
        return True
    return False

def validate_entries():
    missing_fields = []

    if not invoice_number_entry.get():
        missing_fields.append("Invoice Number")
    if not invoice_date_entry.get():
        missing_fields.append("Invoice Date")
    elif not is_valid_date(invoice_date_entry.get()):
        messagebox.showerror("Invalid Date", "Please enter a valid date in the format DD/MM/YYYY.")
        return False
    if not customer_name_entry.get():
        missing_fields.append("Customer Name")
    if not customer_address_line1_entry.get():
        missing_fields.append("Address Line 1")
    if not customer_address_line2_entry.get():
        missing_fields.append("Address Line 2")
    pin_code = pin_code_entry.get().strip()
    if not pin_code:
        missing_fields.append("Pin Code")
    elif not is_valid_pin_code(pin_code):
        messagebox.showerror("Invalid Pin Code", "Please enter a valid 6-digit pin code.")
        return False
    contact = contact_entry.get().strip()
    if not contact:
        missing_fields.append("Contact")
    elif not is_valid_contact(contact):
        messagebox.showerror("Invalid Contact", "Please enter a valid 10-digit phone number or a Gmail address ending with @gmail.com.")
        return False

    if missing_fields:
        messagebox.showerror("Missing Fields", f"Please fill in the following fields: {', '.join(missing_fields)}.")
        return False

    return True

# The rest of your code remains the same...

def update_total(treeview, total_label):
    total = 0
    for row in treeview.get_children():
        total += float(treeview.item(row)["values"][4])  # Get the total (last column)
    total_label.configure(text=f"Total: ₹{round(total, 2)}")

def add_item_entry(item_description_entry, quantity_entry, rate_entry, treeview):
    # Validate entries first (checking the basic form fields)
    if not validate_entries():
        return

    # Ensure the invoice number is set
    if not invoice_number_entry.get():
        invoice_number_entry.insert(0, get_next_invoice_number())

    try:
        # Get and clean the input values by stripping spaces
        quantity = float(quantity_entry.get().strip()) if quantity_entry.get().strip() else None
        rate = float(rate_entry.get().strip()) if rate_entry.get().strip() else None
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numbers for Quantity and Rate.")
        return

    # Calculate total amount
    total_amount = quantity * rate

    # Get the serial number for the new item
    sl_no = len(treeview.get_children()) + 1

    # Add the item to the list
    items.append((sl_no, item_description_entry.get(), quantity, rate, round(total_amount, 2)))

    # Insert the item into the treeview (preview section)
    treeview.insert("", "end", values=(sl_no, item_description_entry.get(), quantity, rate, round(total_amount, 2)))

    # Clear input fields
    item_description_entry.delete(0, tk.END)
    quantity_entry.delete(0, tk.END)
    rate_entry.delete(0, tk.END)

    update_total(treeview, total_label)

    # Set focus to the item_description_entry after adding an item
    item_description_entry.focus_set()

def generate_invoice(treeview):
    # If preview section is empty, show error message
    if not treeview.get_children():  # No items in the preview
        messagebox.showerror("Preview Empty", "Please add items to the preview before generating the invoice.")
    else:
        # Proceed with invoice generation
        print("Generating invoice...")

def on_generate_pdf_click():
    if not is_profile_filled():
        messagebox.showwarning(
            "Incomplete Profile",
            "Please ensure that both the company name and contact number are filled."
        )
        return

    if not validate_entries():
        return

    invoice_number = invoice_number_entry.get().lstrip()
    invoice_date = invoice_date_entry.get()
    customer_name = customer_name_entry.get().lstrip()
    customer_address_line1 = customer_address_line1_entry.get().lstrip()
    customer_address_line2 = customer_address_line2_entry.get().lstrip()
    pin_code = pin_code_entry.get().strip()
    contact = contact_entry.get().strip()

    item_list = [
        treeview.item(row)["values"] for row in treeview.get_children()
    ]

    if not item_list:
        messagebox.showerror("No Items", "Please add at least one item before generating the invoice.")
        return

    generate_pdf(invoice_date, invoice_number, customer_name.title(), customer_address_line1.title(), customer_address_line2.title(), pin_code,contact)

# Generate PDF button
generate_pdf_button = ctk.CTkButton(input_frame, text="Generate PDF", fg_color="#27AE60", text_color="#ffffff",
                                    height=40, command=on_generate_pdf_click)
generate_pdf_button.grid(row=13, column=0, columnspan=2, pady=10)

# Enter Company Info button
profile_button = ctk.CTkButton(input_frame, text="Enter Company Info", fg_color="#34495E", text_color="#ffffff",
                               height=40, command=open_profile_form)
profile_button.grid(row=14, column=0, columnspan=2, pady=10)

def clear_all():
    # Check if all input fields are empty
    if (not customer_name_entry.get() and not customer_address_line1_entry.get() and
        not customer_address_line2_entry.get() and not pin_code_entry.get() and
        not contact_entry.get() and not item_description_entry.get() and
        not quantity_entry.get() and not rate_entry.get() and not treeview.get_children()):
        # Show dialog box indicating that all fields are empty
        messagebox.showinfo("All Fields Empty", "All input fields are already empty.")
        return

    # Do not clear invoice number and invoice date
    # Clear only user-editable fields
    customer_name_entry.delete(0, tk.END)
    customer_address_line1_entry.delete(0, tk.END)
    customer_address_line2_entry.delete(0, tk.END)
    pin_code_entry.delete(0, tk.END)
    contact_entry.delete(0, tk.END)
    item_description_entry.delete(0, tk.END)
    quantity_entry.delete(0, tk.END)
    rate_entry.delete(0, tk.END)

    # Clear the treeview items
    for row in treeview.get_children():
        treeview.delete(row)

    # Clear items list and reset total label
    items.clear()
    total_label.configure(text="Total: ₹0.00")

    # Reset focus to the first editable input field
    customer_name_entry.focus_set()
# Clear All button
clear_all_button = ctk.CTkButton(input_frame, text="Clear All", fg_color="#E74C3C", text_color="#ffffff", height=40,
                                 command=clear_all)
clear_all_button.grid(row=15, column=0, columnspan=2, pady=10)


def setup_treeview(preview_frame):
    # Create a Scrollbar for the Treeview widget
    treeview_scrollbar = ttk.Scrollbar(preview_frame, orient="vertical")

    # Create a Treeview for Excel-like table preview
    treeview = ttk.Treeview(preview_frame, columns=("Sl No", "Item", "Quantity", "Rate", "Total"), show="headings",
                            height=20, yscrollcommand=treeview_scrollbar.set)

    # Center the Treeview widget inside the preview_frame
    treeview.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    # Configure grid weight to allow resizing and centering
    preview_frame.grid_rowconfigure(0, weight=1)
    preview_frame.grid_columnconfigure(0, weight=1)

    # Attach the scrollbar to the Treeview widget
    treeview_scrollbar.config(command=treeview.yview)
    treeview_scrollbar.grid(row=0, column=1, sticky="ns")  # Position the scrollbar beside Treeview

    # Define column headings
    treeview.heading("Sl No", text="Sl No")
    treeview.heading("Item", text="Item Description")
    treeview.heading("Quantity", text="Quantity")
    treeview.heading("Rate", text="Rate")
    treeview.heading("Total", text="Total")

    # Define column width
    treeview.column("Sl No", width=50, anchor="center")
    treeview.column("Item", width=400, anchor="w")
    treeview.column("Quantity", width=150, anchor="center")
    treeview.column("Rate", width=150, anchor="center")
    treeview.column("Total", width=150, anchor="center")

    # Style the Treeview
    style = ttk.Style()
    style.configure("Treeview",
                    background="#EAEDED",
                    foreground="#000000",
                    fieldbackground="#FFFFFF",
                    font=("Helvetica", 14),  # Increase font size for values
                    rowheight=40)  # Increase row height
    style.configure("Treeview.Heading", font=("Helvetica", 16, "bold"))  # Increase font size for headings
    style.map("Treeview",
              background=[('selected', '#2980B9')],
              foreground=[('selected', '#FFFFFF')])

    # Add the total label at the bottom of the preview_frame
    total_label = ctk.CTkLabel(preview_frame, text="Total: ₹0.00", font=("Helvetica", 20, "bold"), text_color="black")
    total_label.grid(row=1, column=0, columnspan=2, pady=10)

    return treeview, total_label


# Integrate the new setup_treeview function into your code
treeview, total_label = setup_treeview(preview_frame)


def on_item_double_click(event):
    selected_item = treeview.selection()
    if selected_item:
        item_values = treeview.item(selected_item)["values"]
        if len(item_values) < 5:  # Ensure there are enough values
            messagebox.showerror("Invalid Item", "Selected item data is incomplete or corrupted.")
            return

        # Populate the entry fields with the item data
        item_description_entry.delete(0, tk.END)
        item_description_entry.insert(0, item_values[1])  # Item description is in the second column

        quantity_entry.delete(0, tk.END)
        quantity_entry.insert(0, item_values[2])  # Quantity is in the third column

        rate_entry.delete(0, tk.END)
        rate_entry.insert(0, item_values[3])  # Rate is in the fourth column

        # Change the button to "Update Item" and update the command to update the selected item
        add_item_button.configure(text="Update Item", command=lambda: update_item(selected_item))


def update_item(selected_item):
    # Get the new values from the entry fields
    item_description = item_description_entry.get()
    try:
        quantity = float(quantity_entry.get())
        rate = float(rate_entry.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numeric values for Quantity and Rate.")
        return

    # Calculate the updated total
    total_amount = quantity * rate

    # Get the original serial number
    sl_no = treeview.item(selected_item)["values"][0]

    # Update the selected item in the treeview
    treeview.item(selected_item, values=(sl_no, item_description, quantity, rate, round(total_amount, 2)))

    # Clear the entry fields
    item_description_entry.delete(0, tk.END)
    quantity_entry.delete(0, tk.END)
    rate_entry.delete(0, tk.END)

    # Restore the "Add Item" button functionality
    add_item_button.configure(text="Add Item", command=lambda: add_item_entry(
        item_description_entry, quantity_entry, rate_entry, treeview
    ))

    # Update the total label
    update_total(treeview, total_label)


# Function to delete an item from the treeview and confirm the deletion
def on_item_delete(event):
    selected_item = treeview.selection()
    if selected_item:
        # Get the item description
        item_description = treeview.item(selected_item)["values"][1]  # Corrected index to 1

        # Ask for confirmation before deleting the item
        confirm_delete = messagebox.askyesno("Delete Item",
                                             f"Are you sure you want to delete the item '{item_description}'?")

        if confirm_delete:
            # Delete the item
            treeview.delete(selected_item)
            # Clear the entry fields and reset the button text to "Add Item"
            item_description_entry.delete(0, tk.END)
            quantity_entry.delete(0, tk.END)
            rate_entry.delete(0, tk.END)

            add_item_button.configure(text="Add Item", command=lambda: add_item_entry(
                item_description_entry, quantity_entry, rate_entry, treeview))

            # Update the total after deletion
            update_total(treeview, total_label)


# Bind double-click event to handle item editing
treeview.bind("<Double-1>", on_item_double_click)

# Bind delete key event to handle item deletion
treeview.bind("<Delete>", on_item_delete)

# Run the application
app.mainloop()