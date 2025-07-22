from pdf2image import convert_from_path

# If Poppler is in PATH, you can omit poppler_path:
images = convert_from_path('your_receipt.pdf')

for i, image in enumerate(images):
    image.save(f'page_{i + 1}.png', 'PNG')