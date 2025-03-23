/* face-sync.js - Face detection and lip syncing */

// Global variables
let faceDetector = false;
let faceData = null;
let isAnimating = false;
let mouthOpenness = 0;
let eyebrowRaise = 0;
let eyeOpenness = 1.0;
let headTilt = 0;
let headTurn = 0;
let headForward = 0;
let depthEffect = 0;
let lastAnimationTime = 0;
let lastBlinkTime = 0;
let animationCanvas = null;
let animationCtx = null;
let originalImageData = null;
let expressionState = {
    surprised: false,
    thinking: false,
    emphasis: false,
    nodding: false,
    turning: false
};

// 3D transformation parameters
let transform3D = {
    rotateX: 0,  // Up/down rotation
    rotateY: 0,  // Left/right rotation
    rotateZ: 0,  // Tilt rotation
    translateZ: 0, // Forward/backward
    perspective: 1000, // Perspective depth
    scale: 1.0    // Zoom level
};

// Initialize face detection using face-api.js
async function initFaceDetection() {
    try {
        console.log("Initializing face detection models...");
        
        // Use CDN for models
        const modelUrl = 'https://justadudewhohacks.github.io/face-api.js/models';
        
        // Load tiny face detector model
        await faceapi.nets.tinyFaceDetector.loadFromUri(modelUrl);
        console.log("Tiny face detector model loaded");
        
        // Load face landmark model
        await faceapi.nets.faceLandmark68Net.loadFromUri(modelUrl);
        console.log("Face landmark model loaded");
        
        console.log("Face detection models loaded successfully");
        faceDetector = true;
        return true;
    } catch (error) {
        console.error("Error loading face detection models:", error);
        document.getElementById('face-status').textContent = 'Error cargando los modelos de detección facial. Por favor, recarga la página.';
        return false;
    }
}

// Detect face in the uploaded image
async function detectFace(imageElement) {
    if (!imageElement) {
        console.error("No image element provided for face detection");
        return false;
    }
    
    try {
        console.log("Starting face detection...");
        document.getElementById('face-status').textContent = 'Detectando rostro...';
        
        // Make sure models are loaded
        if (!faceDetector) {
            console.log("Loading face detection models...");
            const modelsLoaded = await initFaceDetection();
            if (!modelsLoaded) {
                document.getElementById('face-status').textContent = 'Error al cargar los modelos de detección facial.';
                return false;
            }
        }
        
        // Detect face with landmarks
        console.log("Running face detection on image:", imageElement.width, "x", imageElement.height);
        
        // Run face detection
        const detectionOptions = new faceapi.TinyFaceDetectorOptions({ inputSize: 320, scoreThreshold: 0.5 });
        const detections = await faceapi.detectSingleFace(imageElement, detectionOptions).withFaceLandmarks();
        
        if (!detections) {
            console.log("No face detected in the image");
            document.getElementById('face-status').textContent = 'No se detectó ningún rostro. Intenta con otra imagen.';
            return false;
        }
        
        console.log("Face detected:", detections);
        document.getElementById('face-status').textContent = 'Rostro detectado correctamente. ¡Listo para animar!';
        
        // Store face data for animation
        const box = detections.detection.box;
        const landmarks = detections.landmarks;
        
        // Store face dimensions and position
        faceData = {
            faceWidth: box.width,
            faceHeight: box.height,
            faceX: box.x,
            faceY: box.y,
            landmarks: landmarks,
            mouth: landmarks.getMouth(),
            leftEye: landmarks.getLeftEye(),
            rightEye: landmarks.getRightEye(),
            nose: landmarks.getNose(),
            jawOutline: landmarks.getJawOutline()
        };
        
        // Create depth map for 3D effect
        faceData.depthMap = createDepthMap(faceData);
        
        // Create animation canvas
        createAnimationCanvas(imageElement);
        
        // Start subtle idle animation
        startIdleAnimation();
        
        return true;
    } catch (error) {
        console.error("Error detecting face:", error);
        document.getElementById('face-status').textContent = 'Error al detectar el rostro: ' + error.message;
        return false;
    }
}

// Start subtle idle animation when face is detected
function startIdleAnimation() {
    isAnimating = true;
    
    // Set initial 3D transform values for idle state
    transform3D = {
        rotateX: 0,
        rotateY: 0,
        rotateZ: 0,
        translateZ: 0,
        perspective: 1000,
        scale: 1.0
    };
    
    // Start the animation loop
    requestAnimationFrame(updateIdleAnimation);
}

// Update idle animation
function updateIdleAnimation(timestamp) {
    if (!isAnimating) return;
    
    // Only update every 50ms for performance
    if (!lastAnimationTime || timestamp - lastAnimationTime > 50) {
        lastAnimationTime = timestamp;
        
        // Update 3D transforms for subtle movement
        transform3D.rotateX = Math.sin(timestamp / 3000) * 0.02;
        transform3D.rotateY = Math.sin(timestamp / 4000) * 0.02;
        transform3D.rotateZ = Math.sin(timestamp / 5000) * 0.01;
        transform3D.translateZ = Math.sin(timestamp / 2000) * 3;
        
        // Occasional eye blink
        if (Math.random() < 0.005) {
            animateEyeBlink();
        }
        
        // Render with 3D effect
        renderAvatarWith3DEffect();
    }
    
    // Continue animation loop if still animating
    if (isAnimating) {
        requestAnimationFrame(updateIdleAnimation);
    }
}

