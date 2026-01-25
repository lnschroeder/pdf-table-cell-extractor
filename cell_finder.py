import pymupdf
import cv2
import numpy as np

from itertools import combinations


def __pdf_page_to_image(page, dpi):
    mat = pymupdf.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img = np.frombuffer(pix.samples, dtype=np.uint8)
    img = img.reshape(pix.h, pix.w, pix.n)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return img


def __image_to_pdf_coords(x_img, y_img, dpi):
    scale = dpi / 72
    x_pdf = x_img / scale
    y_pdf = y_img / scale
    return x_pdf, y_pdf


def __extend_line_to_image(line, width, height):
    x1, y1, x2, y2 = line
    if x1 == x2:
        return x1, 0, x2, height
    m = (y2 - y1) / (x2 - x1)
    y0 = int(y1 - m * x1)
    yW = int(y1 + m * (width - x1))
    return 0, y0, width, yW


def __line_intersection(line1, line2, width, height):
    x1, y1, x2, y2 = map(float, line1)
    x3, y3, x4, y4 = map(float, line2)

    A1 = y2 - y1
    B1 = x1 - x2
    C1 = A1 * x1 + B1 * y1

    A2 = y4 - y3
    B2 = x3 - x4
    C2 = A2 * x3 + B2 * y3

    det = A1 * B2 - A2 * B1
    if abs(det) < 1e-10:  # Avoid division by zero
        return None

    x = (B2 * C1 - B1 * C2) / det
    y = (A1 * C2 - A2 * C1) / det

    if 0 <= x <= width and 0 <= y <= height:
        return int(round(x)), int(round(y))
    return None


def __remove_duplicates(points, min_distance):
    unique_points = []
    for pt in points:
        if all(np.hypot(pt[0] - up[0], pt[1] - up[1]) >= min_distance for up in unique_points):
            unique_points.append(pt)
    return unique_points


def get_rectangles(doc, page_number):
    page = doc[page_number]
    dpi = 300
    img = __pdf_page_to_image(page, dpi)
    height, width = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 100, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=500, maxLineGap=5)
    lines = [line[0] for line in lines]
    extended_lines = [__extend_line_to_image(l, width, height) for l in lines]
    intersections = []
    for l1, l2 in combinations(extended_lines, 2):
        pt = __line_intersection(l1, l2, width, height)
        if pt:
            intersections.append(pt)
    intersections = __remove_duplicates(intersections, 5)
    xs = sorted({x for x, _ in intersections})
    ys = sorted({y for _, y in intersections})

    # TODO here we are filtering intersection points as follows:
    #  row/col will be merged with the previous row/col, when they are smaller than 200 in height/width
    xs = [x for i, x in enumerate(xs) if i == len(xs) - 1 or xs[i + 1] - xs[i] > 200]
    ys = [y for i, y in enumerate(ys) if i == len(ys) - 1 or ys[i + 1] - ys[i] > 200]

    rectangles = []
    for row, y in enumerate(ys[:-1]):
        for col, x in enumerate(xs[:-1]):
            p1 = __image_to_pdf_coords(xs[col] + 1, ys[row] + 1, dpi)
            p2 = __image_to_pdf_coords(xs[col + 1], ys[row + 1], dpi)
            rectangles.append((row, col, [*p1, *p2]))
    return rectangles
