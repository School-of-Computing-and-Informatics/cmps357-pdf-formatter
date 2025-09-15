import PyPDF2

pdf_path = "Jan 21.pdf"
with open(pdf_path, "rb") as file:
    reader = PyPDF2.PdfReader(file)
    # Example: print number of pages
    print("pages:" , len(reader.pages))