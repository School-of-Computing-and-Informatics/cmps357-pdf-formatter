# CMPS 357 PDF Formatter

A Python utility for processing and reformatting PDF documents by segmenting them into standardized pages with proper aspect ratios.

## Overview

This tool takes PDF files and segments them into properly formatted pages with a standard 8.5:11 aspect ratio (US Letter format). It crops, segments, and reformats PDF content to create clean, uniform output suitable for printing or digital distribution.

## Features

- **PDF to Image Conversion**: Converts PDF pages to images for processing
- **Intelligent Cropping**: Automatically detects and crops content boundaries
- **Vertical Segmentation**: Splits tall images into multiple segments with consistent aspect ratios
- **Padding and Alignment**: Ensures all segments maintain proper dimensions
- **Batch Processing**: Processes multiple PDF files from a directory
- **Output Generation**: Creates a single merged PDF with all processed segments

## Dependencies

The project requires the following Python packages:

- `pdf2image` (1.17.0) - For converting PDF files to images
- `Pillow` (10.3.0) - For image processing and manipulation
- `numpy` (1.26.4) - For numerical operations on image arrays

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
├── merge.py              # Main processing script
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── .gitignore           # Git ignore rules (excludes PDFs and PNGs)
├── chatlog-09172025.md  # Development history and notes
└── PDFS/               # Directory for input PDF files (create this)
```

## Development Notes

- The tool is designed to handle portrait-oriented content as the default
- Segments are analyzed for content density to ensure quality
- The final segment in each image is padded with white space to maintain consistency
- All PDF and PNG files are ignored by git to avoid committing large binary files

## Troubleshooting

**"No module named 'pdf2image'" error:**
- Ensure you've installed the requirements: `pip install -r requirements.txt`
- Verify poppler is installed on your system

**"No images found in PDF" error:**
- Check that your PDF files are not corrupted
- Ensure the PDF contains actual content (not just blank pages)

**Output PDF is empty:**
- Verify that the `PDFS` directory exists and contains PDF files
- Check that the PDF files have the `.pdf` extension (case-insensitive)

## Contributing

This project was developed as part of CMPS 357 coursework. See `chatlog-09172025.md` for detailed development history and evolution of the codebase.

## License

This project is developed for educational purposes as part of the School of Computing and Informatics curriculum.