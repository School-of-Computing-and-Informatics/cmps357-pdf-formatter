import os
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

def segment_image_by_aspect_ratio(img, aspect_w=8.5, aspect_h=11, prefix="segment"):
    w, h = img.size
    aspect_ratio = aspect_w / aspect_h
    segment_height = int(w / aspect_ratio)
    if segment_height <= 0:
        print("Segment height is zero or negative. Check aspect ratio.")
        return []
    count = h // segment_height
    segments = []
    for i in range(count):
        top = i * segment_height
        bottom = top + segment_height
        segment = img.crop((0, top, w, bottom))
        filename = f"{prefix}_{i+1}.png"
        segment.save(filename)
        print(f"Saved segment {i+1} as {filename}")
        segments.append(filename)
    # Handle the last segment (remainder)
    last_start = count * segment_height
    if last_start < h:
        # Crop the remainder from the end of the last segment to the bottom
        remainder = img.crop((0, last_start, w, h))
        # Create a new image with the same width and segment_height, fill with white
        padded = Image.new("RGB", (w, segment_height), (255, 255, 255))
        # Paste the remainder at the top
        padded.paste(remainder, (0, 0))
        filename = f"{prefix}_{count+1}.png"
        padded.save(filename)
        print(f"Saved last segment (with white padding) as {filename}")
        segments.append(filename)
    return segments

if __name__ == "__main__":
    pdf_dir = "PDFS"
    for fname in os.listdir(pdf_dir):
        if fname.lower().endswith(".pdf"):
            pdf_path = os.path.join(pdf_dir, fname)
            base = os.path.splitext(fname)[0]
            cropped_png = f"{base}_cropped.png"
            cropped_img = crop_pdf_first_page(pdf_path, cropped_png)
            count_chunks_with_aspect_ratio(cropped_img)
            segment_image_by_aspect_ratio(cropped_img, 8.5, 11, prefix=f"{base}_segment")