// Visualize the detected face landmarks
function visualizeFaceDetection(imageElement, detections) {
    // Create overlay canvas for visualization if it doesn't exist
    if (!document.getElementById('faceOverlayCanvas')) {
        const container = document.getElementById('avatar-container');
        const mainCanvas = document.getElementById('avatarCanvas');
        
        const overlayCanvas = document.createElement('canvas');
        overlayCanvas.id = 'faceOverlayCanvas';
        overlayCanvas.width = mainCanvas.width;
        overlayCanvas.height = mainCanvas.height;
        overlayCanvas.style.position = 'absolute';
        overlayCanvas.style.top = mainCanvas.offsetTop + 'px';
        overlayCanvas.style.left = mainCanvas.offsetLeft + 'px';
        overlayCanvas.style.pointerEvents = 'none'; // Allow clicks to pass through
        
        // Position the container relatively for absolute positioning of overlay
        container.style.position = 'relative';
        
        // Insert overlay canvas after the main canvas
        mainCanvas.insertAdjacentElement('afterend', overlayCanvas);
        
        // Store reference to animation canvas
        animationCanvas = overlayCanvas;
        animationCtx = overlayCanvas.getContext('2d');
    }
    
    // Clear the overlay canvas
    animationCtx.clearRect(0, 0, animationCanvas.width, animationCanvas.height);
    
    // Calculate scale factor between detection and canvas
    const scale = {
        x: animationCanvas.width / (imageElement.naturalWidth || imageElement.width),
        y: animationCanvas.height / (imageElement.naturalHeight || imageElement.height)
    };
    
    // Draw face landmarks for visualization
    animationCtx.strokeStyle = '#00ff00';
    animationCtx.lineWidth = 2;
    
    // Draw face box
    const box = detections.detection.box;
    animationCtx.strokeRect(
        box.x * scale.x, 
        box.y * scale.y, 
        box.width * scale.x, 
        box.height * scale.y
    );
    
    // Draw mouth outline
    const mouth = detections.landmarks.getMouth();
    animationCtx.beginPath();
    animationCtx.moveTo(mouth[0].x * scale.x, mouth[0].y * scale.y);
    for (let i = 1; i < mouth.length; i++) {
        animationCtx.lineTo(mouth[i].x * scale.x, mouth[i].y * scale.y);
    }
    animationCtx.closePath();
    animationCtx.stroke();
    
    // Add a label
    animationCtx.fillStyle = 'rgba(0, 255, 0, 0.7)';
    animationCtx.font = '14px Arial';
    animationCtx.fillText('Rostro Detectado', box.x * scale.x, (box.y * scale.y) - 5);
    
    // Fade out the visualization after 2 seconds
    setTimeout(() => {
        fadeOutVisualization();
    }, 2000);
}

// Fade out the face detection visualization
function fadeOutVisualization() {
    if (!animationCanvas || !animationCtx) return;
    
    let opacity = 1.0;
    const fadeInterval = setInterval(() => {
        opacity -= 0.05;
        if (opacity <= 0) {
            clearInterval(fadeInterval);
            animationCtx.clearRect(0, 0, animationCanvas.width, animationCanvas.height);
            return;
        }
        
        // Redraw with reduced opacity
        animationCtx.clearRect(0, 0, animationCanvas.width, animationCanvas.height);
        animationCtx.globalAlpha = opacity;
        // We don't redraw anything here as we're just fading out what's already there
    }, 50);
}

// Create animation canvas for overlay effects
function createAnimationCanvas(imageElement) {
    // Get the main canvas and its container
    const mainCanvas = document.getElementById('avatarCanvas');
    const container = mainCanvas.parentElement;
    
    // Remove any existing animation canvas
    const existingCanvas = document.getElementById('animationCanvas');
    if (existingCanvas) {
        container.removeChild(existingCanvas);
    }
    
    // Create a new canvas for animations
    animationCanvas = document.createElement('canvas');
    animationCanvas.id = 'animationCanvas';
    animationCanvas.width = mainCanvas.width;
    animationCanvas.height = mainCanvas.height;
    animationCanvas.style.position = 'absolute';
    animationCanvas.style.top = '0';
    animationCanvas.style.left = '0';
    animationCanvas.style.pointerEvents = 'none'; // Allow clicks to pass through
    
    // Add the canvas to the container
    container.appendChild(animationCanvas);
    
    // Get the animation context
    animationCtx = animationCanvas.getContext('2d');
    
    console.log("Animation canvas created with dimensions:", animationCanvas.width, "x", animationCanvas.height);
    
    return animationCanvas;
}

// Animate mouth based on speech
function animateMouth(utterance) {
    if (!faceData || !animationCanvas) {
        console.error("Face data or animation canvas not available");
        return;
    }
    
    // Set animation status
    const statusElement = document.getElementById('animation-status');
    if (statusElement) {
        statusElement.textContent = 'Hablando...';
        statusElement.style.display = 'block';
    }
    
    // Start animation loop
    isAnimating = true;
    
    // Reset animation values
    mouthOpenness = 0.1;
    eyebrowRaise = 0;
    eyeOpenness = 1.0;
    
    // Reset 3D transform values
    transform3D = {
        rotateX: 0,
        rotateY: 0,
        rotateZ: 0,
        translateZ: 0,
        perspective: 1000,
        scale: 1.0
    };
    
    // Reset expression states
    Object.keys(expressionState).forEach(key => {
        expressionState[key] = false;
    });
    
    // Start animation frame loop
    requestAnimationFrame(updateMouthAnimation);
    
    // Set up speech events to control animation
    utterance.onboundary = function(event) {
        // Syllable boundary event - update mouth openness
        if (event.name === 'word') {
            // Emphasize word beginnings
            mouthOpenness = 0.5 + Math.random() * 0.5;
            
            // Randomly add expressions for more natural speech
            if (Math.random() > 0.8) {
                // 20% chance of eyebrow raise on new words for emphasis
                expressionState.emphasis = true;
                eyebrowRaise = 0.3 + Math.random() * 0.2;
                
                // Occasionally add a head movement
                if (Math.random() > 0.7) {
                    if (Math.random() > 0.5) {
                        expressionState.nodding = true;
                        setTimeout(() => {
                            expressionState.nodding = false;
                        }, 500 + Math.random() * 300);
                    } else {
                        expressionState.turning = true;
                        setTimeout(() => {
                            expressionState.turning = false;
                        }, 500 + Math.random() * 300);
                    }
                }
            } else {
                expressionState.emphasis = false;
            }
        } else {
            // Regular syllable boundary
            mouthOpenness = 0.2 + Math.random() * 0.3;
        }
        
        // Analyze text for expression cues
        analyzeTextForExpressions(utterance.text);
    };
    
    utterance.onend = function() {
        // End animation after a short delay
        setTimeout(() => {
            isAnimating = false;
            
            // Reset animation status
            if (statusElement) {
                statusElement.textContent = '';
                statusElement.style.display = 'none';
            }
        }, 500);
    };
}

