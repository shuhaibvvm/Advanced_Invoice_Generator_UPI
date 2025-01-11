def save_only():
    if not validate_entries():
        return

    invoice_number = invoice_number_entry.get().strip()
    invoice_date = invoice_date_entry.get()
    customer_name = customer_name_entry.get().strip()
    customer_address_line1 = customer_address_line1_entry.get().strip()
    customer_address_line2 = customer_address_line2_entry.get().strip()
    pin_code = pin_code_entry.get().strip()  # Ensure the pin_code is retrieved correctly
    contact = contact_entry.get().strip()

    # Debugging print statement to check pin_code
    print(f"Pin Code Retrieved in Save Only: {pin_code}")

    if not pin_code:
        messagebox.showerror("Missing Pin Code", "Please enter a valid pin code before saving.")
        return

    item_list = [
        treeview.item(row)["values"] for row in treeview.get_children()
    ]

    if not item_list:
        messagebox.showerror("No Items", "Please add at least one item before saving the invoice.")
        return

    # Calculate the total amount, converting each total to float
    try:
        total_amount = sum(float(item[4]) for item in item_list)  # Assuming the 5th column is the total
    except ValueError as e:
        messagebox.showerror("Error", f"An error occurred while calculating the total amount: {e}")
        return

    # Ask for confirmation before saving the invoice
    confirm_save = messagebox.askyesno("Save Invoice", "Are you sure you want to save this invoice?")

    if not confirm_save:
        return

    try:
        # Save data to the database without generating the PDF
        save_only_to_db(invoice_date, invoice_number, customer_name, customer_address_line1, customer_address_line2, pin_code, contact, item_list, total_amount)

        messagebox.showinfo("Invoice Saved", "The invoice has been successfully saved to the database.")
        # Update the invoice number to the next one
        next_invoice_number = get_next_invoice_number()
        invoice_number_entry.delete(0, tk.END)
        invoice_number_entry.insert(0, next_invoice_number)

        clear_all()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while saving the invoice: {e}")