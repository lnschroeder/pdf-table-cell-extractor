import os
import re
import pymupdf

import cell_finder


def __normalize_whitespace(text):
    return re.sub(r"\s+", " ", text).strip()


def __is_mostly_on_page(rect, page_cropbox):
    area = rect.get_area()
    intersection_area = rect.intersect(page_cropbox).get_area()
    return (intersection_area / area) > 0.3


def __extract_text(page, output_path):
    text = __normalize_whitespace(page.get_text())
    with open(output_path, "w") as f:
        f.write(text)


def __extract_image(doc, image, output_dir, i):
    xref = image[0]
    smask = image[1]
    pix = pymupdf.Pixmap(doc, xref)
    if smask > 0:
        mask = pymupdf.Pixmap(doc, smask)
        pix = pymupdf.Pixmap(pix, mask)
    pix.save(os.path.join(output_dir, f"{i:04d}.png"))


def __extract_images(doc, page, output_dir):
    i = 0
    for image in page.get_images():
        if not __is_mostly_on_page(page.get_image_rects(image[0])[0], page.cropbox):
            continue
        __extract_image(doc, image, output_dir, i)
        i += 1


def __extract_content(cropped_pdf_path, output_dir):
    doc = pymupdf.open(cropped_pdf_path)
    page = doc[0]

    __extract_text(page, os.path.join(output_dir, "text.txt"))
    __extract_images(doc, page, output_dir)

    doc.close()


def __extract_cropped_pdf(output_path, rectangle, doc, page_number):
    crop_rect = pymupdf.Rect(*rectangle)
    new_pdf = pymupdf.open()
    new_page = new_pdf.new_page(width=crop_rect.width, height=crop_rect.height)

    new_page.show_pdf_page(new_page.rect, doc, page_number, clip=crop_rect)
    new_pdf.save(output_path)

    new_pdf.close()


# TODO extracting a header is not mandatory
def __extract_header(page):
    return ""


def __extract_cells(doc, page, collection_dir):
    for row, col, rectangle in cell_finder.get_rectangles(doc, page.number):
        output_dir = os.path.join(collection_dir, f"{row + 1:02d}-{col + 1:02d}")
        cropped_pdf_path = os.path.join(output_dir, "crop.pdf")

        os.makedirs(output_dir, exist_ok=True)

        __extract_cropped_pdf(cropped_pdf_path, rectangle, doc, page.number)
        __extract_content(cropped_pdf_path, output_dir)


def extract_page_collection(doc, start_page_idx, end_page_idx, name):
    for page_number in range(start_page_idx, end_page_idx + 1):
        page = doc[page_number]
        header = __extract_header(page)
        collection_dir = f"out/{name}/{page.number + 1:04d}"

        os.makedirs(collection_dir, exist_ok=True)

        with open(os.path.join(collection_dir, "metadata.txt"), "w") as f:
            f.write(header)

        __extract_cells(doc, page, collection_dir)
