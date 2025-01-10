import customtkinter as ctk
import json
import os
from tkinter import filedialog
import tkinter.messagebox as messagebox
import winsound

profile_file = "user_profile.json"
default_profile = {
    "business_name": "",
    "address_line_1": "",
    "address_line_2": "",
    "upi_id": "",
    "logo": "",
    "email": "",
    "phone_no": "",
    "website": "",
    "facebook_instagram_id": "",
    "pin_code": ""
}

profile_form_open = False
sound_played = False  # Flag to track if the sound has been played

# Save the profile data to a JSON file
def save_profile(business_name_entry, address_line_1_entry, address_line_2_entry, upi_id_entry, logo_path, email_entry, phone_no_entry, website_entry, facebook_instagram_id_entry, pin_code_entry):
    profile = {
        "business_name": business_name_entry.get().title().lstrip(),
        "address_line_1": address_line_1_entry.get().title().lstrip(),
        "address_line_2": address_line_2_entry.get().title().lstrip(),
        "upi_id": upi_id_entry.get().lstrip(),
        "logo": logo_path,
        "email": email_entry.get().lstrip(),
        "phone_no": phone_no_entry.get().lstrip(),
        "website": website_entry.get().lstrip(),
        "facebook_instagram_id": facebook_instagram_id_entry.get().lstrip(),
        "pin_code": pin_code_entry.get().strip(),
    }
    with open(profile_file, 'w') as file:
        json.dump(profile, file)

# Load the profile data from a JSON file
def load_profile():
    try:
        with open(profile_file, 'r') as file:
            profile = json.load(file)
            for key, default_value in default_profile.items():
                if key not in profile:
                    profile[key] = default_value
            return profile
    except (FileNotFoundError, json.JSONDecodeError):
        return default_profile

# Move focus to the next widget
def focus_next_widget(event):
    event.widget.tk_focusNext().focus()
    return "break"

# Validate the pin code
def validate_pin_code(pin_code):
    return pin_code.isdigit() and len(pin_code) == 6

# Validate the phone number
def validate_phone_number(phone_no):
    return phone_no.isdigit() and len(phone_no) == 10

# Validate the email address
def validate_email(email):
    return email.endswith("@gmail.com")

# Switch to the specified section and set focus on the specified entry
def switch_and_focus(section, entry):
    show_frame(section)
    entry.focus_set()

# Show the specified frame
def show_frame(frame_name):
    for name, button in nav_buttons.items():
        button.configure(fg_color="#808080")
    nav_buttons[frame_name].configure(fg_color="#007acc")
    for frame in frames.values():
        frame.pack_forget()
    frames[frame_name].pack(fill="both", expand=True, padx=20, pady=20)