// Analyze text for expression cues
function analyzeTextForExpressions(text) {
    // Simple text analysis for expressions
    const lowerText = text.toLowerCase();
    
    // Check for question marks - raise eyebrows
    if (lowerText.includes('?')) {
        expressionState.surprised = true;
        eyebrowRaise = 0.7;
        setTimeout(() => {
            expressionState.surprised = false;
        }, 1000);
    }
    
    // Check for exclamation marks - emphasis
    if (lowerText.includes('!')) {
        expressionState.emphasis = true;
        eyebrowRaise = 0.5;
        setTimeout(() => {
            expressionState.emphasis = false;
        }, 800);
    }
    
    // Check for thinking words
    const thinkingWords = ['hmm', 'quizás', 'tal vez', 'pienso', 'creo'];
    if (thinkingWords.some(word => lowerText.includes(word))) {
        expressionState.thinking = true;
        setTimeout(() => {
            expressionState.thinking = false;
        }, 1500);
    }
}

// Animation loop for mouth movement
function updateMouthAnimation(timestamp) {
    if (!isAnimating || !animationCtx || !faceData) return;
    
    // Limit updates to 30fps for performance
    if (timestamp - lastAnimationTime > 33) {
        lastAnimationTime = timestamp;
        
        // Clear previous frame
        animationCtx.clearRect(0, 0, animationCanvas.width, animationCanvas.height);
        
        // Calculate scale for drawing
        const drawScale = {
            x: animationCanvas.width / (faceData.faceWidth * 3),
            y: animationCanvas.height / (faceData.faceHeight * 3)
        };
        
        // Get facial feature points
        const mouthPoints = faceData.mouth;
        const leftEyePoints = faceData.leftEye;
        const rightEyePoints = faceData.rightEye;
        const leftEyebrowPoints = faceData.landmarks.getLeftEyeBrow();
        const rightEyebrowPoints = faceData.landmarks.getRightEyeBrow();
        
        // Handle natural eye blinking
        if (timestamp - lastBlinkTime > 5000 + Math.random() * 3000) {
            // Time for a blink
            animateEyeBlink();
            lastBlinkTime = timestamp;
        }
        
        // Update eyebrow position based on speech emphasis
        updateEyebrowExpression();
        
        // Update head tilt/turn for more natural movement
        updateHeadMovement();
        
        // Apply 3D transformations
        animationCtx.save();
        
        // Set the center point for transformations
        const centerX = animationCanvas.width / 2;
        const centerY = animationCanvas.height / 2;
        
        // Apply perspective transformation
        animationCtx.translate(centerX, centerY);
        
        // Apply rotation based on head movement
        const rotateX = transform3D.rotateX;
        const rotateY = transform3D.rotateY;
        const rotateZ = transform3D.rotateZ;
        
        // Apply a simplified 3D transformation matrix
        const transformScale = 1 + (transform3D.translateZ / transform3D.perspective) * 0.1;
        
        // Apply transformations to the animation canvas
        animationCtx.transform(
            transformScale * Math.cos(rotateY) * Math.cos(rotateZ),
            transformScale * (Math.sin(rotateX) * Math.sin(rotateY) * Math.cos(rotateZ) + Math.cos(rotateX) * Math.sin(rotateZ)),
            -transformScale * Math.sin(rotateY),
            transformScale * (-Math.sin(rotateX) * Math.sin(rotateZ) + Math.cos(rotateX) * Math.sin(rotateY) * Math.cos(rotateZ)),
            transformScale * Math.cos(rotateX) * Math.cos(rotateZ),
            0
        );
        
        // Translate back
        animationCtx.translate(-centerX, -centerY);
        
        // Draw facial features with current animation values
        drawAnimatedMouth(mouthPoints, drawScale, mouthOpenness);
        drawAnimatedEyes(leftEyePoints, rightEyePoints, drawScale, eyeOpenness);
        drawAnimatedEyebrows(leftEyebrowPoints, rightEyebrowPoints, drawScale, eyebrowRaise);
        
        // Restore the context
        animationCtx.restore();
        
        // Apply lighting effects
        applyLightingEffects();
        
        // Gradually return to neutral expression
        mouthOpenness = Math.max(0.1, mouthOpenness * 0.95);
        eyebrowRaise *= 0.9;
        eyeOpenness = Math.min(1.0, eyeOpenness + 0.1);
    }
    
    requestAnimationFrame(updateMouthAnimation);
}

