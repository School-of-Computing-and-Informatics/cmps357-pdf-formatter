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
        body {
            background: linear-gradient(120deg, #f8fafc 0%, #e0e7ff 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 0;
        }
        .container {
            background: #fff;
            padding: 2.5rem 2rem 2rem 2rem;
            border-radius: 1.2rem;
            box-shadow: 0 4px 24px 0 rgba(80, 80, 180, 0.10);
            text-align: center;
            max-width: 400px;
            width: 100%;
        }
        h1 {
            color: #3730a3;
            margin-bottom: 1.2rem;
            font-size: 1.6rem;
            letter-spacing: 0.01em;
        }
        .drop-area {
            border: 2px dashed #818cf8;
            border-radius: 0.7rem;
            background: #f1f5f9;
            padding: 1.2rem 0.5rem;
            margin-bottom: 1.2rem;
            cursor: pointer;
            transition: background 0.2s, border-color 0.2s;
        }
        .drop-area.dragover {
            background: #e0e7ff;
            border-color: #6366f1;
        }
        .file-list {
            list-style: none;
            padding: 0;
            margin: 0 0 1.2rem 0;
            min-height: 1.5rem;
        }
        .file-list li {
            background: #eef2ff;
            border-radius: 0.4rem;
            margin-bottom: 0.5rem;
            padding: 0.5rem 0.8rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 1rem;
            cursor: grab;
            border: 1px solid #c7d2fe;
        }
        .file-list li.dragging {
            opacity: 0.5;
        }
        .move-btn {
            background: none;
            border: none;
            color: #6366f1;
            font-size: 1.2rem;
            cursor: pointer;
            margin-left: 0.3rem;
            padding: 0.1rem 0.3rem;
            border-radius: 0.2rem;
            transition: background 0.15s;
        }
        .move-btn:hover {
            background: #c7d2fe;
        }
        input[type="submit"] {
            background: linear-gradient(90deg, #6366f1 0%, #818cf8 100%);
            color: #fff;
            border: none;
            border-radius: 0.4rem;
            padding: 0.7rem 2.2rem;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
            box-shadow: 0 2px 8px 0 rgba(99, 102, 241, 0.10);
        }
        input[type="submit"]:hover {
            background: linear-gradient(90deg, #4f46e5 0%, #6366f1 100%);
        }
        .footer {
            margin-top: 1.5rem;
            color: #64748b;
            font-size: 0.95rem;
        }
        #real-file-input {
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>PDF Formatter</h1>
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
    <script>
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