# Open the profile form
def open_profile_form():
    global profile_form_open, nav_buttons, frames
    if profile_form_open:
        return
    profile_form_open = True
    profile = load_profile()

    form_window = ctk.CTkToplevel()
    form_window.title("Company Profile")
    form_window.logo_path = profile.get("logo", "")
    form_window.attributes('-topmost', 1)
    form_window.protocol("WM_DELETE_WINDOW", lambda: close_form(form_window))

    form_window.geometry("730x725")
    form_window.resizable(False, False)

    # Main Frame
    main_frame = ctk.CTkFrame(form_window, fg_color="#f0f0f0", corner_radius=15)
    main_frame.pack(padx=20, pady=20, fill="both", expand=True)

    # Title Label
    title_label = ctk.CTkLabel(main_frame, text="Edit Company Profile", font=("Arial", 26, "bold"), text_color="#333333")
    title_label.pack(pady=(30, 20))

    # Navigation Buttons
    nav_frame = ctk.CTkFrame(main_frame, fg_color="#eaeaea", corner_radius=15)
    nav_frame.pack(fill="x", padx=30, pady=10)

    nav_frame.grid_columnconfigure((0, 1, 2), weight=1)

    nav_buttons = {}
    frames = {}

    # Add navigation buttons
    for idx, name in enumerate(["Company Info", "Contact Info", "Logo"]):
        frames[name] = ctk.CTkFrame(main_frame, fg_color="#ffffff", corner_radius=15)
        nav_buttons[name] = ctk.CTkButton(
            nav_frame,
            text=name,
            command=lambda n=name: show_frame(n),
            fg_color="#007acc" if idx == 0 else "#808080",
            hover_color="#005a99",
            width=150
        )
        nav_buttons[name].grid(row=0, column=idx, padx=10, pady=10)

    # Initialize the first frame
    show_frame("Company Info")

    # Populate "Company Info" Frame
    labels = {
        "Business Name": "business_name",
        "Address Line 1": "address_line_1",
        "Address Line 2": "address_line_2",
        "UPI ID": "upi_id",
        "Pin Code": "pin_code"
    }

    entries = {}
    for row, (label_text, key) in enumerate(labels.items()):
        ctk.CTkLabel(frames["Company Info"], text=label_text, font=("Arial", 16, "bold"), text_color="#444444").grid(row=row, column=0, padx=20, pady=15, sticky="w")
        entry = ctk.CTkEntry(frames["Company Info"], width=450, font=("Arial", 14), fg_color="#eaeaea")
        entry.insert(0, profile[key])
        entry.grid(row=row, column=1, padx=20, pady=15)
        entry.bind("<Return>", focus_next_widget)
        entries[key] = entry

    # Populate "Contact Info" Frame
    labels = {
        "Email": "email",
        "Phone No": "phone_no",
        "Website (optional)": "website",
        "Facebook/Instagram ID": "facebook_instagram_id"
    }

    for row, (label_text, key) in enumerate(labels.items()):
        ctk.CTkLabel(frames["Contact Info"], text=label_text, font=("Arial", 16, "bold"), text_color="#444444").grid(row=row, column=0, padx=20, pady=15, sticky="w")
        entry = ctk.CTkEntry(frames["Contact Info"], width=400, font=("Arial", 14), fg_color="#eaeaea")
        entry.insert(0, profile[key])
        entry.grid(row=row, column=1, padx=20, pady=15)
        entry.bind("<Return>", focus_next_widget)
        entries[key] = entry

    # Populate "Logo" Frame
    logo_path_label = ctk.CTkLabel(
        frames["Logo"],
        text=f"Logo uploaded: {os.path.basename(profile['logo'])}" if profile['logo'] else "No logo uploaded",
        font=("Arial", 14),
        text_color="#555555"
    )
    logo_path_label.pack(pady=30)

    def upload_logo_callback():
        logo_path = filedialog.askopenfilename(
            parent=form_window,
            title="Select a logo",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
        )
        if logo_path:
            form_window.logo_path = logo_path
            file_name = os.path.basename(logo_path)
            logo_path_label.configure(text=f"Logo uploaded: {file_name}")
            logo_path_label.update()

    upload_button = ctk.CTkButton(
        frames["Logo"],
        text="Upload Logo",
        command=upload_logo_callback,
        fg_color="#4caf50",
        hover_color="#388e3c",
        width=250,
        height=40
    )
    upload_button.pack(pady=15)

    def remove_logo():
        form_window.logo_path = ""
        logo_path_label.configure(text="No logo uploaded")
        logo_path_label.update()

    remove_button = ctk.CTkButton(
        frames["Logo"],
        text="Remove",
        command=remove_logo,
        fg_color="#f44336",
        hover_color="#d32f2f",
        width=250,
        height=40
    )
    remove_button.pack(pady=15)

    # Save and Close Buttons
    button_frame = ctk.CTkFrame(main_frame, fg_color="#ffffff")
    button_frame.pack(padx=20, pady=30, fill="x", side="bottom")

    save_button = ctk.CTkButton(
        button_frame,
        text="Save",
        command=lambda: save_and_close(
            form_window,
            entries["business_name"],
            entries["address_line_1"],
            entries["address_line_2"],
            entries["upi_id"],
            entries["email"],
            entries["phone_no"],
            entries["website"],
            entries["facebook_instagram_id"],
            entries["pin_code"]
        ),
        fg_color="#007acc",
        hover_color="#005a99",
        width=230,
        height=40
    )
    save_button.pack(side="left", padx=20, pady=20)

    close_button = ctk.CTkButton(
        button_frame,
        text="Close",
        command=lambda: close_form(form_window),
        fg_color="#808080",
        hover_color="#606060",
        width=230,
        height=40
    )
    close_button.pack(side="right", padx=20, pady=20)

    # Function to handle save shortcut
    def save_profile_shortcut(event):
        save_and_close(
            form_window,
            entries["business_name"],
            entries["address_line_1"],
            entries["address_line_2"],
            entries["upi_id"],
            entries["email"],
            entries["phone_no"],
            entries["website"],
            entries["facebook_instagram_id"],
            entries["pin_code"]
        )

    # Bind Ctrl+S to save the profile
    form_window.bind("<Control-s>", save_profile_shortcut)

