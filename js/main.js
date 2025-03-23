/* main.js - Main application initialization */

document.addEventListener("DOMContentLoaded", async () => {
    console.log("Initializing application...");
    
    // Check if browser supports required APIs
    if (!window.SpeechSynthesisUtterance || !window.speechSynthesis) {
        alert("Tu navegador no soporta la API de síntesis de voz necesaria para esta aplicación.");
        document.getElementById("speakText").disabled = true;
    }
    
    // Wait for face-api.js to be fully loaded
    if (typeof faceapi === 'undefined') {
        console.log("Waiting for face-api.js to load...");
        await new Promise(resolve => {
            const checkFaceApi = setInterval(() => {
                if (typeof faceapi !== 'undefined') {
                    clearInterval(checkFaceApi);
                    resolve();
                }
            }, 100);
            
            // Timeout after 10 seconds
            setTimeout(() => {
                clearInterval(checkFaceApi);
                console.error("Timeout waiting for face-api.js to load");
                resolve();
            }, 10000);
        });
    }
    
    // Initialize face detection models
    try {
        console.log("Starting face detection initialization...");
        const modelsLoaded = await initFaceDetection();
        if (modelsLoaded) {
            console.log("Face detection models loaded successfully");
        } else {
            console.error("Failed to load face detection models");
        }
    } catch (error) {
        console.error("Error initializing face detection:", error);
    }
    
    // Set up responsive UI
    setupResponsiveUI();
    
    // Add debug button for development
    addDebugHelpers();
});

// Set up responsive UI elements
function setupResponsiveUI() {
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Mobile navigation menu toggle
    const navToggle = document.querySelector('.nav__menu');
    const navMenu = document.querySelector('.nav__link');
    const navClose = document.querySelector('.nav__close');
    
    if (navToggle && navMenu && navClose) {
        navToggle.addEventListener('click', () => {
            navMenu.classList.add('nav__link--show');
        });
        
        navClose.addEventListener('click', () => {
            navMenu.classList.remove('nav__link--show');
        });
    }
}

// Add debug helpers for development
function addDebugHelpers() {
    // Only add in development mode
    if (location.hostname === 'localhost' || location.hostname === '127.0.0.1') {
        const debugButton = document.createElement('button');
        debugButton.textContent = 'Debug Face Detection';
        debugButton.style.position = 'fixed';
        debugButton.style.bottom = '10px';
        debugButton.style.right = '10px';
        debugButton.style.zIndex = '9999';
        debugButton.style.padding = '5px 10px';
        debugButton.style.backgroundColor = '#ff5722';
        debugButton.style.color = 'white';
        debugButton.style.border = 'none';
        debugButton.style.borderRadius = '4px';
        debugButton.style.cursor = 'pointer';
        
        debugButton.addEventListener('click', async () => {
            console.log('Debug info:');
            console.log('Avatar image:', window.debugAvatarImage);
            console.log('Face data:', window.debugFaceData);
            console.log('Face API loaded:', typeof faceapi !== 'undefined');
            
            if (typeof faceapi !== 'undefined') {
                console.log('TinyFaceDetector loaded:', faceapi.nets.tinyFaceDetector.isLoaded);
                console.log('FaceLandmark68Net loaded:', faceapi.nets.faceLandmark68Net.isLoaded);
                
                if (window.debugAvatarImage && !window.debugFaceData) {
                    console.log('Attempting face detection again...');
                    try {
                        const result = await detectFace(window.debugAvatarImage);
                        console.log('Face detection result:', result);
                    } catch (error) {
                        console.error('Face detection error:', error);
                    }
                }
            }
        });
        
        document.body.appendChild(debugButton);
    }
}
