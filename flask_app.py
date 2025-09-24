from flask import Flask, request, render_template_string, send_file
import tempfile
import os
import io
from merge import crop_pdf_first_page, segment_image_by_aspect_ratio, create_pdf_from_images

app = Flask(__name__)

UPLOAD_FORM = '''
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>PDF Formatter</title>
    <style>
        /* Base styles - no theme dependencies */
        * {
            box-sizing: border-box;
        }
        
        body {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 0;
            transition: background 0.3s ease, color 0.3s ease;
            /* Force initial dark mode styles */
            background: linear-gradient(120deg, #181a20 0%, #232946 100%);
            color: #e0e7ef;
        }
        .container {
            padding: 2.5rem 2rem 2rem 2rem;
            border-radius: 1.2rem;
            text-align: center;
            max-width: 400px;
            width: 100%;
            transition: background 0.3s ease, box-shadow 0.3s ease;
            /* Force initial dark mode styles */
            background: #232946;
            color: #e0e7ef;
            box-shadow: 0 4px 24px 0 rgba(30, 30, 60, 0.25);
        }
        h1 {
            margin-bottom: 1.2rem;
            font-size: 1.6rem;
            letter-spacing: 0.01em;
            transition: color 0.3s ease;
            /* Force initial dark mode styles */
            color: #a5b4fc;
        }
        .drop-area {
            border-radius: 0.7rem;
            padding: 1.2rem 0.5rem;
            margin-bottom: 1.2rem;
            cursor: pointer;
            transition: background 0.2s, border-color 0.2s;
            /* Force initial dark mode styles */
            border: 2px dashed #6366f1;
            background: #232946;
            color: #e0e7ef;
        }
        .drop-area.dragover {
            background: #3730a3;
            border-color: #a5b4fc;
        }
        .file-list {
            list-style: none;
            padding: 0;
            margin: 0 0 1.2rem 0;
            min-height: 1.5rem;
        }
        .file-list li {
            border-radius: 0.4rem;
            margin-bottom: 0.5rem;
            padding: 0.5rem 0.8rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 1rem;
            cursor: grab;
            transition: background 0.3s ease, border-color 0.3s ease;
            /* Force initial dark mode styles */
            background: #1a1b22;
            color: #e0e7ef;
            border: 1px solid #6366f1;
        }
        .file-list li.dragging {
            opacity: 0.5;
        }
        .file-list li.dragover {
            border: 2px dashed #a5b4fc;
            background: #3730a3;
        }
        .move-btn {
            background: none;
            border: none;
            font-size: 1.2rem;
            cursor: pointer;
            margin-left: 0.3rem;
            padding: 0.1rem 0.3rem;
            border-radius: 0.2rem;
            transition: background 0.15s, color 0.3s ease;
            /* Force initial dark mode styles */
            color: #a5b4fc;
        }
        .move-btn:hover {
            background: #3730a3;
        }
        input[type="submit"] {
            border: none;
            border-radius: 0.4rem;
            padding: 0.7rem 2.2rem;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
            box-shadow: 0 2px 8px 0 rgba(99, 102, 241, 0.10);
            /* Force initial dark mode styles */
            background: linear-gradient(90deg, #3730a3 0%, #6366f1 100%);
            color: #fff;
        }
        input[type="submit"]:hover {
            background: linear-gradient(90deg, #6366f1 0%, #818cf8 100%);
        }
        .footer {
            margin-top: 1.5rem;
            font-size: 0.95rem;
            transition: color 0.3s ease;
            /* Force initial dark mode styles */
            color: #a5b4fc;
        }
        #real-file-input {
            display: none;
        }
    </style>

    <style id="light-mode-style">
    /* Light mode overrides - only applied when body has .light class */
    body.light {
        background: linear-gradient(120deg, #f8fafc 0%, #e0e7ff 100%) !important;
        color: #22223b !important;
    }
    body.light .container {
        background: #fff !important;
        color: #22223b !important;
        box-shadow: 0 4px 24px 0 rgba(80, 80, 180, 0.10) !important;
    }
    body.light h1 {
        color: #3730a3 !important;
    }
    body.light .drop-area {
        border: 2px dashed #818cf8 !important;
        background: #f1f5f9 !important;
        color: #22223b !important;
    }
    body.light .drop-area.dragover {
        background: #e0e7ff !important;
        border-color: #6366f1 !important;
    }
    body.light .file-list li {
        background: #eef2ff !important;
        color: #22223b !important;
        border: 1px solid #c7d2fe !important;
    }
    body.light .file-list li.dragover {
        border: 2px dashed #6366f1 !important;
        background: #e0e7ff !important;
    }
    body.light .move-btn {
        color: #6366f1 !important;
    }
    body.light .move-btn:hover {
        background: #c7d2fe !important;
    }
    body.light input[type="submit"] {
        background: linear-gradient(90deg, #6366f1 0%, #818cf8 100%) !important;
        color: #fff !important;
    }
    body.light input[type="submit"]:hover {
        background: linear-gradient(90deg, #4f46e5 0%, #6366f1 100%) !important;
    }
    body.light .footer {
        color: #64748b !important;
    }
    </style>
</head>
<body>
    <div class="container">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <h1 style="margin-bottom: 0;">PDF Formatter</h1>
                        <div style="position: relative; top: 0; right: 0; display: flex; align-items: center; gap: 0.3rem;">
                                                <span class="slider-icon slider-moon" title="Dark mode" aria-label="Dark mode" style="font-size: 1.3rem;">&#x1F319;</span>
                                <label class="switch">
                                    <input type="checkbox" id="slider-toggle">
                                    <span class="slider round"></span>
                                </label>
                                                <span class="slider-icon slider-sun" title="Light mode" aria-label="Light mode" style="font-size: 1.3rem;">&#x2600;&#xFE0F;</span>
                        </div>
                </div>
        <form id="pdf-form" method="post" enctype="multipart/form-data">
            <div class="drop-area" id="drop-area">
                <span id="drop-text">Drag & drop PDF files here or click to select</span>
                <input id="real-file-input" type="file" name="pdf_file" accept="application/pdf" multiple>
            </div>
            <ul class="file-list" id="file-list"></ul>
            <input type="submit" value="Upload & Format">
        </form>
        <div class="footer">Your PDF stays private and is never stored.</div>
    </div>
        <style>
        .slider-icon {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          height: 28px;
          width: 28px;
          user-select: none;
          pointer-events: none;
        }
                .slider-moon, .slider-sun {
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    height: 28px;
                    width: 28px;
                    user-select: none;
                    pointer-events: none;
                }
        .switch {
            position: relative;
            display: inline-block;
            width: 48px;
            height: 28px;
        }
        .switch input {display:none;}
        .slider {
            position: absolute;
            cursor: pointer;
            top: 0; left: 0; right: 0; bottom: 0;
            background-color: #6366f1;
            transition: .4s;
            border-radius: 28px;
        }
        .slider:before {
            position: absolute;
            content: "";
            height: 22px;
            width: 22px;
            left: 3px;
            bottom: 3px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }
        input:checked + .slider {
            background-color: #a5b4fc;
        }
        input:checked + .slider:before {
            transform: translateX(20px);
        }
        </style>
        <script>
            // Slider toggle event and theme switching
            document.addEventListener('DOMContentLoaded', function() {
                const slider = document.getElementById('slider-toggle');
                
                function setTheme(isLight) {
                    const body = document.body;
                    if (isLight) {
                        body.classList.add('light');
                        if (slider) slider.checked = true;
                    } else {
                        body.classList.remove('light');
                        if (slider) slider.checked = false;
                    }
                }
                
                if (slider) {
                    // Check current state - if light class exists, sync slider
                    const isCurrentlyLight = document.body.classList.contains('light');
                    slider.checked = isCurrentlyLight;
                    
                    slider.addEventListener('change', function() {
                        setTheme(slider.checked);
                    });
                }
            });
        const dropArea = document.getElementById('drop-area');
        const realInput = document.getElementById('real-file-input');
        const fileList = document.getElementById('file-list');
        let files = [];

        dropArea.addEventListener('click', () => realInput.click());
        dropArea.addEventListener('dragover', e => {
            e.preventDefault();
            dropArea.classList.add('dragover');
        });
        dropArea.addEventListener('dragleave', e => {
            e.preventDefault();
            dropArea.classList.remove('dragover');
        });
        dropArea.addEventListener('drop', e => {
            e.preventDefault();
            dropArea.classList.remove('dragover');
            addFiles(e.dataTransfer.files);
        });
        realInput.addEventListener('change', e => {
            addFiles(e.target.files);
            realInput.value = '';
        });

        function addFiles(fileListObj) {
            for (let f of fileListObj) {
                if (f.type === 'application/pdf' && !files.some(existing => existing.name === f.name && existing.size === f.size)) {
                    files.push(f);
                }
            }
            renderFileList();
        }

        function renderFileList() {
            fileList.innerHTML = '';
            files.forEach((file, idx) => {
                const li = document.createElement('li');
                li.textContent = file.name;
                // Move up button
                const upBtn = document.createElement('button');
                upBtn.innerHTML = '↑';
                upBtn.className = 'move-btn';
                upBtn.title = 'Move up';
                upBtn.disabled = idx === 0;
                upBtn.onclick = e => {
                    e.preventDefault();
                    if (idx > 0) {
                        [files[idx-1], files[idx]] = [files[idx], files[idx-1]];
                        renderFileList();
                    }
                };
                // Move down button
                const downBtn = document.createElement('button');
                downBtn.innerHTML = '↓';
                downBtn.className = 'move-btn';
                downBtn.title = 'Move down';
                downBtn.disabled = idx === files.length-1;
                downBtn.onclick = e => {
                    e.preventDefault();
                    if (idx < files.length-1) {
                        [files[idx+1], files[idx]] = [files[idx], files[idx+1]];
                        renderFileList();
                    }
                };
                li.appendChild(upBtn);
                li.appendChild(downBtn);

                // Drag-and-drop attributes and handlers
                li.setAttribute('draggable', 'true');
                li.dataset.idx = idx;

                li.addEventListener('dragstart', function(e) {
                    li.classList.add('dragging');
                    e.dataTransfer.effectAllowed = 'move';
                    e.dataTransfer.setData('text/plain', idx);
                });
                li.addEventListener('dragend', function(e) {
                    li.classList.remove('dragging');
                });
                li.addEventListener('dragover', function(e) {
                    e.preventDefault();
                    li.classList.add('dragover');
                });
                li.addEventListener('dragleave', function(e) {
                    li.classList.remove('dragover');
                });
                li.addEventListener('drop', function(e) {
                    e.preventDefault();
                    li.classList.remove('dragover');
                    const fromIdx = parseInt(e.dataTransfer.getData('text/plain'));
                    const toIdx = idx;
                    if (fromIdx !== toIdx) {
                        const moved = files.splice(fromIdx, 1)[0];
                        files.splice(toIdx, 0, moved);
                        renderFileList();
                    }
                });

                fileList.appendChild(li);
            });
        }

        // On submit, build a FormData with files in the chosen order
        document.getElementById('pdf-form').addEventListener('submit', function(e) {
            if (!files.length) {
                alert('Please select at least one PDF file.');
                e.preventDefault();
                return;
            }
            const formData = new FormData();
            files.forEach(f => formData.append('pdf_file', f));
            // Submit via fetch to preserve order
            e.preventDefault();
            fetch('/', {
                method: 'POST',
                body: formData
            }).then(async resp => {
                if (resp.ok) {
                    const blob = await resp.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'formatted.pdf';
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    window.URL.revokeObjectURL(url);
                } else {
                    alert('Error processing PDF(s).');
                }
            });
        });
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            return 'No file part', 400
        files = request.files.getlist('pdf_file')
        if not files or all(f.filename == '' for f in files):
            return 'No selected file', 400
        with tempfile.TemporaryDirectory() as tmpdir:
            all_segments = []
            for file in files:
                if file and file.filename:
                    input_path = os.path.join(tmpdir, file.filename)
                    file.save(input_path)
                    cropped_img = crop_pdf_first_page(input_path)
                    segments = segment_image_by_aspect_ratio(cropped_img, 8.5, 11)
                    all_segments.extend(segments)
            if not all_segments:
                return 'No valid PDF files processed', 400
            output_path = os.path.join(tmpdir, 'output.pdf')
            create_pdf_from_images(all_segments, output_path)
            # Read the PDF into memory and send as BytesIO
            with open(output_path, 'rb') as f:
                pdf_bytes = f.read()
            return send_file(
                io.BytesIO(pdf_bytes),
                as_attachment=True,
                download_name='formatted.pdf',
                mimetype='application/pdf'
            )
    return render_template_string(UPLOAD_FORM)

if __name__ == '__main__':
    app.run(debug=True)
