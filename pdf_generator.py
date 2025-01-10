from fpdf import FPDF
import segno
import os
import sqlite3
from tkinter import filedialog
from profile import load_profile  # Assuming this function is defined elsewhere
from shared import items  # Import items from the shared module
from PIL import Image  # Import Pillow for image resizing

class PDF(FPDF):
    def footer(self):
        # Set the initial position for the footer
        self.set_y(-25)

        # Add a thank-you message
        self.set_font('Arial', 'I', 10)
        self.set_text_color(50, 50, 50)
        self.cell(0, 5, 'Thank you for your business!', align='C', ln=True)

        # Load profile data
        profile = load_profile() or {}

        # Extract available information
        email = profile.get("email", "example@gmail.com")
        phone_no = profile.get("phone_no", "+91 1234567890")
        website = profile.get("website", None)
        social_media = profile.get("facebook_instagram_id", "@examplebusiness")

        # Add contact information in one line
        contact_info = f"Contact us: {email} | {phone_no}"
        self.set_font('Arial', '', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, contact_info, align='C', ln=True)

        # Add website or social media line
        if website:
            self.cell(0, 5, f'Visit us: {website}', align='C', ln=True)
        else:
            self.cell(0, 5, f'Follow us: {social_media}', align='C', ln=True)

        # Ensure page number is always on a separate line
        self.set_y(-10)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 5, f'Page {self.page_no()}/{self.alias_nb_pages()}', 0, 0, 'C')

def resize_logo(input_path, output_path, size=(600, 600)):
    with Image.open(input_path) as img:
        # Preserve aspect ratio using LANCZOS resampling
        img.thumbnail(size, Image.LANCZOS)

        # Create a blank square canvas
        new_img = Image.new("RGBA", size, (255, 255, 255, 0))  # White background with transparency

        # Calculate the position to paste the resized image
        paste_position = ((size[0] - img.width) // 2, (size[1] - img.height) // 2)

        # Paste the resized image onto the canvas
        new_img.paste(img, paste_position)

        # Save the resized image
        new_img.save(output_path, format="PNG")

def store_to_db(data):
    conn = sqlite3.connect('invoices.db')
    cursor = conn.cursor()

    # List of required columns and their types
    required_columns = {
        "invoice_date": "TEXT",
        "invoice_number": "TEXT",
        "customer_name": "TEXT",
        "customer_address_line1": "TEXT",
        "customer_address_line2": "TEXT",
        "customer_pin_code": "TEXT",
        "contact": "TEXT",
        "items": "TEXT",
        "total_amount": "REAL"
    }

    # Check if the table exists and get its columns
    cursor.execute("PRAGMA table_info(invoices)")
    columns = cursor.fetchall()

    # Extract column names from the existing table
    column_names = [column[1] for column in columns]

    # Add missing columns if necessary
    for column_name, column_type in required_columns.items():
        if column_name not in column_names:
            cursor.execute(f"ALTER TABLE invoices ADD COLUMN {column_name} {column_type}")

    # Create table if it doesn't exist with the correct schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            invoice_date TEXT,
            invoice_number TEXT,
            customer_name TEXT,
            customer_address_line1 TEXT,
            customer_address_line2 TEXT,
            customer_pin_code TEXT,
            contact TEXT,
            items TEXT,
            total_amount REAL
        )
    ''')

    # Validate and convert items to a string
    try:
        items_str = str(data['items'])
    except Exception as e:
        print(f"Error converting items to string: {e}")
        items_str = "[]"

    # Insert the data into the table
    cursor.execute('''
        INSERT INTO invoices (
            invoice_date, invoice_number, customer_name, customer_address_line1,
            customer_address_line2, customer_pin_code, contact, items, total_amount
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['invoice_date'], data['invoice_number'], data['customer_name'],
        data['customer_address_line1'], data['customer_address_line2'], data['customer_pin_code'],
        data['contact'], items_str, data['total_amount']
    ))

    conn.commit()
    conn.close()

