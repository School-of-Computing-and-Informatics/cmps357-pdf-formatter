from pdf2image import convert_from_path
from PIL import Image
import numpy as np

def crop_pdf_first_page(pdf_path, output_png):
    images = convert_from_path(pdf_path)
    if not images:
        raise ValueError("No images found in PDF.")
    # Improved cropping: convert to grayscale, threshold, find bounding box
    first_img = images[0].convert("L")  # Convert to grayscale
    img_np = np.array(first_img)
    # Threshold: consider pixels >240 as white
    mask = img_np < 240
    coords = np.argwhere(mask)
    if coords.size > 0:
        y0, x0 = coords.min(axis=0)
        y1, x1 = coords.max(axis=0) + 1  # slices are exclusive at the top
        cropped_img = images[0].crop((x0, y0, x1, y1))
    else:
        cropped_img = images[0]
    cropped_img.save(output_png)
    print(f"Cropped first page saved as {output_png}")

if __name__ == "__main__":
    crop_pdf_first_page("Jan 21.pdf", "cropped_page1.png")