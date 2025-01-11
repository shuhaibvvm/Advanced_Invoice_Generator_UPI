import customtkinter as ctk

def start_app():
    splash.destroy()  # Close the splash screen
    app.deiconify()  # Show the main app after loading is complete

# Create the splash screen
splash = ctk.CTk()
splash.geometry("400x200")
splash_label = ctk.CTkLabel(splash, text="Loading...", font=("Helvetica", 18))
splash_label.pack(expand=True)

# Hide the main app until the splash screen is closed
app.withdraw()

# Load resources in a separate thread after showing the splash screen
def load_resources():
    import time
    time.sleep(3)  # Simulating resource loading delay
    start_app()  # Start the main app after loading is done

# Start the resource loading in a separate thread
import threading
threading.Thread(target=load_resources).start()

splash.mainloop()