# Play the default system sound
def play_default_sound():
    global sound_played
    if not sound_played:
        winsound.PlaySound("SystemBeep", winsound.SND_ALIAS)
        sound_played = True

# Save and close the profile form
def save_and_close(form_window, business_name_entry, address_line_1_entry, address_line_2_entry,
                   upi_id_entry, email_entry, phone_no_entry, website_entry, facebook_instagram_id_entry, pin_code_entry):
    business_name = business_name_entry.get().strip()
    address_line_1 = address_line_1_entry.get().strip()
    address_line_2 = address_line_2_entry.get().strip()
    pin_code = pin_code_entry.get().strip()
    phone_no = phone_no_entry.get().strip()
    email = email_entry.get().strip()

    # Check required fields in Company Info
    if not business_name:
        messagebox.showerror("Missing Information", "Please fill the required field: Business Name.", parent=form_window)
        switch_and_focus("Company Info", business_name_entry)
        return

    if not address_line_1:
        messagebox.showerror("Missing Information", "Please fill the required field: Address Line 1.", parent=form_window)
        switch_and_focus("Company Info", address_line_1_entry)
        return

    if not address_line_2:
        messagebox.showerror("Missing Information", "Please fill the required field: Address Line 2.", parent=form_window)
        switch_and_focus("Company Info", address_line_2_entry)
        return

    if not validate_pin_code(pin_code):
        messagebox.showerror("Invalid Pin Code", "Please enter a valid 6-digit pin code.", parent=form_window)
        switch_and_focus("Company Info", pin_code_entry)
        return

    # Check required fields in Contact Info
    if not email:
        messagebox.showerror("Missing Information", "Please fill the required field: Email.", parent=form_window)
        switch_and_focus("Contact Info", email_entry)
        return

    if not validate_email(email):
        messagebox.showerror("Invalid Email", "Please enter a valid email ending with @gmail.com.", parent=form_window)
        switch_and_focus("Contact Info", email_entry)
        return

    if not phone_no:
        messagebox.showerror("Missing Information", "Please fill the required field: Phone No.", parent=form_window)
        switch_and_focus("Contact Info", phone_no_entry)
        return

    if not validate_phone_number(phone_no):
        messagebox.showerror("Invalid Phone No", "Please enter a valid 10-digit phone number.", parent=form_window)
        switch_and_focus("Contact Info", phone_no_entry)
        return

    # Check if either website or facebook/instagram id is provided
    website = website_entry.get().strip()
    facebook_instagram_id = facebook_instagram_id_entry.get().strip()
    if not website and not facebook_instagram_id:
        messagebox.showerror("Missing Information", "Please provide either a Website or Facebook/Instagram ID.", parent=form_window)
        switch_and_focus("Contact Info", website_entry)
        return

    # Gather missing optional fields
    missing_fields = []
    if not form_window.logo_path:
        missing_fields.append("Logo")
    if not upi_id_entry.get().strip():
        missing_fields.append("UPI ID")

    # Create a formatted message for the confirmation dialog box
    confirm_message = "Do you want to save the changes to your profile?"
    if missing_fields:
        confirm_message += "\n\nOptional fields not filled:\n"
        confirm_message += "\n".join(f"- {field}" for field in missing_fields)

    result = messagebox.askyesno(
        "Confirm Save",
        confirm_message,
        parent=form_window
    )

    form_window.after(100, play_default_sound)

    if result:
        save_profile(
            business_name_entry,
            address_line_1_entry,
            address_line_2_entry,
            upi_id_entry,
            form_window.logo_path,
            email_entry,
            phone_no_entry,
            website_entry,
            facebook_instagram_id_entry,
            pin_code_entry
        )
        close_form(form_window)

# Close the profile form
def close_form(form_window):
    global profile_form_open, sound_played
    profile_form_open = False
    sound_played = False  # Reset sound flag
    form_window.destroy()

# Check if the profile is filled
def is_profile_filled():
    profile = load_profile()
    company_name = profile.get("business_name", "").strip()
    contact_number = profile.get("phone_no", "").strip()

    return bool(company_name and contact_number)

# Example usage:
# open_profile_form()