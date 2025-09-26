import os
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
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

def analyze_bottom_rows(img, segment_num, threshold=240, dpi=300):
    """
    Analyze the bottom rows of the image to find the best place to segment (the true bottom of content).
    Draw a black line at that row and return both the row index and inches from the top.
    """
    gray = img.convert("L")
    arr = np.array(gray)
    h, w = arr.shape
    # Calculate number of rows for half an inch
    num_rows = int(0.5 * dpi)
    min_nonwhite = w  # max possible non-white per row
    min_row = h - 1
    for i in range(h-1, max(h-1-num_rows, -1), -1):
        nonwhite = np.sum(arr[i] < threshold)
        if nonwhite < min_nonwhite:
            min_nonwhite = nonwhite
            min_row = i
    # Draw a black line at the detected bottom row
    rgb_img = img.convert("RGB")
    pixels = rgb_img.load()
    for x in range(rgb_img.width):
        pixels[x, min_row] = (0, 0, 0)
    img.paste(rgb_img)
    min_row_inches = min_row / dpi
    return min_row, min_row_inches

def segment_image_by_aspect_ratio(img, aspect_w=8.5, aspect_h=11):
    w, h = img.size
    aspect_ratio = aspect_w / aspect_h
    segment_height = int(w / aspect_ratio)
    if segment_height <= 0:
        return []
    segments = []
    start_row = 0
    seg_num = 1
    while start_row < h:
        # Tentative bottom row for this segment
        tentative_bottom = min(start_row + segment_height, h)
        segment = img.crop((0, start_row, w, tentative_bottom))
        # Analyze the bottom rows of this segment to find the true bottom
        min_row, min_row_inches = analyze_bottom_rows(segment, seg_num, dpi=300)
        print(f"Segment {seg_num}: min row at {min_row_inches:.2f} inches from top (relative to segment)")
        # The true bottom in the original image is:
        true_bottom = start_row + min_row + 1  # +1 to include the black line
        # Crop the segment from start_row to true_bottom
        segment_final = img.crop((0, start_row, w, true_bottom))
        segments.append(segment_final)
        # Prepare for next segment
        start_row = true_bottom
        seg_num += 1
        # If the next segment would be too small, break
        if h - start_row < int(0.2 * segment_height):
            break
    # Handle the last segment (if any rows remain)
    if start_row < h:
        remainder = img.crop((0, start_row, w, h))
        # Always pad to segment_height for consistency
        padded = Image.new("RGB", (w, segment_height), (255, 255, 255))
        padded.paste(remainder, (0, 0))
        # Only analyze up to the actual content height (not the padded area)
        actual_content_height = min(remainder.height, segment_height)
        # Draw black line at the bottom of actual content in the remainder
        # Temporarily crop to actual content for analysis
        content_crop = padded.crop((0, 0, w, actual_content_height))
        min_row, min_row_inches = analyze_bottom_rows(content_crop, seg_num, dpi=300)
        print(f"Segment {seg_num}: min row at {min_row_inches:.2f} inches from top (last segment)")
        # Draw the black line on the padded image at min_row (if within content)
        rgb_img = padded.convert("RGB")
        pixels = rgb_img.load()
        if min_row < actual_content_height:
            for x in range(rgb_img.width):
                pixels[x, min_row] = (0, 0, 0)
            padded.paste(rgb_img)
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

def perform_ocr_on_segments(segments, filename):
    """Perform OCR on image segments and print results to console"""
    import pytesseract
    print(f"\n--- OCR for: {filename} ---", flush=True)
    try:
        for i, segment in enumerate(segments):
            # Preprocess: binarize for multicolored, full-intensity handwriting on whitish background
            arr = np.array(segment.convert('RGB'))
            # Consider a pixel background if all channels are near 255 (very light)
            bg_mask = (arr[...,0] > 235) & (arr[...,1] > 235) & (arr[...,2] > 235)
            # Foreground: at least one channel is strongly colored (e.g., >180)
            fg_mask = ((arr[...,0] > 180) | (arr[...,1] > 180) | (arr[...,2] > 180)) & (~bg_mask)
            # Build a binary image: foreground=black, background=white
            binarized = np.ones(arr.shape[:2], dtype='uint8') * 255
            binarized[fg_mask] = 0
            bin_img = Image.fromarray(binarized)
            # OCR configuration parameters:
            # --oem 1: Use LSTM OCR Engine Mode (more accurate for modern text)
            # --psm 6: Assume uniform block of text (good for documents with paragraphs)
            config = '--oem 1 --psm 6'
            text = pytesseract.image_to_string(bin_img, lang='eng', config=config)
            print(f"[Segment {i+1}]:\n{text.strip()}\n", flush=True)
    except Exception as e:
        print(f"Error performing OCR on {filename}: {e}", flush=True)

def process_pdfs_directory(pdf_dir="PDFS"):
    """Process all PDFs in a directory (for CLI usage)"""
    import glob
    import sys
    
    print("[merge.py] Script started", flush=True)
    # Find all PDFs in PDFS/ directory
    pdf_files = [f for f in glob.glob(os.path.join(pdf_dir, '*.pdf'))]
    print(f"Found {len(pdf_files)} PDF(s) in {pdf_dir}", flush=True)
    if not pdf_files:
        print("No PDF files found. Exiting.", flush=True)
        sys.exit(0)
    
    # OCR processing
    for pdf_path in pdf_files:
        try:
            cropped_img = crop_pdf_first_page(pdf_path)
            segments = segment_image_by_aspect_ratio(cropped_img, 8.5, 11)
            perform_ocr_on_segments(segments, os.path.basename(pdf_path))
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}", flush=True)
    
    # PDF processing
    all_segments = []
    for fname in os.listdir(pdf_dir):
        if fname.lower().endswith(".pdf"):
            pdf_path = os.path.join(pdf_dir, fname)
            cropped_img = crop_pdf_first_page(pdf_path)
            segments = segment_image_by_aspect_ratio(cropped_img, 8.5, 11)
            all_segments.extend(segments)
    create_pdf_from_images(all_segments, "output.pdf")

if __name__ == "__main__":
    process_pdfs_directory()