// Animate eye blink
function animateEyeBlink() {
    // Quick blink animation
    eyeOpenness = 0.1;
    
    // Schedule eye opening
    setTimeout(() => {
        eyeOpenness = 0.5;
        setTimeout(() => {
            eyeOpenness = 1.0;
        }, 50);
    }, 100);
}

// Update eyebrow expression based on speech context
function updateEyebrowExpression() {
    if (expressionState.surprised) {
        eyebrowRaise = 0.8;
    } else if (expressionState.thinking) {
        // One eyebrow up, one normal
        eyebrowRaise = 0.5;
    } else if (expressionState.emphasis && Math.random() > 0.7) {
        // Occasional eyebrow raise for emphasis
        eyebrowRaise = 0.3 + Math.random() * 0.3;
    }
}

// Update head movement for natural effect
function updateHeadMovement() {
    if (expressionState.nodding) {
        // Nodding animation
        transform3D.rotateX = Math.sin(Date.now() / 200) * 0.1;
        headTilt = Math.sin(Date.now() / 200) * 0.05;
    } else if (expressionState.turning) {
        // Head turning animation
        transform3D.rotateY = Math.sin(Date.now() / 300) * 0.15;
        headTurn = Math.sin(Date.now() / 300) * 0.05;
    } else {
        // Subtle random movement for realism
        transform3D.rotateX = Math.sin(Date.now() / 2000) * 0.03;
        transform3D.rotateY = Math.sin(Date.now() / 3000) * 0.03;
        transform3D.rotateZ = Math.sin(Date.now() / 4000) * 0.01;
        
        // Subtle breathing effect
        transform3D.translateZ = Math.sin(Date.now() / 1500) * 5;
        
        // Update traditional variables for compatibility
        headTilt = transform3D.rotateZ;
        headTurn = transform3D.rotateY;
        headForward = transform3D.translateZ;
    }
}

// Apply 3D transformations to canvas
function apply3DTransforms(ctx, width, height) {
    // Save the current state
    ctx.save();
    
    // Translate to center for transformations
    ctx.translate(width / 2, height / 2);
    
    // Apply perspective and 3D transformations
    const perspective = transform3D.perspective;
    const scale = 1 + (transform3D.translateZ / perspective) * 0.1;
    
    // Apply 3D rotation matrix (simplified)
    ctx.transform(
        scale * Math.cos(transform3D.rotateY) * Math.cos(transform3D.rotateZ),
        scale * (Math.sin(transform3D.rotateX) * Math.sin(transform3D.rotateY) * Math.cos(transform3D.rotateZ) + Math.cos(transform3D.rotateX) * Math.sin(transform3D.rotateZ)),
        -scale * Math.sin(transform3D.rotateY),
        scale * (-Math.sin(transform3D.rotateX) * Math.sin(transform3D.rotateZ) + Math.cos(transform3D.rotateX) * Math.sin(transform3D.rotateY) * Math.cos(transform3D.rotateZ)),
        scale * Math.cos(transform3D.rotateX) * Math.cos(transform3D.rotateZ),
        0
    );
    
    // Translate back
    ctx.translate(-width / 2, -height / 2);
}

// Apply lighting effects for realism
function applyLightingEffects() {
    if (!animationCtx) return;
    
    // Create a subtle lighting gradient
    const gradient = animationCtx.createRadialGradient(
        animationCanvas.width / 2, 
        animationCanvas.height / 2, 
        10,
        animationCanvas.width / 2 + Math.sin(Date.now() / 2000) * 50, 
        animationCanvas.height / 2 + Math.cos(Date.now() / 2000) * 30, 
        animationCanvas.width * 0.8
    );
    
    // Add color stops
    gradient.addColorStop(0, 'rgba(255, 255, 255, 0.1)');
    gradient.addColorStop(0.5, 'rgba(255, 255, 255, 0.05)');
    gradient.addColorStop(1, 'rgba(0, 0, 0, 0.15)');
    
    // Apply the gradient overlay
    animationCtx.globalCompositeOperation = 'overlay';
    animationCtx.fillStyle = gradient;
    animationCtx.fillRect(0, 0, animationCanvas.width, animationCanvas.height);
    
    // Reset composite operation
    animationCtx.globalCompositeOperation = 'source-over';
}

