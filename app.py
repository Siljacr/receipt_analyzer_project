import streamlit as st
from PIL import Image
import pytesseract
import sqlite3
import re
import os
import pandas as pd

# Database Setup
conn = sqlite3.connect('data.db', check_same_thread=False)
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS past_receipts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_date TEXT,
        vendor TEXT,
        amount TEXT
    )
''')
conn.commit()

# Helper functions
def extract_data_from_text(text):
    # Extract date in various formats like 8/3/2023, 2023-03-08, etc.
    date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{1,2}-\d{1,2})', text)
    invoice_date = date_match.group(1) if date_match else "Not found"

    # Extract vendor: take first line or line with store-related keywords
    vendor = "Not found"
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    for line in lines:
        if any(keyword in line.lower() for keyword in ["store", "shop", "mart", "supermarket", "bazaar", "restaurant"]):
            vendor = line
            break
    if vendor == "Not found" and lines:
        vendor = lines[0]  # fallback to first non-empty line

    # Improved amount extraction: check all total/amount lines and choose the last valid number
    amount_candidates = []
    for line in lines:
        if re.search(r'(total|amount|subtotal|grand total)', line, re.IGNORECASE):
            amt_match = re.search(r'([₹$€£]?\s*\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)', line)
            if amt_match:
                amount_candidates.append(amt_match.group(1).strip())
    amount = amount_candidates[-1] if amount_candidates else "Not found"

    return invoice_date, vendor, amount

def detect_currency(text):
    if "$" in text:
        return "USD"
    elif "₹" in text:
        return "INR"
    elif "€" in text:
        return "EUR"
    elif "£" in text:
        return "GBP"
    else:
        return "Unknown"

# Streamlit App
st.set_page_config(page_title="Receipt Analyzer", layout="wide")
st.title("🧾 Receipt and Bill Analyzer")

menu = ["Upload a Receipt", "View Structured Data", "Analytics Dashboard"]
choice = st.sidebar.selectbox("Choose an option", menu)

if choice == "Upload a Receipt":
    st.subheader("Upload and Process a Receipt")
    uploaded_file = st.file_uploader("Upload Receipt Image", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Receipt", use_container_width=True)

        # OCR
        text = pytesseract.image_to_string(image)
        st.text_area("🔍 Extracted Text (OCR)", text, height=200)

        # Extract structured fields
        invoice_date, vendor, amount = extract_data_from_text(text)
        currency = detect_currency(text)

        st.write("📅 Invoice Date:", invoice_date)
        st.write("🏬 Vendor:", vendor)
        st.write("💰 Amount:", amount)
        st.write("💱 Currency:", currency)

        if st.button("Save to Database"):
            c.execute("INSERT INTO past_receipts (invoice_date, vendor, amount) VALUES (?, ?, ?)",
                      (invoice_date, vendor, amount))
            conn.commit()
            st.success("✅ Receipt saved to database!")

elif choice == "View Structured Data":
    st.subheader("📄 Structured Receipt Information")
    c.execute("SELECT * FROM past_receipts ORDER BY id DESC")
    rows = c.fetchall()

    if rows:
        df = pd.DataFrame(rows, columns=["ID", "Invoice Date", "Vendor", "Amount"])
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("⚠ No receipts found.")

elif choice == "Analytics Dashboard":
    st.subheader("📊 Analytics")
    c.execute("SELECT * FROM past_receipts")
    rows = c.fetchall()

    if rows:
        df = pd.DataFrame(rows, columns=["ID", "Invoice Date", "Vendor", "Amount"])
        df["Amount"] = df["Amount"].replace(r"[^\d.]", "", regex=True)
        df = df[df["Amount"].str.match(r'^\d+(\.\d+)?$')]  # Keep only valid amounts
        df["Amount"] = df["Amount"].astype(float)

        if not df.empty:
            total = df["Amount"].sum()
            avg = df["Amount"].mean()
            st.metric("💸 Total Spent", f"{total:.2f}")
            st.metric("📊 Average per Receipt", f"{avg:.2f}")
            st.bar_chart(df.set_index("Vendor")["Amount"])
        else:
            st.warning("⚠ No valid amount data found for analytics.")
    else:
        st.warning("⚠ No receipts in database.")