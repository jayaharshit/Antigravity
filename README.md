# PDF Converter Web Application

A modern, beautiful web application for converting Office documents (docx, pptx, doc, ppt) to PDF format with optional merge functionality.

![PDF Converter](https://img.shields.io/badge/PDF-Converter-purple?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0+-green?style=for-the-badge&logo=flask)

## ✨ Features

- **Multiple File Upload** - Select and convert multiple files at once
- **PDF Merge** - Combine all uploaded files into a single PDF
- **Drag & Drop** - Intuitive drag-and-drop interface
- **Beautiful UI** - Modern dark theme with glassmorphism effects
- **Real-time Progress** - Live conversion progress tracking
- **High Quality** - LibreOffice-powered conversion preserves formatting
- **Secure & Private** - All processing happens locally

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- LibreOffice ([Download here](https://www.libreoffice.org/download/))

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/pdf-converter.git
   cd pdf-converter
   ```

2. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Install LibreOffice**
   - Download from [libreoffice.org](https://www.libreoffice.org/download/)
   - Install to the default location for auto-detection

### Running the Application

```bash
python app.py
```

Open your browser and navigate to `http://localhost:5000`

## 📖 Usage

### Convert Single File

1. Click the upload zone or drag a file
2. Conversion starts automatically
3. PDF downloads with the original filename

### Convert Multiple Files

1. Select multiple files or drag them into the upload zone
2. **Optional**: Check "Merge all files into one PDF" to combine them
3. Files convert sequentially (or merge into one)
4. PDFs download automatically

## 🛠️ Technology Stack

**Frontend:**

- HTML5 with semantic markup
- Vanilla CSS with modern design patterns
- JavaScript (ES6+) for interactions

**Backend:**

- Python 3 with Flask framework
- Flask-CORS for cross-origin requests
- PyPDF2 for PDF merging
- LibreOffice for document conversion

## 📁 Project Structure

```
pdf-converter/
├── app.py              # Flask backend server
├── requirements.txt    # Python dependencies
├── .gitignore         # Git ignore rules
├── static/
│   ├── index.html     # Main web interface
│   ├── style.css      # Modern styling
│   └── script.js      # Frontend logic
├── uploads/           # Temporary upload storage (auto-created)
└── outputs/           # Converted PDF storage (auto-created)
```

## 🎨 Features Showcase

- **Modern UI** - Dark theme with vibrant gradients
- **Glassmorphism** - Beautiful frosted-glass card effects
- **Smooth Animations** - Hover effects and transitions
- **Responsive Design** - Works on all screen sizes
- **Custom Checkbox** - Gradient-styled merge option

## 🔧 Configuration

The application uses LibreOffice for conversion. Supported file types:

- `.docx` - Microsoft Word (2007+)
- `.doc` - Microsoft Word (Legacy)
- `.pptx` - Microsoft PowerPoint (2007+)
- `.ppt` - Microsoft PowerPoint (Legacy)

Maximum file size: **50MB**

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest new features
- Submit pull requests

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Powered by [LibreOffice](https://www.libreoffice.org/)
- PDF merging by [PyPDF2](https://pypdf2.readthedocs.io/)

---

**Made with ❤️ by Jaya**