// Draw animated eyes
function drawAnimatedEyes(leftEyePoints, rightEyePoints, scale, openness) {
    if (!animationCtx) return;
    
    // Center the eyes in the canvas
    const centerX = animationCanvas.width / 2;
    const centerY = animationCanvas.height / 2;
    
    // Calculate eye centers
    let leftEyeCenterX = 0, leftEyeCenterY = 0;
    let rightEyeCenterX = 0, rightEyeCenterY = 0;
    
    for (const point of leftEyePoints) {
        leftEyeCenterX += point.x;
        leftEyeCenterY += point.y;
    }
    
    for (const point of rightEyePoints) {
        rightEyeCenterX += point.x;
        rightEyeCenterY += point.y;
    }
    
    leftEyeCenterX /= leftEyePoints.length;
    leftEyeCenterY /= leftEyePoints.length;
    rightEyeCenterX /= rightEyePoints.length;
    rightEyeCenterY /= rightEyePoints.length;
    
    // Calculate mouth center for reference
    let mouthCenterX = 0, mouthCenterY = 0;
    for (const point of faceData.mouth) {
        mouthCenterX += point.x;
        mouthCenterY += point.y;
    }
    mouthCenterX /= faceData.mouth.length;
    mouthCenterY /= faceData.mouth.length;
    
    // Draw eyes with openness factor
    animationCtx.save();
    
    // Apply head tilt/turn transformations
    animationCtx.translate(centerX, centerY);
    animationCtx.rotate(headTilt);
    animationCtx.scale(1 + headTurn, 1);
    animationCtx.translate(-centerX, -centerY);
    
    // Set styles for eyes
    animationCtx.fillStyle = 'rgba(255, 255, 255, 0.9)';
    animationCtx.strokeStyle = 'rgba(0, 0, 0, 0.8)';
    animationCtx.lineWidth = 1;
    
    // Calculate eye dimensions
    const leftEyeWidth = Math.max(...leftEyePoints.map(p => p.x)) - Math.min(...leftEyePoints.map(p => p.x));
    const leftEyeHeight = Math.max(...leftEyePoints.map(p => p.y)) - Math.min(...leftEyePoints.map(p => p.y));
    const rightEyeWidth = Math.max(...rightEyePoints.map(p => p.x)) - Math.min(...rightEyePoints.map(p => p.x));
    const rightEyeHeight = Math.max(...rightEyePoints.map(p => p.y)) - Math.min(...rightEyePoints.map(p => p.y));
    
    // Draw left eye
    animationCtx.beginPath();
    animationCtx.ellipse(
        centerX + (leftEyeCenterX - mouthCenterX) * scale.x * 2,
        centerY + (leftEyeCenterY - mouthCenterY) * scale.y * 2,
        leftEyeWidth * scale.x,
        leftEyeHeight * scale.y * openness,
        0, 0, Math.PI * 2
    );
    animationCtx.fill();
    animationCtx.stroke();
    
    // Draw right eye
    animationCtx.beginPath();
    animationCtx.ellipse(
        centerX + (rightEyeCenterX - mouthCenterX) * scale.x * 2,
        centerY + (rightEyeCenterY - mouthCenterY) * scale.y * 2,
        rightEyeWidth * scale.x,
        rightEyeHeight * scale.y * openness,
        0, 0, Math.PI * 2
    );
    animationCtx.fill();
    animationCtx.stroke();
    
    // Draw pupils
    animationCtx.fillStyle = 'rgba(0, 0, 0, 0.9)';
    
    // Left pupil
    animationCtx.beginPath();
    animationCtx.ellipse(
        centerX + (leftEyeCenterX - mouthCenterX) * scale.x * 2,
        centerY + (leftEyeCenterY - mouthCenterY) * scale.y * 2,
        leftEyeWidth * scale.x * 0.3,
        leftEyeHeight * scale.y * openness * 0.3,
        0, 0, Math.PI * 2
    );
    animationCtx.fill();
    
    // Right pupil
    animationCtx.beginPath();
    animationCtx.ellipse(
        centerX + (rightEyeCenterX - mouthCenterX) * scale.x * 2,
        centerY + (rightEyeCenterY - mouthCenterY) * scale.y * 2,
        rightEyeWidth * scale.x * 0.3,
        rightEyeHeight * scale.y * openness * 0.3,
        0, 0, Math.PI * 2
    );
    animationCtx.fill();
    
    animationCtx.restore();
}

// Draw animated eyebrows
function drawAnimatedEyebrows(leftEyebrowPoints, rightEyebrowPoints, scale, raiseAmount) {
    if (!animationCtx) return;
    
    // Center the eyebrows in the canvas
    const centerX = animationCanvas.width / 2;
    const centerY = animationCanvas.height / 2;
    
    // Calculate mouth center for reference
    let mouthCenterX = 0;
    let mouthCenterY = 0;
    
    for (const point of faceData.mouth) {
        mouthCenterX += point.x;
        mouthCenterY += point.y;
    }
    
    mouthCenterX /= faceData.mouth.length;
    mouthCenterY /= faceData.mouth.length;
    
    // Draw eyebrows
    animationCtx.save();
    
    // Apply head tilt/turn transformations
    animationCtx.translate(centerX, centerY);
    animationCtx.rotate(headTilt);
    animationCtx.scale(1 + headTurn, 1);
    animationCtx.translate(-centerX, -centerY);
    
    // Set styles for eyebrows
    animationCtx.strokeStyle = 'rgba(0, 0, 0, 0.8)';
    animationCtx.lineWidth = 3;
    
    // Draw left eyebrow
    animationCtx.beginPath();
    animationCtx.moveTo(
        centerX + (leftEyebrowPoints[0].x - mouthCenterX) * scale.x * 2,
        centerY + (leftEyebrowPoints[0].y - mouthCenterY - raiseAmount * 10) * scale.y * 2
    );
    
    for (let i = 1; i < leftEyebrowPoints.length; i++) {
        // Apply more raise to the outer points for expressive eyebrows
        const pointRaise = raiseAmount * (i < leftEyebrowPoints.length / 2 ? 5 : 15);
        
        animationCtx.lineTo(
            centerX + (leftEyebrowPoints[i].x - mouthCenterX) * scale.x * 2,
            centerY + (leftEyebrowPoints[i].y - mouthCenterY - pointRaise) * scale.y * 2
        );
    }
    animationCtx.stroke();
    
    // Draw right eyebrow
    animationCtx.beginPath();
    animationCtx.moveTo(
        centerX + (rightEyebrowPoints[0].x - mouthCenterX) * scale.x * 2,
        centerY + (rightEyebrowPoints[0].y - mouthCenterY - raiseAmount * 15) * scale.y * 2
    );
    
    for (let i = 1; i < rightEyebrowPoints.length; i++) {
        // Apply more raise to the outer points for expressive eyebrows
        const pointRaise = raiseAmount * (i > rightEyebrowPoints.length / 2 ? 5 : 15);
        
        animationCtx.lineTo(
            centerX + (rightEyebrowPoints[i].x - mouthCenterX) * scale.x * 2,
            centerY + (rightEyebrowPoints[i].y - mouthCenterY - pointRaise) * scale.y * 2
        );
    }
    animationCtx.stroke();
    
    animationCtx.restore();
}

