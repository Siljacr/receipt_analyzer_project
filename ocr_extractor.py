from PIL import Image
import pytesseract
import re

# Step 1: Load the image
image = Image.open("Page_1.png")  # Make sure the image file is in the same folder

# Step 2: Extract text from the image
extracted_text = pytesseract.image_to_string(image)
print("Extracted Text:\n", extracted_text)

# Step 3: Extract Invoice Date (supports formats like 12/03/2024, 2024-03-12, etc.)
date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{1,2}-\d{1,2})', extracted_text)
invoice_date = date_match.group() if date_match else "Not found"

# Step 4: Extract Total Amount – pick the last matching amount line with keywords
amount = "Not found"
amount_candidates = []

for line in extracted_text.splitlines():
    if re.search(r'(total|amount|subtotal|grand total)', line, re.IGNORECASE):
        amt_match = re.search(r'([₹$€£]?\s*\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)', line)
        if amt_match:
            amount_candidates.append(amt_match.group(1).strip())

if amount_candidates:
    amount = amount_candidates[-1]  # Use the last matched amount

# Step 5: Extract Vendor / Company Name
lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
vendor = "Not found"
for line in lines:
    if any(keyword in line.lower() for keyword in ["store", "shop", "mart", "supermarket", "bazaar", "restaurant"]):
        vendor = line
        break
if vendor == "Not found" and lines:
    vendor = lines[0]  # fallback to first line of receipt

# Step 6: Display Structured Information
print("\nStructured Information:")
print("Invoice Date:", invoice_date)
print("Vendor Name:", vendor)
print("Total Amount:", amount)

# Step 7: Save extracted OCR text
with open("extracted_text.txt", "w", encoding="utf-8") as f:
    f.write(extracted_text)