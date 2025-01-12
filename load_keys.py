# load_keys.py
from license_manager import load_license_keys_from_csv

if __name__ == "__main__":
    load_license_keys_from_csv('license_keys.csv')
    print("License keys loaded into the database from 'license_keys.csv'.")