// Draw the animated mouth
function drawAnimatedMouth(mouthPoints, scale, openness) {
    if (!animationCtx) return;
    
    // Center the mouth in the canvas
    const centerX = animationCanvas.width / 2;
    const centerY = animationCanvas.height / 2;
    
    // Calculate mouth center
    let mouthCenterX = 0;
    let mouthCenterY = 0;
    
    for (const point of mouthPoints) {
        mouthCenterX += point.x;
        mouthCenterY += point.y;
    }
    
    mouthCenterX /= mouthPoints.length;
    mouthCenterY /= mouthPoints.length;
    
    // Draw mouth with enhanced visibility
    animationCtx.save();
    
    // Make the animation more visible
    const scaleFactor = 2.0; // Increase size for visibility
    scale.x *= scaleFactor;
    scale.y *= scaleFactor;
    
    // Set styles for mouth
    animationCtx.fillStyle = 'rgba(255, 0, 0, 0.7)'; // Red with transparency
    animationCtx.strokeStyle = 'rgba(0, 0, 0, 0.8)'; // Black outline
    animationCtx.lineWidth = 2;
    
    // Upper lip points
    const upperLipCenter = mouthPoints[14]; // Upper lip center
    const lowerLipCenter = mouthPoints[18]; // Lower lip center
    
    // Draw mouth
    animationCtx.beginPath();
    
    // Start from the left corner of the mouth
    animationCtx.moveTo(
        centerX + (mouthPoints[0].x - mouthCenterX) * scale.x,
        centerY + (mouthPoints[0].y - mouthCenterY) * scale.y
    );
    
    // Draw upper lip
    for (let i = 1; i < 7; i++) {
        animationCtx.lineTo(
            centerX + (mouthPoints[i].x - mouthCenterX) * scale.x,
            centerY + (mouthPoints[i].y - mouthCenterY) * scale.y
        );
    }
    
    // Draw right side
    for (let i = 7; i < 12; i++) {
        animationCtx.lineTo(
            centerX + (mouthPoints[i].x - mouthCenterX) * scale.x,
            centerY + (mouthPoints[i].y - mouthCenterY) * scale.y + (openness * 20) // Add openness effect
        );
    }
    
    // Draw lower lip with openness
    for (let i = 12; i < 20; i++) {
        let point = mouthPoints[i];
        // Adjust lower lip points based on openness
        let adjustedY = point.y + (openness * 15 * Math.sin((i - 12) / 8 * Math.PI));
        animationCtx.lineTo(
            centerX + (point.x - mouthCenterX) * scale.x,
            centerY + (adjustedY - mouthCenterY) * scale.y
        );
    }
    
    animationCtx.closePath();
    animationCtx.fill();
    animationCtx.stroke();
    
    // Add teeth for more realistic effect when mouth is open
    if (openness > 0.3) {
        animationCtx.fillStyle = 'rgba(255, 255, 255, 0.9)';
        animationCtx.beginPath();
        
        // Upper teeth
        animationCtx.moveTo(
            centerX + (mouthPoints[0].x - mouthCenterX) * scale.x + 2,
            centerY + (mouthPoints[0].y - mouthCenterY) * scale.y + 2
        );
        
        for (let i = 1; i < 7; i++) {
            animationCtx.lineTo(
                centerX + (mouthPoints[i].x - mouthCenterX) * scale.x,
                centerY + (mouthPoints[i].y - mouthCenterY) * scale.y + 2
            );
        }
        
        // Close the upper teeth shape
        animationCtx.lineTo(
            centerX + (mouthPoints[6].x - mouthCenterX) * scale.x,
            centerY + (mouthPoints[6].y - mouthCenterY) * scale.y + (openness * 10)
        );
        
        animationCtx.lineTo(
            centerX + (mouthPoints[0].x - mouthCenterX) * scale.x,
            centerY + (mouthPoints[0].y - mouthCenterY) * scale.y + (openness * 10)
        );
        
        animationCtx.closePath();
        animationCtx.fill();
    }
    
    // Add a tongue when mouth is very open
    if (openness > 0.5) {
        animationCtx.fillStyle = 'rgba(255, 150, 150, 0.8)';
        animationCtx.beginPath();
        
        const tongueWidth = (mouthPoints[6].x - mouthPoints[0].x) * 0.7;
        const tongueHeight = openness * 10;
        
        animationCtx.ellipse(
            centerX,
            centerY + (lowerLipCenter.y - mouthCenterY) * scale.y - 5,
            tongueWidth * scale.x / 2,
            tongueHeight,
            0, 0, Math.PI, false
        );
        
        animationCtx.fill();
    }
    
    animationCtx.restore();
}

// Create a depth map for 3D effect
function createDepthMap(faceData) {
    if (!faceData || !faceData.landmarks) return null;
    
    const depthMap = {};
    const landmarks = faceData.landmarks;
    
    // Get face parts
    const jawOutline = landmarks.getJawOutline();
    const nose = landmarks.getNose();
    const mouth = landmarks.getMouth();
    const leftEye = landmarks.getLeftEye();
    const rightEye = landmarks.getRightEye();
    const leftEyeBrow = landmarks.getLeftEyeBrow();
    const rightEyeBrow = landmarks.getRightEyeBrow();
    
    // Assign depth values to different facial features
    // Higher values = closer to viewer (more protruding)
    depthMap.jawline = 0.2;  // Base depth
    depthMap.cheeks = 0.3;
    depthMap.nose = 0.8;     // Nose protrudes the most
    depthMap.noseTip = 1.0;  // Tip of nose
    depthMap.eyes = 0.4;
    depthMap.eyebrows = 0.5;
    depthMap.lips = 0.6;
    depthMap.chin = 0.25;
    depthMap.forehead = 0.2;
    
    console.log("Depth map created for 3D effect");
    return depthMap;
}

