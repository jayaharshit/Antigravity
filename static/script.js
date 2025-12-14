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
    // Original behavior - convert each file separately
    let successCount = 0;
    let failedFiles = [];

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const progressText = document.querySelector('.progress-text');
      const progressSubtext = document.querySelector('.progress-subtext');

      progressText.textContent = `Converting ${i + 1} of ${files.length}...`;
      progressSubtext.textContent = `Processing: ${file.name}`;

      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await fetch('http://localhost:5000/upload', {
          method: 'POST',
          body: formData
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Conversion failed');
        }

        // Get the PDF blob
        const blob = await response.blob();

        // Create download link with original filename
        const originalName = file.name.substring(0, file.name.lastIndexOf('.'));
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${originalName}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        successCount++;

        // Small delay between downloads to avoid browser blocking
        if (i < files.length - 1) {
          await new Promise(resolve => setTimeout(resolve, 500));
        }

      } catch (error) {
        console.error(`Error converting ${file.name}:`, error);
        failedFiles.push({ name: file.name, error: error.message });
      }
    }

    // Show results
    if (failedFiles.length === 0) {
      showSuccess(
        `${successCount} file${successCount > 1 ? 's' : ''} converted!`,
        'All PDFs have been converted and downloaded successfully.'
      );
    } else if (successCount > 0) {
      const failedList = failedFiles.map(f => `• ${f.name}: ${f.error}`).join('\n');
      showSuccess(
        `${successCount} of ${files.length} files converted`,
        `Some files failed:\n${failedList}`
      );
    } else {
      const failedList = failedFiles.map(f => `• ${f.name}: ${f.error}`).join('\n');
      showError(`All conversions failed:\n${failedList}`);
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
