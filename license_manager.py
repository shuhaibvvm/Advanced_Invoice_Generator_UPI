import os
import json
import firebase_admin
from firebase_admin import credentials, db
from uuid import uuid4

# Firebase initialization
def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate("ernadixlicensemanager-firebase-adminsdk-hno7l-d2324efdf4.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://ernadixlicensemanager-default-rtdb.firebaseio.com/'
        })

# Store license key in Firebase
def store_license_key(license_key):
    ref = db.reference("licenses")
    ref.child(license_key).set({"valid": True})

# Validate a license key online
def validate_license_key_online(license_key):
    ref = db.reference(f"licenses/{license_key}")
    license_data = ref.get()
    if license_data and license_data.get("valid", False):
        ref.update({"valid": False})  # Mark as used
        return True
    return False

# Check if license key is valid locally
def is_license_valid_locally():
    if os.path.exists("license.json"):
        with open("license.json", "r") as file:
            data = json.load(file)
            return data.get("valid", False)
    return False

# Save license key locally
def save_license_key_locally(license_key, valid):
    with open("license.json", "w") as file:
        json.dump({"license_key": license_key, "valid": valid}, file)

# Validate the license key (first time online, then offline)
def validate_license_key(license_key):
    if is_license_valid_locally():
        return True
    else:
        initialize_firebase()
        if validate_license_key_online(license_key):
            save_license_key_locally(license_key, True)
            return True
    return False

# Generate a batch of license keys and store them in Firebase
def generate_keys(batch_size=1000):
    keys = [str(uuid4()) for _ in range(batch_size)]
    ref = db.reference("licenses")
    for key in keys:
        ref.child(key).set({"valid": True})
    return keys

# Save generated keys to a file
def save_keys_to_file(keys, file_name="license_keys.txt"):
    with open(file_name, "w") as file:
        file.writelines(f"{key}\n" for key in keys)

# Example function to generate and save 1000 keys
def generate_and_save_keys():
    initialize_firebase()
    keys = generate_keys(1000)
    save_keys_to_file(keys)
    print("1000 license keys generated and saved to license_keys.txt.")

# Check if license key is valid (used for initial startup check)
def is_license_valid():
    if os.path.exists("license.json"):
        with open("license.json", "r") as file:
            data = json.load(file)
            license_key = data.get("license_key")
            if license_key and validate_license_key(license_key):
                return True
    return False

# Example usage
if __name__ == "__main__":
    license_key = "your_license_key_here"
    if validate_license_key(license_key):
        print("License is valid.")
    else:
        print("License is not valid or has already been used.")