// Apply shader-like effects for enhanced 3D appearance
function applyShaderEffects(ctx, width, height) {
    if (!ctx || !faceData || !faceData.depthMap) return;
    
    // Create a temporary canvas for shader effects
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = width;
    tempCanvas.height = height;
    const tempCtx = tempCanvas.getContext('2d');
    
    // Copy the current canvas to the temp canvas
    tempCtx.drawImage(ctx.canvas, 0, 0);
    
    // Apply a subtle blur for depth of field effect
    ctx.filter = 'blur(1px)';
    ctx.drawImage(tempCanvas, 0, 0);
    ctx.filter = 'none';
    
    // Apply chromatic aberration effect based on head rotation
    const aberrationStrength = Math.abs(transform3D.rotateY) * 2;
    
    // Red channel shift
    ctx.globalCompositeOperation = 'screen';
    ctx.fillStyle = 'rgba(255, 0, 0, 0.03)';
    ctx.globalAlpha = 0.3;
    ctx.drawImage(tempCanvas, aberrationStrength, 0);
    
    // Blue channel shift
    ctx.fillStyle = 'rgba(0, 0, 255, 0.03)';
    ctx.drawImage(tempCanvas, -aberrationStrength, 0);
    
    // Reset composite operation and alpha
    ctx.globalCompositeOperation = 'source-over';
    ctx.globalAlpha = 1.0;
    
    // Add subtle vignette effect
    const gradient = ctx.createRadialGradient(
        width / 2, height / 2, width * 0.3,
        width / 2, height / 2, width * 0.7
    );
    
    gradient.addColorStop(0, 'rgba(0, 0, 0, 0)');
    gradient.addColorStop(1, 'rgba(0, 0, 0, 0.3)');
    
    ctx.globalCompositeOperation = 'multiply';
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);
    
    // Reset composite operation
    ctx.globalCompositeOperation = 'source-over';
}

// Render the avatar with 3D depth effect
function renderAvatarWith3DEffect() {
    if (!faceData || !animationCanvas) return;
    
    // Get the main canvas and its context
    const mainCanvas = document.getElementById('avatarCanvas');
    if (!mainCanvas) return;
    
    const ctx = mainCanvas.getContext('2d');
    
    // Clear the canvas
    ctx.clearRect(0, 0, mainCanvas.width, mainCanvas.height);
    
    // Create a depth map if we don't have one yet
    if (!faceData.depthMap) {
        faceData.depthMap = createDepthMap(faceData);
    }
    
    // First, redraw the original avatar image
    if (originalImageData) {
        ctx.putImageData(originalImageData, 0, 0);
    }
    
    // Then apply 3D transformations to the animation canvas
    if (animationCtx) {
        // Clear the animation canvas
        animationCtx.clearRect(0, 0, animationCanvas.width, animationCanvas.height);
        
        // Apply 3D transformations to the animation canvas
        animationCtx.save();
        
        // Set the center point for transformations
        const centerX = animationCanvas.width / 2;
        const centerY = animationCanvas.height / 2;
        
        // Apply perspective transformation
        animationCtx.translate(centerX, centerY);
        
        // Apply rotation based on head movement
        const rotateX = transform3D.rotateX;
        const rotateY = transform3D.rotateY;
        const rotateZ = transform3D.rotateZ;
        
        // Apply a simplified 3D transformation matrix
        const transformScale = 1 + (transform3D.translateZ / transform3D.perspective) * 0.1;
        
        // Apply transformations to the animation canvas
        animationCtx.transform(
            transformScale * Math.cos(rotateY) * Math.cos(rotateZ),
            transformScale * (Math.sin(rotateX) * Math.sin(rotateY) * Math.cos(rotateZ) + Math.cos(rotateX) * Math.sin(rotateZ)),
            -transformScale * Math.sin(rotateY),
            transformScale * (-Math.sin(rotateX) * Math.sin(rotateZ) + Math.cos(rotateX) * Math.sin(rotateY) * Math.cos(rotateZ)),
            transformScale * Math.cos(rotateX) * Math.cos(rotateZ),
            0
        );
        
        // Translate back
        animationCtx.translate(-centerX, -centerY);
        
        // Draw facial features on the animation canvas
        if (faceData.mouth && faceData.leftEye && faceData.rightEye) {
            // Get drawing parameters
            const drawParams = window.avatarDrawParams || {
                x: 0,
                y: 0,
                width: animationCanvas.width,
                height: animationCanvas.height
            };
            
            // Calculate scale for drawing
            const drawScale = {
                x: drawParams.width / (faceData.faceWidth * 3),
                y: drawParams.height / (faceData.faceHeight * 3)
            };
            
            // Draw facial features with current animation values
            drawAnimatedMouth(faceData.mouth, drawScale, mouthOpenness);
            drawAnimatedEyes(faceData.leftEye, faceData.rightEye, drawScale, eyeOpenness);
            
            // Draw eyebrows if available
            if (faceData.landmarks && faceData.landmarks.getLeftEyeBrow && faceData.landmarks.getRightEyeBrow) {
                const leftEyebrowPoints = faceData.landmarks.getLeftEyeBrow();
                const rightEyebrowPoints = faceData.landmarks.getRightEyeBrow();
                drawAnimatedEyebrows(leftEyebrowPoints, rightEyebrowPoints, drawScale, eyebrowRaise);
            }
        }
        
        // Apply lighting effects
        applyDynamicLighting(animationCtx, animationCanvas.width, animationCanvas.height);
        
        // Apply shader-like effects
        applyShaderEffects(animationCtx, animationCanvas.width, animationCanvas.height);
        
        // Restore the context
        animationCtx.restore();
    }
}

