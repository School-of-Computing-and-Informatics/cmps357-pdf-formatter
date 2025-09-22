# CMPS 357 PDF Formatter

A Python utility for processing and reformatting PDF documents by segmenting them into standardized pages with proper aspect ratios. Available as both a command-line tool and a web interface.

## Overview

This tool takes PDF files and segments them into properly formatted pages with a standard 8.5:11 aspect ratio (US Letter format). It crops, segments, and reformats PDF content to create clean, uniform output suitable for printing or digital distribution.

The application is available in two modes:
- **Command-line interface** (`merge.py`) - Batch process PDFs from a directory
- **Web interface** (`flask_app.py`) - Interactive web application with drag & drop functionality

## Features

### Core Processing Features
- **PDF to Image Conversion**: Converts PDF pages to images for processing
- **Intelligent Cropping**: Automatically detects and crops content boundaries
- **Vertical Segmentation**: Splits tall images into multiple segments with consistent aspect ratios
- **Content Analysis**: Analyzes content distribution for optimal segment boundaries
- **Padding and Alignment**: Ensures all segments maintain proper dimensions
- **Batch Processing**: Processes multiple PDF files from a directory
- **Output Generation**: Creates a single merged PDF with all processed segments

### Web Interface Features
- **Modern Web UI**: Clean, responsive interface with dark/light mode toggle
- **Drag & Drop Upload**: Intuitive file upload with visual feedback
- **File Reordering**: Drag files to reorder processing sequence
- **Multiple File Support**: Process multiple PDFs in a single operation
- **Instant Download**: Automatically downloads processed PDF
- **Privacy-First**: Files are processed locally and never stored on server

## Dependencies

The project requires the following Python packages:

- `pdf2image` (1.17.0) - For converting PDF files to images
- `Pillow` (10.3.0) - For image processing and manipulation
- `numpy` (1.26.4) - For numerical operations on image arrays
- `Flask` (3.0.0) - For web interface functionality

All dependencies are listed in `requirements.txt`.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/School-of-Computing-and-Informatics/cmps357-pdf-formatter.git
   cd cmps357-pdf-formatter
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Additional system dependencies (for pdf2image):**
   
   **On Ubuntu/Debian:**
   ```bash
   sudo apt-get install poppler-utils
   ```
   
   **On macOS:**
   ```bash
   brew install poppler
   ```
   
   **On Windows:**
   Download and install poppler from [poppler for Windows](http://blog.alivate.com.au/poppler-windows/)

## Usage

### Command-Line Interface

1. **Prepare your PDF files:**
   - Create a `PDFS` directory in the project root
   - Place your PDF files in the `PDFS` directory

2. **Run the formatter:**
   ```bash
   python merge.py
   ```

3. **Output:**
   - The tool will process all PDF files in the `PDFS` directory
   - A single output file `output.pdf` will be generated containing all processed segments

### Web Interface

1. **Start the web server:**
   ```bash
   python flask_app.py
   ```

2. **Access the application:**
   - Open your browser to `http://localhost:5000`
   - The web interface will load with an upload area

3. **Upload and process PDFs:**
   - Drag & drop PDF files onto the upload area, or click to select files
   - Reorder files by dragging them in the file list or using the arrow buttons
   - Click "Upload & Format" to process the files
   - The processed PDF will automatically download as `formatted.pdf`

4. **Features:**
   - Toggle between dark and light modes using the switch in the top-right
   - Files are processed in the order they appear in the list
   - Multiple files are combined into a single output PDF
   - All processing happens locally - files are never stored on the server

## How It Works

### Processing Pipeline

1. **PDF Conversion**: Each PDF is converted to images using `pdf2image`
2. **Content Detection**: Intelligent cropping removes white space and detects actual content boundaries
3. **Segmentation**: Images are divided into vertical segments with 8.5:11 aspect ratio
4. **Padding**: Final segments are padded to maintain consistent dimensions
5. **Analysis**: Each segment is analyzed for content distribution (useful for debugging)
6. **PDF Generation**: All segments are compiled into a single output PDF with proper margins

### Key Functions

- `crop_pdf_first_page()`: Converts PDF to image and crops to content boundaries
- `segment_image_by_aspect_ratio()`: Divides images into standard-sized segments
- `analyze_bottom_rows()`: Analyzes content distribution for quality assurance
- `create_pdf_from_images()`: Generates final PDF output with proper formatting

## File Structure

```
cmps357-pdf-formatter/
├── merge.py              # Main CLI processing script
├── flask_app.py          # Web interface application
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── .gitignore           # Git ignore rules (excludes PDFs and PNGs)
├── chatlog-09172025.md  # Development history and notes
└── PDFS/               # Directory for input PDF files (create this for CLI mode)
```

## Development Notes

- The tool is designed to handle portrait-oriented content as the default
- Segments are analyzed for content density to ensure quality
- The final segment in each image is padded with white space to maintain consistency
- All PDF and PNG files are ignored by git to avoid committing large binary files
- Both CLI and web interfaces use the same core processing functions (`crop_pdf_first_page`, `segment_image_by_aspect_ratio`, `analyze_bottom_rows`, `create_pdf_from_images`)
- The web interface includes modern UI features like dark/light mode toggle and drag & drop functionality

## Troubleshooting

### Command-Line Interface Issues

**"No module named 'pdf2image'" error:**
- Ensure you've installed the requirements: `pip install -r requirements.txt`
- Verify poppler is installed on your system

**"No images found in PDF" error:**
- Check that your PDF files are not corrupted
- Ensure the PDF contains actual content (not just blank pages)

**Output PDF is empty:**
- Verify that the `PDFS` directory exists and contains PDF files
- Check that the PDF files have the `.pdf` extension (case-insensitive)

### Web Interface Issues

**"No module named 'flask'" error:**
- Ensure you've installed all requirements: `pip install -r requirements.txt`
- Flask should be included in the requirements

**Web server won't start:**
- Check that no other application is using port 5000
- Try running with: `python flask_app.py` and check for error messages

**File upload not working:**
- Ensure you're uploading PDF files (other file types are filtered out)
- Check browser console for JavaScript errors
- Verify that the files are not corrupted

**Processed PDF download fails:**
- Check that the uploaded PDFs contain valid content
- Ensure sufficient disk space for processing temporary files
- Try with smaller PDF files first

## Contributing

This project was developed as part of CMPS 357 coursework. See `chatlog-09172025.md` for detailed development history and evolution of the codebase.

## License

This project is developed for educational purposes as part of the School of Computing and Informatics curriculum.