import sqlite3
import re

# Step 1: Connect to the database
conn = sqlite3.connect("data.db")

# Step 2: Create a table with more fields
conn.execute("""
CREATE TABLE IF NOT EXISTS receipts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor TEXT,
    date TEXT,
    amount REAL,
    full_text TEXT
)
""")

# Step 3: Open the text file created from OCR
with open("extracted_text.txt", "r", encoding="utf-8") as file:
    full_text = file.read()

# Step 4: Extract vendor, date, and amount (basic logic)
vendor = full_text.split('\n')[0]  # First line usually has vendor
date_match = re.search(r'\d{2}/\d{2}/\d{4}', full_text)
amount_match = re.search(r'[\₹\$]\s*\d+(?:\.\d{2})?', full_text)

date = date_match.group(0) if date_match else "N/A"
amount = float(amount_match.group(0).replace("₹", "").replace("$", "").strip()) if amount_match else 0.0

# Step 5: Insert all data
conn.execute("""
INSERT INTO receipts (vendor, date, amount, full_text)
VALUES (?, ?, ?, ?)
""", (vendor, date, amount, full_text))
conn.commit()
conn.close()

print("✅ Saved all structured data into the database.")