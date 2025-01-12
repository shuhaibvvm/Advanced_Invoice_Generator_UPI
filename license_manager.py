import sqlite3
import uuid
import os
import csv

DATABASE_FILE = 'license_keys.db'
ENCRYPTION_KEY = 'your-super-secret-encryption-key'  # Example encryption key

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.execute(f"PRAGMA key = '{ENCRYPTION_KEY}';")
    return conn

def create_license_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS licenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_key TEXT NOT NULL,
            is_used INTEGER DEFAULT 0,
            hardware_id TEXT
        )
    ''')
    conn.commit()
    conn.close()

def load_license_keys_from_csv(filename):
    create_license_table()
    conn = get_db_connection()
    cursor = conn.cursor()
    with open(filename, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute('INSERT INTO licenses (license_key) VALUES (?)', (row['license_key'],))
    conn.commit()
    conn.close()

def get_hardware_id():
    return str(uuid.getnode())

def validate_license_key(license_key):
    create_license_table()
    conn = get_db_connection()
    cursor = conn.cursor()
    hardware_id = get_hardware_id()
    cursor.execute('SELECT * FROM licenses WHERE license_key = ? AND (is_used = 0 OR hardware_id = ?)', (license_key, hardware_id))
    row = cursor.fetchone()
    if row:
        cursor.execute('UPDATE licenses SET is_used = 1, hardware_id = ? WHERE license_key = ?', (hardware_id, license_key))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def is_license_valid():
    if not os.path.exists('license_key.txt'):
        return False
    try:
        with open('license_key.txt', 'r') as file:
            stored_license = file.read().strip()
            return validate_license_key(stored_license)
    except Exception as e:
        print(f"Error validating license: {e}")
        return False

def store_license_key(license_key):
    with open('license_key.txt', 'w') as file:
        file.write(license_key)