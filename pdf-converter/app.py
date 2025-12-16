from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
import subprocess
from pathlib import Path
import tempfile
import shutil
import zipfile
from PyPDF2 import PdfMerger

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Create necessary directories
UPLOAD_FOLDER = Path('uploads')
OUTPUT_FOLDER = Path('outputs')
UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {'docx', 'pptx', 'doc', 'ppt'}

def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def find_libreoffice():
    """Find LibreOffice executable path"""
    # Common LibreOffice paths for Windows
    possible_paths = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        r"C:\Program Files\LibreOffice\program\soffice.com",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.com",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Try to find in PATH
    try:
        result = subprocess.run(['where', 'soffice'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip().split('\n')[0]
    except:
        pass
    
    return None

def convert_to_pdf(input_file):
    """Convert Office file to PDF using LibreOffice"""
    soffice_path = find_libreoffice()
    
    if not soffice_path:
        raise Exception("LibreOffice not found. Please install LibreOffice to use this conversion tool.")
    
    output_path = OUTPUT_FOLDER / 'file.pdf'
    
    # Remove old PDF if exists
    if output_path.exists():
        output_path.unlink()
    
    # Convert using LibreOffice headless mode
    try:
        cmd = [
            soffice_path,
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', str(OUTPUT_FOLDER.absolute()),
            str(input_file.absolute())
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            raise Exception(f"Conversion failed: {result.stderr}")
        
        # LibreOffice creates PDF with original filename
        # Rename it to file.pdf
        original_name = input_file.stem + '.pdf'
        generated_pdf = OUTPUT_FOLDER / original_name
        
        if generated_pdf.exists() and generated_pdf != output_path:
            generated_pdf.rename(output_path)
        
        if not output_path.exists():
            raise Exception("PDF was not generated successfully")
        
        return output_path
        
    except subprocess.TimeoutExpired:
        raise Exception("Conversion timed out. The file might be too large or complex.")
    except Exception as e:
        raise Exception(f"Conversion error: {str(e)}")

def merge_pdfs(pdf_paths, output_filename='merged.pdf'):
    """Merge multiple PDF files into one"""
    merger = PdfMerger()
    
    try:
        for pdf_path in pdf_paths:
            merger.append(str(pdf_path))
        
        output_path = OUTPUT_FOLDER / output_filename
        merger.write(str(output_path))
        merger.close()
        
        # Clean up individual PDFs
        for pdf_path in pdf_paths:
            if pdf_path.exists():
                pdf_path.unlink()
        
        return output_path
    except Exception as e:
        merger.close()
        raise Exception(f"Merge error: {str(e)}")

@app.route('/')
def index():
    """Serve the main HTML page"""
    return app.send_static_file('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and conversion"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only docx, pptx, doc, and ppt files are supported.'}), 400
        
        # Save uploaded file
        filename = file.filename
        upload_path = UPLOAD_FOLDER / filename
        file.save(str(upload_path))
        
        try:
            # Convert to PDF
            pdf_path = convert_to_pdf(upload_path)
            
            # Clean up uploaded file
            upload_path.unlink()
            
            # Send PDF file
            return send_file(
                str(pdf_path),
                as_attachment=True,
                download_name='file.pdf',
                mimetype='application/pdf'
            )
            
        except Exception as e:
            # Clean up on error
            if upload_path.exists():
                upload_path.unlink()
            return jsonify({'error': str(e)}), 500
            
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/upload_batch', methods=['POST'])
def upload_batch():
    """Handle multiple file upload and conversion with optional merge"""
    try:
        # Check if files were uploaded
        if 'files[]' not in request.files:
            return jsonify({'error': 'No files uploaded'}), 400
        
        files = request.files.getlist('files[]')
        merge = request.form.get('merge', 'false').lower() == 'true'
        
        if not files or len(files) == 0:
            return jsonify({'error': 'No files selected'}), 400
        
        uploaded_paths = []
        pdf_paths = []
        
        try:
            # Save all uploaded files
            for file in files:
                if file.filename == '':
                    continue
                    
                if not allowed_file(file.filename):
                    # Clean up
                    for path in uploaded_paths:
                        if path.exists():
                            path.unlink()
                    return jsonify({'error': f'Invalid file type: {file.filename}'}), 400
                
                filename = file.filename
                upload_path = UPLOAD_FOLDER / filename
                file.save(str(upload_path))
                uploaded_paths.append(upload_path)
            
            # Convert all files to PDF
            for upload_path in uploaded_paths:
                # Use LibreOffice directly for batch conversion
                soffice_path = find_libreoffice()
                
                if not soffice_path:
                    raise Exception("LibreOffice not found. Please install LibreOffice to use this conversion tool.")
                
                try:
                    cmd = [
                        soffice_path,
                        '--headless',
                        '--convert-to', 'pdf',
                        '--outdir', str(OUTPUT_FOLDER.absolute()),
                        str(upload_path.absolute())
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                    
                    if result.returncode != 0:
                        raise Exception(f"Conversion failed: {result.stderr}")
                    
                    # LibreOffice creates PDF with original filename
                    pdf_path = OUTPUT_FOLDER / (upload_path.stem + '.pdf')
                    
                    if not pdf_path.exists():
                        raise Exception("PDF was not generated successfully")
                    
                    pdf_paths.append(pdf_path)
                    
                except subprocess.TimeoutExpired:
                    raise Exception("Conversion timed out. The file might be too large or complex.")
                except Exception as e:
                    raise Exception(f"Conversion error: {str(e)}")
                finally:
                    # Clean up uploaded file
                    if upload_path.exists():
                        upload_path.unlink()
            
            # Merge or return individual PDFs
            if merge and len(pdf_paths) > 1:
                merged_pdf = merge_pdfs(pdf_paths, 'merged.pdf')
                return send_file(
                    str(merged_pdf),
                    as_attachment=True,
                    download_name='merged.pdf',
                    mimetype='application/pdf'
                )
            else:
                # Create a ZIP file with all individual PDFs
                zip_path = OUTPUT_FOLDER / 'converted_files.zip'
                
                with zipfile.ZipFile(str(zip_path), 'w') as zipf:
                    for pdf_path in pdf_paths:
                        # Add each PDF to ZIP with its original name
                        zipf.write(str(pdf_path), pdf_path.name)
                
                # Clean up individual PDFs
                for pdf_path in pdf_paths:
                    if pdf_path.exists():
                        pdf_path.unlink()
                
                # Send ZIP file
                return send_file(
                    str(zip_path),
                    as_attachment=True,
                    download_name='converted_files.zip',
                    mimetype='application/zip'
                )
                
        except Exception as e:
            # Clean up on error
            for path in uploaded_paths:
                if path.exists():
                    path.unlink()
            for path in pdf_paths:
                if path.exists():
                    path.unlink()
            return jsonify({'error': str(e)}), 500
            
    except Exception as e:
        return jsonify({'error': f'Batch upload failed: {str(e)}'}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("PDF Conversion Server Starting...")
    print("=" * 60)
    print(f"Server running at: http://localhost:5000")
    print(f"Upload folder: {UPLOAD_FOLDER.absolute()}")
    print(f"Output folder: {OUTPUT_FOLDER.absolute()}")
    
    # Check for LibreOffice
    soffice_path = find_libreoffice()
    if soffice_path:
        print(f"LibreOffice found at: {soffice_path}")
    else:
        print("WARNING: LibreOffice not found!")
        print("   Please install LibreOffice from: https://www.libreoffice.org/download/")
    
    print("=" * 60)
    print()
    
    # Disable auto-reloader to prevent server restarts during file operations
    app.run(debug=True, port=5000, use_reloader=False)
