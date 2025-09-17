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
    # Always use the full width, segment vertically by aspect ratio
    aspect_ratio = aspect_w / aspect_h
    # For a segment with full width, what is the height?
    segment_height = int(w / aspect_ratio)
    if segment_height <= 0:
        print("Segment height is zero or negative. Check aspect ratio.")
        return 0
    if h < segment_height:
        print("Image is smaller than one segment.")
        percent_remaining = (h / segment_height) * 100 if segment_height > 0 else 0
        print(f"Percentage of image remaining after last segment: {percent_remaining:.2f}%")
        return 1 if w > 0 and h > 0 else 0
    count = h // segment_height
    remaining_height = h - (count * segment_height)
    percent_remaining = (remaining_height / h) * 100 if h > 0 else 0
    print(f"Number of non-overlapping vertical segments with aspect ratio {aspect_w}:{aspect_h}: {count}")
    print(f"Percentage of image remaining after last segment: {percent_remaining:.2f}%")
    return count

if __name__ == "__main__":
    cropped_img = crop_pdf_first_page("Jan 21.pdf", "cropped_page1.png")
    count_chunks_with_aspect_ratio(cropped_img)