import os
from pdf2image import convert_from_path
from PIL import Image
import numpy as np

def crop_pdf_first_page(pdf_path):
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
    return cropped_img

def segment_image_by_aspect_ratio(img, aspect_w=8.5, aspect_h=11):
    w, h = img.size
    aspect_ratio = aspect_w / aspect_h
    segment_height = int(w / aspect_ratio)
    if segment_height <= 0:
        return []
    count = h // segment_height
    segments = []
    for i in range(count):
        top = i * segment_height
        bottom = top + segment_height
        segment = img.crop((0, top, w, bottom))
        segments.append(segment)
    # Handle the last segment (remainder)
    last_start = count * segment_height
    if last_start < h:
        # Crop the remainder from the end of the last segment to the bottom
        remainder = img.crop((0, last_start, w, h))
        # Create a new image with the same width and segment_height, fill with white
        padded = Image.new("RGB", (w, segment_height), (255, 255, 255))
        # Paste the remainder at the top
        padded.paste(remainder, (0, 0))
        segments.append(padded)
    return segments

def create_pdf_from_images(images, output_pdf, margin_in=0.5, page_w_in=8.5, page_h_in=11, dpi=300):
    page_w_px = int(page_w_in * dpi)
    page_h_px = int(page_h_in * dpi)
    margin_px = int(margin_in * dpi)
    content_w = page_w_px - 2 * margin_px
    content_h = page_h_px - 2 * margin_px
    pdf_pages = []
    for img in images:
        img = img.convert("RGB")
        img_w, img_h = img.size
        scale = min(content_w / img_w, content_h / img_h)
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)
        resized = img.resize((new_w, new_h), Image.LANCZOS)
        page = Image.new("RGB", (page_w_px, page_h_px), (255, 255, 255))
        x = (page_w_px - new_w) // 2
        y = (page_h_px - new_h) // 2
        page.paste(resized, (x, y))
        pdf_pages.append(page)
    if pdf_pages:
        pdf_pages[0].save(output_pdf, save_all=True, append_images=pdf_pages[1:])
        print(f"Saved all pages to {output_pdf}")

if __name__ == "__main__":
    pdf_dir = "PDFS"
    all_segments = []
    for fname in os.listdir(pdf_dir):
        if fname.lower().endswith(".pdf"):
            pdf_path = os.path.join(pdf_dir, fname)
            base = os.path.splitext(fname)[0]
            cropped_img = crop_pdf_first_page(pdf_path)
            segments = segment_image_by_aspect_ratio(cropped_img, 8.5, 11)
            all_segments.extend(segments)
    create_pdf_from_images(all_segments, "output.pdf")