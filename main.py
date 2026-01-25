import pymupdf

from pdf_page_extractor import extract_page_collection

if __name__ == "__main__":
    # TODO specify the input PDF
    document = pymupdf.open("input.pdf")
    # TODO specify where the table are in the PDF (1-based index)
    page_collections = {
        # "table-1": (2, 10),
        # "table-2": (20, 24),
        # ...
    }
    for collection_name, (start_page, end_page) in page_collections.items():
        print(f"Extracting: {collection_name}")
        extract_page_collection(document, start_page - 1, end_page - 1, collection_name)
    document.close()
