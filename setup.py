from cx_Freeze import setup, Executable

# Specify the files to include in the build
build_exe_options = {
    "include_files": [
        "my_icon.ico",     # Path to your icon file
        "invoices.db"      # Path to your database file
    ]
}

# Setup configuration
setup(
    name="InvoiceGenerator",
    version="1.0",
    description="GST Invoice Generator",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "main.py",       # Replace with the name of your main Python script
            base="Win32GUI", # Use "Win32GUI" for GUI applications
            icon="my_icon.ico"  # Path to the icon file
        )
    ]
)
