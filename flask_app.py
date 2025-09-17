from flask import Flask, request, render_template_string, send_file
import tempfile
import os
import io
from merge import crop_pdf_first_page, segment_image_by_aspect_ratio, create_pdf_from_images

app = Flask(__name__)

UPLOAD_FORM = '''
<!doctype html>
<title>PDF Formatter</title>
<h1>Upload a PDF to format</h1>
<form method=post enctype=multipart/form-data>
  <input type=file name=pdf_file accept="application/pdf">
  <input type=submit value=Upload>
</form>
'''

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            return 'No file part', 400
        file = request.files['pdf_file']
        if file.filename == '':
            return 'No selected file', 400
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, 'input.pdf')
            file.save(input_path)
            cropped_img = crop_pdf_first_page(input_path)
            segments = segment_image_by_aspect_ratio(cropped_img, 8.5, 11)
            output_path = os.path.join(tmpdir, 'output.pdf')
            create_pdf_from_images(segments, output_path)
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
