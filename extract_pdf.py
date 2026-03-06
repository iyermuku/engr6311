import PyPDF2
import sys

pdf_path = r'c:\Users\mukun\Documents\engr6311\engr6311\ENGR6311_W26_HW3.pdf'

try:
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        print(f"Number of pages: {len(reader.pages)}\n")
        print("="*80)
        
        for page_num, page in enumerate(reader.pages, 1):
            print(f"\n--- PAGE {page_num} ---\n")
            text = page.extract_text()
            print(text)
            print("\n" + "="*80)
            
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