def generate_pdf(invoice_date, invoice_number, customer_name, customer_address_line1, customer_address_line2, customer_pin_code, contact):
    profile = load_profile()

    pdf = PDF()
    pdf.alias_nb_pages()  # Allow for total page count
    pdf.add_page()

    # Add logo if available
    if profile.get('logo'):
        resized_logo_path = "resized_logo.png"
        resize_logo(profile['logo'], resized_logo_path)  # Resize the logo
        pdf.image(resized_logo_path, 10, 10, 30)  # Place resized logo on the left
        os.remove(resized_logo_path)  # Clean up the temporary resized logo file
    pdf.ln(5)

    # Add invoice title and number
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 10, 'INVOICE', align='C', ln=True)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 6, f"Invoice No: {invoice_number}", align='R', ln=True)
    pdf.cell(0, 6, f"Date: {invoice_date}", align='R', ln=True)
    pdf.ln(10)  # Add a small space after the date

    # Add business and customer details side by side
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(100, 10, 'BILLED TO:', ln=0)  # "Billed to" stays on the left
    pdf.cell(0, 10, 'FROM:', align='R', ln=True)  # "From" on the right

    pdf.set_font('Arial', '', 12)
    pdf.cell(100, 7, customer_name, ln=0)  # Customer name on the left
    pdf.cell(0, 7, profile.get('business_name', 'Business Name Not Provided'), align='R', ln=True)

    pdf.cell(100, 7, customer_address_line1, ln=0)  # Customer address line 1 on the left
    pdf.cell(0, 7, profile.get('address_line_1', 'Address Line 1 Not Provided'), align='R', ln=True)

    if customer_address_line2:
        pdf.cell(100, 7, customer_address_line2, ln=0)  # Customer address line 2 on the left
        pdf.cell(0, 7, profile.get('address_line_2', ''), align='R', ln=True)
    else:
        pdf.cell(100, 7, '', ln=0)  # Empty line for second address line
        pdf.cell(0, 7, profile.get('address_line_2', ''), align='R', ln=True)

    pdf.cell(100, 7, f"Pin Code: {customer_pin_code}", ln=0)  # Customer Pin Code on the left
    pdf.cell(0, 7, f"Pin Code: {profile.get('pin_code', 'Pin Code Not Provided')}", align='R', ln=True)

    pdf.ln(10)

    # Table Headers
    pdf.set_x(7.5)  # Adjust table's starting x-coordinate to move it even further left
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(20, 10, 'Sl. No.', border=1, align='C')
    pdf.cell(100, 10, 'Item Description', border=1, align='C')
    pdf.cell(25, 10, 'Qty', border=1, align='C')
    pdf.cell(25, 10, 'Rate', border=1, align='C')
    pdf.cell(25, 10, 'Amount', border=1, align='C', ln=True)

    # Table Rows
    pdf.set_font('Arial', '', 12)
    total_amount = 0
    for index, item in enumerate(items, start=1):
        sl_no, description, qty, rate, total = item

        # Check remaining space on the page
        if pdf.get_y() + 20 > 270:  # 270 is the approximate space left on the page for rows and QR code
            pdf.add_page()  # Add a new page if there's not enough space

        pdf.set_x(7.5)  # Set x-coordinate for each row

        # Increase the line height
        line_height = pdf.font_size * 1.65  # Adjust the multiplier to increase row height
        description_lines = pdf.multi_cell(100, line_height, description, border=0, align='L', split_only=True)
        cell_height = max(line_height, len(description_lines) * line_height)

        # Shade every second row
        shaded = (index % 2 == 0)
        if shaded:
            pdf.set_fill_color(240, 240, 240)
        else:
            pdf.set_fill_color(255, 255, 255)

        # Create cells for each column, ensuring they all have the same height
        pdf.cell(20, cell_height, str(sl_no), border=1, align='C', fill=shaded)
        x, y = pdf.get_x(), pdf.get_y()
        pdf.multi_cell(100, line_height, description, border=1, align='L', fill=shaded)
        pdf.set_xy(x + 100, y)  # Move to the next cell position
        pdf.cell(25, cell_height, str(qty), border=1, align='C', fill=shaded)
        pdf.cell(25, cell_height, f"{rate:,.2f}", border=1, align='C', fill=shaded)
        pdf.cell(25, cell_height, f"{total:,.2f}", border=1, align='C', ln=True, fill=shaded)  # Adds commas

        total_amount += total

    # Total Amount Row
    pdf.set_x(7.5)  # Align the total row with the table
    pdf.set_font('Arial', 'B', 12)
    pdf.set_fill_color(200, 220, 255)  # Light blue background for the total row
    pdf.cell(170, 10, 'Total', border=1, fill=True, align='C')
    pdf.cell(25, 10, f"{total_amount:,.2f}", border=1, fill=True, align='C', ln=True)  # Adds commas

    # QR Code for UPI Payment
    if profile.get('upi_id'):
        upi_url = (
            f"upi://pay?pa={profile['upi_id']}&pn={profile['business_name']}"
            f"&am={total_amount:.2f}&cu=INR&tn=Payment for Invoice"
        )
        qr_code = segno.make(upi_url)
        qr_code_path = "upi_qr_code.png"
        qr_code.save(qr_code_path)

        # Add a row for the QR code in the table format
        if pdf.get_y() + 35 > 240:  # Ensure there's enough space for the QR code row
            pdf.add_page()

        pdf.set_x(7.5)  # Align with the table
        pdf.set_font('Arial', 'B', 12)
        pdf.set_fill_color(240, 240, 240)  # Light gray background for the QR code row
        pdf.cell(195, 35, 'Scan the QR code for payment', border=1, fill=True, align='C')
        pdf.image(qr_code_path, x=170, y=pdf.get_y() + 2.5, w=30, h=30)  # Place QR on the right in the cell

        os.remove(qr_code_path)  # Clean up the temporary file

    # Save the PDF
    save_path = filedialog.asksaveasfilename(
        defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")]
    )
    if save_path:
        pdf.output(save_path)
        # Store to database after PDF is saved
        data = {
            'invoice_date': invoice_date,
            'invoice_number': invoice_number,
            'customer_name': customer_name,
            'customer_address_line1': customer_address_line1,
            'customer_address_line2': customer_address_line2,
            'customer_pin_code': customer_pin_code,
            'contact': contact,
            'items': items,  # Ensure items list only contains necessary values
            'total_amount': total_amount
        }
        store_to_db(data)

