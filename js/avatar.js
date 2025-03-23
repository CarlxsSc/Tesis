/* avatar.js - Handle avatar image upload and processing */

// Global variables
let avatarImage = null;
let originalImageData = null;

// Initialize avatar functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM loaded, initializing avatar functionality");
    
    // Set up image upload button
    const uploadButton = document.getElementById('uploadAvatar');
    const fileInput = document.getElementById('imageUpload');
    
    if (uploadButton && fileInput) {
        console.log("Found upload elements, attaching event listeners");
        uploadButton.addEventListener('click', function() {
            fileInput.click();
        });
        fileInput.addEventListener('change', handleImageUpload);
    } else {
        console.error("Upload elements not found");
    }
});

// Handle image upload
function handleImageUpload(event) {
    console.log("handleImageUpload called");
    const file = event.target.files[0];
    if (!file) {
        console.log("No file selected");
        return;
    }
    
    // Check file type
    if (!file.type.match('image.*')) {
        alert('Por favor, selecciona una imagen válida.');
        return;
    }
    
    console.log("Processing image file:", file.name);
    document.getElementById('face-status').textContent = 'Cargando imagen...';
    
    // Create image element for processing
    const img = new Image();
    img.onload = function() {
        console.log("Image loaded successfully");
        
        // Store the image for later use
        avatarImage = img;
        
        // Display in canvas
        displayAvatarInCanvas(img);
        
        // Store original image data for 3D effects
        storeOriginalImageData(img);
        
        // Detect face
        detectFace(img).then(success => {
            if (success) {
                console.log("Face detection successful");
            } else {
                console.log("Face detection failed");
                document.getElementById('face-status').textContent = 'No se detectó ningún rostro. Intenta con otra imagen.';
            }
        }).catch(error => {
            console.error("Error in face detection:", error);
            document.getElementById('face-status').textContent = 'Error al detectar el rostro: ' + error.message;
        });
    };
    
    img.onerror = function() {
        console.error("Error loading image");
        document.getElementById('face-status').textContent = 'Error al cargar la imagen.';
    };
    
    // Load image from file
    const reader = new FileReader();
    reader.onload = function(e) {
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
}

// Display avatar in canvas
function displayAvatarInCanvas(imageElement) {
    const canvas = document.getElementById('avatarCanvas');
    const ctx = canvas.getContext('2d');
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Calculate dimensions to maintain aspect ratio
    const scale = Math.min(canvas.width / imageElement.width, canvas.height / imageElement.height);
    const x = (canvas.width - imageElement.width * scale) / 2;
    const y = (canvas.height - imageElement.height * scale) / 2;
    
    // Draw image
    ctx.drawImage(imageElement, x, y, imageElement.width * scale, imageElement.height * scale);
}

// Store original image data for 3D effects
function storeOriginalImageData(imageElement) {
    // Create temporary canvas to store original image data
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = imageElement.width;
    tempCanvas.height = imageElement.height;
    
    const tempCtx = tempCanvas.getContext('2d');
    tempCtx.drawImage(imageElement, 0, 0);
    
    // Store image data
    originalImageData = tempCtx.getImageData(0, 0, tempCanvas.width, tempCanvas.height);
}

// Detect face in the uploaded image
async function detectFace(img) {
    try {
        console.log("Starting face detection on uploaded image");
        const results = await faceapi.detectAllFaces(img, new faceapi.TinyFaceDetectorOptions());
        if (results.length > 0) {
            document.getElementById('face-status').textContent = 'Rostro detectado correctamente. ¡Listo para animar!';
            return true;
        } else {
            document.getElementById('face-status').textContent = 'No se detectó ningún rostro. Intenta con otra imagen.';
            return false;
        }
    } catch (error) {
        document.getElementById('face-status').textContent = 'Error al detectar el rostro.';
        console.error("Face detection error:", error);
        return false;
    }
}
