// DOM Elements
const uploadZone = document.getElementById("uploadZone");
const fileInput = document.getElementById("fileInput");
const mergeCheckbox = document.getElementById("mergeCheckbox");
const progressContainer = document.getElementById("progressContainer");
const messageContainer = document.getElementById("messageContainer");
const messageIcon = document.getElementById("messageIcon");
const messageTitle = document.getElementById("messageTitle");
const messageText = document.getElementById("messageText");
const convertAnother = document.getElementById("convertAnother");

// Supported file types
const ALLOWED_TYPES = [".docx", ".pptx", ".doc", ".ppt"];
const ALLOWED_MIME_TYPES = [
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "application/vnd.openxmlformats-officedocument.presentationml.presentation",
  "application/msword",
  "application/vnd.ms-powerpoint",
];

// Event Listeners
uploadZone.addEventListener("click", () => fileInput.click());
uploadZone.addEventListener("dragover", handleDragOver);
uploadZone.addEventListener("dragleave", handleDragLeave);
uploadZone.addEventListener("drop", handleDrop);
fileInput.addEventListener("change", handleFileSelect);
convertAnother.addEventListener("click", resetUpload);

// Drag and Drop Handlers
function handleDragOver(e) {
  e.preventDefault();
  e.stopPropagation();
  uploadZone.classList.add("dragover");
}

function handleDragLeave(e) {
  e.preventDefault();
  e.stopPropagation();
  uploadZone.classList.remove("dragover");
}

function handleDrop(e) {
  e.preventDefault();
  e.stopPropagation();
  uploadZone.classList.remove("dragover");

  const files = Array.from(e.dataTransfer.files);
  if (files.length > 0) {
    handleFiles(files);
  }
}

function handleFileSelect(e) {
  const files = Array.from(e.target.files);
  if (files.length > 0) {
    handleFiles(files);
  }
}

// File Validation
function validateFile(file) {
  const fileName = file.name.toLowerCase();
  const fileExtension = "." + fileName.split(".").pop();

  if (!ALLOWED_TYPES.includes(fileExtension)) {
    return {
      valid: false,
      error: `Invalid file type. Please upload one of: ${ALLOWED_TYPES.join(
        ", "
      )}`,
    };
  }

  // Check file size (max 50MB)
  const maxSize = 50 * 1024 * 1024;
  if (file.size > maxSize) {
    return {
      valid: false,
      error: "File is too large. Maximum size is 50MB.",
    };
  }

  return { valid: true };
}

// Handle Multiple Files
function handleFiles(files) {
  // Validate all files first
  const validationResults = files.map(file => ({
    file,
    validation: validateFile(file)
  }));

  const invalidFiles = validationResults.filter(r => !r.validation.valid);

  if (invalidFiles.length > 0) {
    const errorMessages = invalidFiles.map(r => 
      `${r.file.name}: ${r.validation.error}`
    ).join('\n');
    showError(errorMessages);
    return;
  }

  // Upload all valid files
  uploadFiles(files);
}

// Upload and Convert Multiple Files
async function uploadFiles(files) {
  // Show progress
  uploadZone.style.display = "none";
  progressContainer.style.display = "block";
  messageContainer.style.display = "none";

  const mergeFiles = mergeCheckbox.checked && files.length > 1;
  
  if (mergeFiles) {
    // Use batch endpoint with merge option
    const progressText = document.querySelector('.progress-text');
    const progressSubtext = document.querySelector('.progress-subtext');
    
    progressText.textContent = `Merging ${files.length} files...`;
    progressSubtext.textContent = 'Converting and combining into one PDF';
    
    const formData = new FormData();
    for (let file of files) {
      formData.append('files[]', file);
    }
    formData.append('merge', 'true');
    
    try {
      const response = await fetch('http://localhost:5000/upload_batch', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Merge failed');
      }
      
      // Get the merged PDF blob
      const blob = await response.blob();
      
      // Download merged PDF
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'merged.pdf';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      showSuccess(
        `${files.length} files merged successfully!`,
        'Your merged PDF has been downloaded.'
      );
      
    } catch (error) {
      console.error('Merge error:', error);
      showError(error.message || 'An error occurred during merging. Please try again.');
    }
    
  } else {
    // Convert files individually but download as ZIP
    const progressText = document.querySelector('.progress-text');
    const progressSubtext = document.querySelector('.progress-subtext');
    
    progressText.textContent = `Converting ${files.length} file${files.length > 1 ? 's' : ''}...`;
    progressSubtext.textContent = 'Processing your files';
    
    const formData = new FormData();
    for (let file of files) {
      formData.append('files[]', file);
    }
    formData.append('merge', 'false');
    
    try {
      const response = await fetch('http://localhost:5000/upload_batch', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Conversion failed');
      }
      
      // Get the ZIP blob
      const blob = await response.blob();
      
      // Download ZIP file
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'converted_files.zip';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      showSuccess(
        `${files.length} file${files.length > 1 ? 's' : ''} converted successfully!`,
        'Your PDFs have been downloaded as a ZIP file.'
      );
      
    } catch (error) {
      console.error('Conversion error:', error);
      showError(error.message || 'An error occurred during conversion. Please try again.');
    }
  }
}

// UI State Management
function showSuccess(title, message) {
  progressContainer.style.display = "none";
  messageContainer.style.display = "block";

  messageIcon.className = "message-icon success";
  messageTitle.textContent = title;
  messageText.textContent = message;
  convertAnother.style.display = "inline-block";
}

function showError(message) {
  uploadZone.style.display = "none";
  progressContainer.style.display = "none";
  messageContainer.style.display = "block";

  messageIcon.className = "message-icon error";
  messageTitle.textContent = "Conversion Failed";
  messageText.textContent = message;
  convertAnother.style.display = "inline-block";
}

function resetUpload() {
  uploadZone.style.display = "block";
  progressContainer.style.display = "none";
  messageContainer.style.display = "none";
  fileInput.value = "";
}

// Prevent default drag and drop on the whole page
window.addEventListener(
  "dragover",
  (e) => {
    e.preventDefault();
  },
  false
);

window.addEventListener(
  "drop",
  (e) => {
    e.preventDefault();
  },
  false
);
