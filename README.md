# Receipt Analyzer App

This app lets you upload a receipt image or PDF and extract:
- Invoice date
- Vendor name
- Total amount

It shows the data in a table and a dashboard.

## Tools Used
- Python
- Tesseract OCR (to read text from images)
- Streamlit (to make the web app)
- SQLite (to store the data)
- pdf2image and PIL (to handle images)

## How to Run

1. Install Python and Tesseract.
2. Install required packages:
   pip install streamlit pytesseract pdf2image pillow
3. Run the app:
   streamlit run app.py
4. Upload a receipt and view the results.

## How It Works

- It uses OCR to read the receipt image.
- It finds the date, vendor, and amount from the text.
- It saves the data in a database.
- It shows everything in a web app.

## Made by: Silja CR
