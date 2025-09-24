# CMPS 357 PDF Formatter - Web Frontend

A Python Flask web application for processing and reformatting PDF documents by segmenting them into standardized pages with proper aspect ratios.

## Overview

This web application provides an intuitive interface for uploading PDF files and automatically processing them into properly formatted pages with a standard 8.5:11 aspect ratio (US Letter format). The tool crops, segments, and reformats PDF content to create clean, uniform output suitable for printing or digital distribution.

## Features

- **Web-Based Interface**: Easy-to-use drag-and-drop file upload with dark/light theme support
- **Multiple File Support**: Process multiple PDF files simultaneously 
- **File Management**: Reorder files before processing with drag-and-drop interface
- **Real-Time Processing**: Upload files and receive processed PDF immediately
- **PDF to Image Conversion**: Converts PDF pages to images for processing
- **Intelligent Cropping**: Automatically detects and crops content boundaries
- **Vertical Segmentation**: Splits tall images into multiple segments with consistent aspect ratios
- **Padding and Alignment**: Ensures all segments maintain proper dimensions
- **Batch Processing**: Processes multiple PDF files in a single operation
- **Download Output**: Generates and downloads a single merged PDF with all processed segments
- **OCR/Handwriting Recognition**: Extracts text (including handwriting, if possible) from PDF images using Tesseract OCR

## Dependencies


The project requires the following Python packages:

- `pdf2image` (1.17.0) - For converting PDF files to images
- `Pillow` (10.3.0) - For image processing and manipulation
- `numpy` (1.26.4) - For numerical operations on image arrays
- `Flask` (3.0.0) - Web framework for the user interface
- `pytesseract` (0.3.10) - Python wrapper for Tesseract OCR (for text/handwriting recognition)

All dependencies are listed in `requirements.txt`.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/School-of-Computing-and-Informatics/cmps357-pdf-formatter.git
   cd cmps357-pdf-formatter
   git checkout frontend  # Switch to frontend branch
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```


3. **Additional system dependencies:**

    - **For pdf2image:**
       - **Ubuntu/Debian:**
          ```bash
          sudo apt-get install poppler-utils
          ```
       - **macOS:**
          ```bash
          brew install poppler
          ```
       - **Windows:**
          Download and install poppler from [poppler for Windows](http://blog.alivate.com.au/poppler-windows/)

    - **For OCR/Handwriting Recognition:**
       - **Tesseract OCR must be installed and on your PATH.**
       - **Ubuntu/Debian:**
          ```bash
          sudo apt-get install tesseract-ocr
          ```
       - **macOS:**
          ```bash
          brew install tesseract
          ```
       - **Windows:**
          Download and install Tesseract from [UB Mannheim builds](https://github.com/UB-Mannheim/tesseract/wiki) or [official repo](https://github.com/tesseract-ocr/tesseract). Add the install directory (e.g., `C:\Program Files\Tesseract-OCR`) to your PATH.

## Usage

### Web Application (Recommended)

1. **Start the Flask web server:**
   ```bash
   python flask_app.py
   ```

2. **Open your web browser and navigate to:**
   ```
   http://localhost:5000
   ```

3. **Use the web interface:**
   - Drag and drop PDF files onto the upload area or click to browse files
   - Reorder files by dragging them in the file list if needed
   - Toggle between dark and light themes using the theme switch
   - Click "Process PDFs" to upload and process your files
   - The processed PDF will automatically download as `formatted.pdf`

### Command Line (Alternative)

For batch processing and OCR (text/handwriting extraction) without the web interface:

1. **Prepare your PDF files:**
   - Create a `PDFS` directory in the project root
   - Place your PDF files in the `PDFS` directory

2. **Run the formatter:**
   ```bash
   python merge.py
   ```

3. **Output:**
   - The console will display recognized text for each PDF segment (using Tesseract OCR)
   - A single output file `output.pdf` will be generated containing all processed segments

## How It Works

### Processing Pipeline

1. **PDF Upload**: Files are uploaded through the web interface or placed in the PDFS directory
2. **PDF Conversion**: Each PDF is converted to images using `pdf2image`
3. **Content Detection**: Intelligent cropping removes white space and detects actual content boundaries
4. **Segmentation**: Images are divided into vertical segments with 8.5:11 aspect ratio
5. **Padding**: Final segments are padded to maintain consistent dimensions
6. **Analysis**: Each segment is analyzed for content distribution (useful for debugging)
7. **PDF Generation**: All segments are compiled into a single output PDF with proper margins
8. **Download**: The processed PDF is sent to the user for download

### Key Functions

- `crop_pdf_first_page()`: Converts PDF to image and crops to content boundaries
- `segment_image_by_aspect_ratio()`: Divides images into standard-sized segments
- `analyze_bottom_rows()`: Analyzes content distribution for quality assurance
- `create_pdf_from_images()`: Generates final PDF output with proper formatting
- **OCR Integration:** Uses `pytesseract` to extract text (including handwriting, if possible) from each image segment

## File Structure

```
cmps357-pdf-formatter/
├── flask_app.py          # Flask web application
├── merge.py              # Core PDF processing functions
├── requirements.txt      # Python dependencies (Flask + processing libs)
├── README.md            # This file
├── .gitignore           # Git ignore rules (excludes PDFs, PNGs, and temp files)
├── chatlog-09172025.md  # Development history and notes
└── PDFS/               # Directory for input PDF files (for CLI usage)
```

## Development Notes

- The web application provides a modern, responsive interface with dark/light theme support
- The tool is designed to handle portrait-oriented content as the default
- Segments are analyzed for content density to ensure quality
- The final segment in each image is padded with white space to maintain consistency
- All PDF and PNG files are ignored by git to avoid committing large binary files
- The Flask app runs in debug mode by default for development

## Troubleshooting

**Flask app won't start:**
- Ensure you've installed the requirements: `pip install -r requirements.txt`
- Check that Flask is properly installed: `python -c "import flask; print(flask.__version__)"`

**"No module named 'pdf2image'" error:**
- Ensure you've installed the requirements: `pip install -r requirements.txt`
- Verify poppler is installed on your system

**"No images found in PDF" error:**
- Check that your PDF files are not corrupted
- Ensure the PDF contains actual content (not just blank pages)

**Upload fails in web interface:**
- Verify that you're uploading valid PDF files
- Check browser console for any JavaScript errors
- Ensure Flask app has write permissions for temporary files

**Web page not loading:**
- Ensure the Flask app is running: `python flask_app.py`
- Check that you're accessing the correct URL: `http://localhost:5000`
- Verify no other application is using port 5000

## Contributing

This project was developed as part of CMPS 357 coursework. See `chatlog-09172025.md` for detailed development history and evolution of the codebase.

## License

This project is developed for educational purposes as part of the School of Computing and Informatics curriculum.