// Apply dynamic lighting for 3D effect
function applyDynamicLighting(ctx, width, height) {
    // Create a subtle lighting gradient that moves with head rotation
    const lightX = width / 2 + Math.sin(transform3D.rotateY * 5) * width * 0.3;
    const lightY = height / 2 + Math.sin(transform3D.rotateX * 5) * height * 0.3;
    
    const gradient = ctx.createRadialGradient(
        lightX, lightY, 10,
        width / 2, height / 2, width * 0.8
    );
    
    // Add color stops for lighting effect
    gradient.addColorStop(0, 'rgba(255, 255, 255, 0.15)');
    gradient.addColorStop(0.5, 'rgba(255, 255, 255, 0.05)');
    gradient.addColorStop(1, 'rgba(0, 0, 0, 0.2)');
    
    // Apply the gradient overlay
    ctx.globalCompositeOperation = 'overlay';
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);
    
    // Add a subtle shadow on the opposite side of the light
    const shadowGradient = ctx.createRadialGradient(
        width - lightX, height - lightY, 10,
        width / 2, height / 2, width * 0.8
    );
    
    shadowGradient.addColorStop(0, 'rgba(0, 0, 0, 0.2)');
    shadowGradient.addColorStop(0.5, 'rgba(0, 0, 0, 0.1)');
    shadowGradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
    
    ctx.fillStyle = shadowGradient;
    ctx.fillRect(0, 0, width, height);
    
    // Reset composite operation
    ctx.globalCompositeOperation = 'source-over';
}

// Update the animation loop to include 3D rendering
function updateAnimation(timestamp) {
    // Update head movement
    updateHeadMovement();
    
    // Render the avatar with 3D effect
    renderAvatarWith3DEffect();
    
    // Continue the animation loop
    if (isAnimating) {
        requestAnimationFrame(updateAnimation);
    }
}

// Start the animation with 3D effects
function startAnimation() {
    isAnimating = true;
    requestAnimationFrame(updateAnimation);
}

// Modify the animateMouth function to use our enhanced 3D effects
function animateMouth(utterance) {
    if (!faceData || !animationCanvas) {
        console.error("Face data or animation canvas not available");
        return;
    }
    
    // Set animation status
    const statusElement = document.getElementById('animation-status');
    if (statusElement) {
        statusElement.textContent = 'Hablando...';
        statusElement.style.display = 'block';
    }
    
    // Start animation loop with 3D effects
    isAnimating = true;
    startAnimation();
    
    // Reset animation values
    mouthOpenness = 0.1;
    eyebrowRaise = 0;
    eyeOpenness = 1.0;
    
    // Reset 3D transform values
    transform3D = {
        rotateX: 0,
        rotateY: 0,
        rotateZ: 0,
        translateZ: 0,
        perspective: 1000,
        scale: 1.0
    };
    
    // Reset expression states
    Object.keys(expressionState).forEach(key => {
        expressionState[key] = false;
    });
    
    // Start animation frame loop
    requestAnimationFrame(updateMouthAnimation);
    
    // Set up speech events to control animation
    utterance.onboundary = function(event) {
        // Syllable boundary event - update mouth openness
        if (event.name === 'word') {
            // Emphasize word beginnings
            mouthOpenness = 0.5 + Math.random() * 0.5;
            
            // Randomly add expressions for more natural speech
            if (Math.random() > 0.8) {
                // 20% chance of eyebrow raise on new words for emphasis
                expressionState.emphasis = true;
                eyebrowRaise = 0.3 + Math.random() * 0.2;
                
                // Occasionally add a head movement
                if (Math.random() > 0.7) {
                    if (Math.random() > 0.5) {
                        expressionState.nodding = true;
                        setTimeout(() => {
                            expressionState.nodding = false;
                        }, 500 + Math.random() * 300);
                    } else {
                        expressionState.turning = true;
                        setTimeout(() => {
                            expressionState.turning = false;
                        }, 500 + Math.random() * 300);
                    }
                }
            } else {
                expressionState.emphasis = false;
            }
        } else {
            // Regular syllable boundary
            mouthOpenness = 0.2 + Math.random() * 0.3;
        }
        
        // Analyze text for expression cues
        analyzeTextForExpressions(utterance.text);
    };
    
    utterance.onend = function() {
        // End animation after a short delay
        setTimeout(() => {
            isAnimating = false;
            
            // Reset animation status
            if (statusElement) {
                statusElement.textContent = '';
                statusElement.style.display = 'none';
            }
        }, 500);
    };
}

// Function to integrate with TTS
function speakWithLipSync(text) {
    if (!faceData) {
        alert("Por favor, sube una imagen con un rostro visible primero.");
        return false;
    }
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "es-ES";
    utterance.rate = 1;
    utterance.pitch = 1;
    utterance.volume = 1;
    utterance.onstart = function(event) {
        console.log('Speech has started');
    };
    utterance.onend = function(event) {
        console.log('Speech has ended');
    };
    utterance.onerror = function(event) {
        console.log('An error occurred while speaking');
    };
    
    // Start animation
    animateMouth(utterance);
    
    // Start speaking
    window.speechSynthesis.speak(utterance);
    return true;
}
