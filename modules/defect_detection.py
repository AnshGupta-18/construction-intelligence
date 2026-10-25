
import cv2
import numpy as np


def detect_possible_cracks(image):
    """
    Performs basic image processing to highlight possible
    crack-like regions. This is not a trained defect detector.
    """

    # Convert the uploaded image to a NumPy array
    image_array = np.array(image.convert("RGB"))

    # Convert RGB to grayscale for processing
    gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)

    # Reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Detect edges
    edges = cv2.Canny(blurred, 50, 150)

    # Highlight detected edges in red
    highlighted = image_array.copy()
    highlighted[edges > 0] = [255, 0, 0]

    # Calculate basic image measurements
    total_pixels = edges.size
    edge_pixels = int(np.count_nonzero(edges))
    edge_percentage = round(
        (edge_pixels / total_pixels) * 100, 2
    )

    return {
        "highlighted_image": highlighted,
        "edge_count": edge_pixels,
        "edge_percentage": edge_percentage,
    }
