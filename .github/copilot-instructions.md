# PDF Formatter - GitHub Copilot Instructions

CMPS357 PDF Formatter is a Python application that processes PDF files by segmenting them into standardized 8.5:11 aspect ratio chunks and reformatting them into a single output PDF. The application crops PDF pages, analyzes content, and segments large documents into properly sized pages.

**ALWAYS reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Working Effectively

### Environment Setup and Dependencies
- Install system dependencies: `sudo apt-get update && sudo apt-get install -y poppler-utils`
- Install Python dependencies: `pip3 install pdf2image pillow numpy`
- Verify installation: `python3 -c "import pdf2image; import PIL; import numpy; print('All dependencies available')"`
- Python 3.12+ is required and available in the environment

### Building and Running
- **NO BUILD STEP REQUIRED** - This is a pure Python script application
- Create input directory: `mkdir -p PDFS`
- Place PDF files in the `PDFS/` directory
- Run the application: `python3 merge.py`
- **TYPICAL RUNTIME**: Single PDF takes ~0.7 seconds, multiple PDFs take ~2 seconds. NEVER CANCEL - application completes quickly.
- Output: Creates `output.pdf` containing all processed segments
- Verify syntax: `python3 -m py_compile merge.py`

### Core Application Workflow
1. Scans `PDFS/` directory for PDF files (case-insensitive `.pdf` extension)
2. For each PDF:
   - Extracts and crops the first page using content-based bounding box detection
   - Segments the cropped image vertically into 8.5:11 aspect ratio chunks
   - Analyzes bottom rows for content distribution
   - Pads final segment with white background if needed
3. Combines all segments into a single reformatted PDF (`output.pdf`)

### Required Directory Structure
```
/
├── merge.py (main application)
├── PDFS/ (input directory - MUST exist or application crashes)
│   ├── document1.pdf
│   └── document2.pdf
└── output.pdf (generated output)
```

### Error Conditions and Recovery
- **PDFS directory missing**: Application crashes with `FileNotFoundError`. Create with `mkdir -p PDFS`
- **Empty PDFS directory**: Application runs successfully, creates no output
- **Non-PDF files in PDFS**: Ignored automatically (only processes `.pdf` files)
- **Corrupted PDFs**: May crash with `ValueError: No images found in PDF`

## Validation and Testing

### Manual Validation Scenarios
**ALWAYS run these validation steps after making code changes:**

1. **Basic functionality test**:
   ```bash
   mkdir -p PDFS
   # Create a test PDF (you'll need to provide one or create using PIL)
   python3 merge.py
   ls -la output.pdf  # Should exist and have reasonable size
   ```

2. **Multi-PDF processing test**:
   ```bash
   # Place 2-3 PDFs in PDFS directory
   python3 merge.py
   # Verify output.pdf contains segments from all input PDFs
   ```

3. **Edge case testing**:
   ```bash
   # Test empty directory
   mkdir -p PDFS && rm -f PDFS/*.pdf
   python3 merge.py  # Should complete without error
   
   # Test missing directory
   rmdir PDFS
   python3 merge.py  # Should fail with clear error message
   mkdir -p PDFS  # Restore for next tests
   ```

4. **Content verification**:
   - Open `output.pdf` in a PDF viewer if available
   - Verify segments maintain proper aspect ratios
   - Check that content is properly cropped and positioned

### Performance Expectations
- **Single small PDF**: ~0.7 seconds
- **Multiple PDFs (2-3 files)**: ~2 seconds  
- **NEVER CANCEL**: Application completes quickly, no long-running operations

## Common Development Tasks

### Code Structure
The application consists of four main functions in `merge.py`:
- `crop_pdf_first_page()`: Extracts and crops PDF content using grayscale thresholding
- `analyze_bottom_rows()`: Analyzes content distribution in image segments  
- `segment_image_by_aspect_ratio()`: Divides images into 8.5:11 ratio segments
- `create_pdf_from_images()`: Assembles final PDF with proper margins and scaling

### Making Changes
- **ALWAYS test changes** with the validation scenarios above
- **No linting tools configured** - rely on syntax checking: `python3 -m py_compile merge.py`
- **No automated testing framework** - use manual validation only
- **No CI/CD pipeline** - test locally before committing

### Key Constants and Configuration
- Default aspect ratio: 8.5:11 (US Letter)
- Default margins: 0.5 inches
- Default DPI: 300
- Content threshold: 240 (for white pixel detection)
- Analysis rows: 100 (bottom rows analyzed per segment)

## Debugging and Troubleshooting

### Common Issues
1. **Import errors**: Ensure `pip3 install pdf2image pillow numpy` completed successfully
2. **poppler-utils missing**: Install with `sudo apt-get install -y poppler-utils`
3. **No output generated**: Check that PDFS directory contains valid PDF files
4. **Application hangs**: Should never happen - application completes in seconds

### Diagnostic Commands
- Check dependencies: `python3 -c "import pdf2image; import PIL; import numpy"`
- Verify poppler: `pdftoppm -h` (should show help)
- Check PDF directory: `ls -la PDFS/`
- Verify file permissions: `ls -la merge.py` (should be readable)

## File Management
- **Input files**: Place PDFs in `PDFS/` directory
- **Output files**: `output.pdf` is overwritten on each run
- **Temporary files**: None created
- **Cache files**: Python cache files (`__pycache__/`) are ignored by .gitignore
- **Generated files**: PDF and PNG files are ignored by .gitignore

## Development History
See `chatlog-09172025.md` for detailed development evolution and decision rationale. Key changes include:
- Refactored from horizontal to vertical segmentation  
- Added content analysis for segment quality assessment
- Implemented padding for final segments to maintain consistent sizing
- Added support for multiple PDF processing in single run