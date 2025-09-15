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
    return cropped_img

def count_chunks_with_aspect_ratio(img, aspect_w=8.5, aspect_h=11):
    w, h = img.size
    aspect_ratio = aspect_w / aspect_h
    chunk_height = h
    chunk_width = int(chunk_height * aspect_ratio)
    if chunk_width <= 0:
        print("Chunk width is zero or negative. Check aspect ratio.")
        return 0
    if w < chunk_width:
        print("Image is smaller than one chunk.")
        return 1 if w > 0 and h > 0 else 0
    count = w // chunk_width
    print(f"Number of non-overlapping chunks with aspect ratio {aspect_w}:{aspect_h}: {count}")
    return count

if __name__ == "__main__":
    cropped_img = crop_pdf_first_page("Jan 21.pdf", "cropped_page1.png")
    count_chunks_with_aspect_ratio(cropped_img)