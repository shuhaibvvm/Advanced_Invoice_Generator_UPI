import os
import json
import firebase_admin
from firebase_admin import credentials, db
from uuid import uuid4

# Firebase initialization
def initialize_firebase():
    if not firebase_admin._apps:
        try:
            json_path = os.path.join(os.path.dirname(__file__), "ernadixlicensemanager-firebase-adminsdk-hno7l-d2324efdf4.json")
            with open(json_path) as json_file:
                cred = credentials.Certificate(json.load(json_file))
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://ernadixlicensemanager-default-rtdb.firebaseio.com/'
            })
        except FileNotFoundError:
            print("Firebase credentials file not found.")
        except json.JSONDecodeError:
            print("Error decoding JSON from the credentials file.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

# Store license key and user information in Firebase
def store_license_key(license_key, user_info):
    ref = db.reference("licenses")
    ref.child(license_key).set({
        "valid": True,
        "user_info": user_info
    })

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
        try:
            with open("license.json", "r") as file:
                data = json.load(file)
                return data.get("valid", False)
        except json.JSONDecodeError:
            print("Error decoding JSON from the license.json file.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
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

# Retrieve user information based on license key
def get_user_info(license_key):
    ref = db.reference(f"licenses/{license_key}/user_info")
    user_info = ref.get()
    return user_info

# Example function to generate and save 1000 keys
def generate_and_save_keys():
    initialize_firebase()
    keys = generate_keys(1000)
    save_keys_to_file(keys)
    print("1000 license keys generated and saved to license_keys.txt.")

# Check if license key is valid (used for initial startup check)
def is_license_valid():
    if os.path.exists("license.json"):
        try:
            with open("license.json", "r") as file:
                content = file.read()
                print("Contents of license.json:", content)
                data = json.loads(content)
                license_key = data.get("license_key")
                if license_key and validate_license_key(license_key):
                    return True
        except json.JSONDecodeError:
            print("Error decoding JSON from the license.json file.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    return False

# Example usage
if __name__ == "__main__":
    initialize_firebase()
    license_key = "your_license_key_here"
    user_info = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "123-456-7890"
    }
    if validate_license_key(license_key):
        store_license_key(license_key, user_info)
        print("License is valid and user information stored.")
    else:
        print("License is not valid or has already been used.")