import pymupdf

from pdf_page_extractor import extract_page_collection

if __name__ == "__main__":
    # TODO specify the input PDF
    document = pymupdf.open("assets/CoP-MAG-2025-2028-1.1-de.pdf")
    # TODO specify where the table are in the PDF (1-based index)
    page_collections = {
        "1-fx": (1, 11),
        "2-ph": (12, 23),
        "3-sr": (24, 40),
        "4-vt": (42, 48),
        "5-pb": (49, 65),
        "6-hb": (66, 82),
    }
    for collection_name, (start_page, end_page) in page_collections.items():
        print(f"Extracting: {collection_name}")
        extract_page_collection(document, start_page - 1, end_page - 1, collection_name)
    document.close()
