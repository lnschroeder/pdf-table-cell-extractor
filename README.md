# pdf-table-cell-extractor

This is a specialized tool designed to deconstruct PDF tables into individual cell components. Using Computer Vision, it
identifies cell boundaries and generates cropped PDF files for every single cell, allowing for further extraction of text and images.

# How it Works

- Line Detection: Computer vision algorithms identify horizontal and vertical lines and determines intersections.
- Cropping: The script "slices" the PDF into individual files based on the detected grid.
- Parsing: Text and images are extracted from each resulting cell-crop.

# Usage & Configuration

You might need to adjust the code a bit to suit your document. Please see the `TODO` comments in the code for more information.

To run the application run
```sh
python3 main.py
```

## Example: Gymnastics Code of Points

The provided code is fine-tuned to extract elements from the 2025 Men's Artistic Gymnastics Code of Points.

You have to adjust just two things for this to work:

1. Define page collections

In `main.py`, map your sections to specific page ranges:

```python
if __name__ == "__main__":
    ...
    page_collections = {
        "1-fx": (28, 38),
        "2-ph": (47, 58),
        "3-sr": (63, 79),
        "4-vt": (85, 91),
        "5-pb": (96, 112),
        "6-hb": (118, 134),
    }
    ...
```

2. Custom header logic

Adjust `pdf_page_extractor.py` for extracting headers from a page:

```python
def __extract_header(page):
    for line in page.get_text().splitlines():
        line = __normalize_whitespace(line)
        if line.startswith("EG "):
            return line
    return ""
```

