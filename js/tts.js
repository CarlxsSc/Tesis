/* tts.js - Text-to-speech functionality with voice customization options */

// Global variables
let availableVoices = [];
let selectedVoice = null;
let voiceOptions = {
    rate: 1.0,
    pitch: 1.0,
    volume: 1.0,
    language: 'es-ES'
};

// Initialize TTS
function initTTS() {
    // Check if browser supports speech synthesis
    if (!('speechSynthesis' in window)) {
        console.error("Este navegador no soporta la síntesis de voz");
        alert("Tu navegador no soporta la síntesis de voz. Por favor, intenta con Chrome, Edge o Safari.");
        return false;
    }
    
    // Load available voices
    loadVoices();
    
    // Handle voices changed event (important for some browsers)
    if (speechSynthesis.onvoiceschanged !== undefined) {
        speechSynthesis.onvoiceschanged = loadVoices;
    }
    
    // Set up event listeners
    document.getElementById('speakText').addEventListener('click', handleSpeakButtonClick);
    
    // Add voice customization controls
    createVoiceCustomizationControls();
    
    return true;
}

// Load available voices
function loadVoices() {
    availableVoices = speechSynthesis.getVoices();
    
    // Filter for Spanish voices as default
    const spanishVoices = availableVoices.filter(voice => voice.lang.includes('es'));
    
    // Select a default voice
    if (spanishVoices.length > 0) {
        selectedVoice = spanishVoices[0];
    } else if (availableVoices.length > 0) {
        selectedVoice = availableVoices[0];
    }
    
    // Update voice selector if it exists
    updateVoiceSelector();
}

// Create voice customization controls
function createVoiceCustomizationControls() {
    // Create container for voice controls
    const controlsContainer = document.createElement('div');
    controlsContainer.id = 'voice-controls';
    controlsContainer.className = 'voice-controls';
    
    // Create voice selector
    const voiceSelector = document.createElement('select');
    voiceSelector.id = 'voice-selector';
    voiceSelector.className = 'voice-selector';
    voiceSelector.setAttribute('aria-label', 'Seleccionar voz');
    
    // Create label for voice selector
    const voiceLabel = document.createElement('label');
    voiceLabel.setAttribute('for', 'voice-selector');
    voiceLabel.textContent = 'Voz:';
    
    // Create rate control
    const rateControl = createRangeControl('rate', 'Velocidad:', 0.5, 2, 0.1, voiceOptions.rate);
    
    // Create pitch control
    const pitchControl = createRangeControl('pitch', 'Tono:', 0.5, 2, 0.1, voiceOptions.pitch);
    
    // Create volume control
    const volumeControl = createRangeControl('volume', 'Volumen:', 0, 1, 0.1, voiceOptions.volume);
    
    // Add controls to container
    controlsContainer.appendChild(voiceLabel);
    controlsContainer.appendChild(voiceSelector);
    controlsContainer.appendChild(document.createElement('br'));
    controlsContainer.appendChild(rateControl);
    controlsContainer.appendChild(document.createElement('br'));
    controlsContainer.appendChild(pitchControl);
    controlsContainer.appendChild(document.createElement('br'));
    controlsContainer.appendChild(volumeControl);
    
    // Add container after text input
    const textInput = document.getElementById('textToSpeak');
    textInput.parentNode.insertBefore(controlsContainer, textInput.nextSibling);
    
    // Update voice selector
    updateVoiceSelector();
    
    // Add event listeners
    voiceSelector.addEventListener('change', function() {
        const selectedIndex = this.selectedIndex;
        if (selectedIndex >= 0 && availableVoices.length > 0) {
            selectedVoice = availableVoices[selectedIndex];
            
            // Update language based on selected voice
            voiceOptions.language = selectedVoice.lang;
            
            console.log(`Voice changed to: ${selectedVoice.name} (${selectedVoice.lang})`);
        }
    });
    
    // Add event listeners for range controls
    document.getElementById('rate-control').addEventListener('input', function() {
        voiceOptions.rate = parseFloat(this.value);
        document.getElementById('rate-value').textContent = this.value;
    });
    
    document.getElementById('pitch-control').addEventListener('input', function() {
        voiceOptions.pitch = parseFloat(this.value);
        document.getElementById('pitch-value').textContent = this.value;
    });
    
    document.getElementById('volume-control').addEventListener('input', function() {
        voiceOptions.volume = parseFloat(this.value);
        document.getElementById('volume-value').textContent = this.value;
    });
}

// Create a label element
function createLabel(text) {
    const label = document.createElement('label');
    label.textContent = text;
    return label;
}

// Create a range control with label
function createRangeControl(id, labelText, min, max, step, value) {
    const container = document.createElement('div');
    container.className = 'range-control';
    
    // Create label
    const label = document.createElement('label');
    label.setAttribute('for', id + '-control');
    label.textContent = labelText;
    
    // Create range input
    const range = document.createElement('input');
    range.type = 'range';
    range.id = id + '-control';
    range.min = min;
    range.max = max;
    range.step = step;
    range.value = value;
    range.setAttribute('aria-valuemin', min);
    range.setAttribute('aria-valuemax', max);
    range.setAttribute('aria-valuenow', value);
    range.setAttribute('aria-label', labelText.replace(':', ''));
    
    // Create value display
    const valueDisplay = document.createElement('span');
    valueDisplay.className = 'range-value';
    valueDisplay.textContent = value;
    valueDisplay.id = id + '-value';
    valueDisplay.setAttribute('aria-live', 'polite');
    
    // Add event listener to update value display
    range.addEventListener('input', function() {
        valueDisplay.textContent = this.value;
        voiceOptions[id] = parseFloat(this.value);
        range.setAttribute('aria-valuenow', this.value);
    });
    
    // Add elements to container
    container.appendChild(label);
    container.appendChild(range);
    container.appendChild(valueDisplay);
    
    return container;
}

// Update voice selector with available voices
function updateVoiceSelector() {
    const voiceSelector = document.getElementById('voice-selector');
    if (!voiceSelector) return;
    
    // Clear existing options
    voiceSelector.innerHTML = '';
    
    // Add available voices
    availableVoices.forEach((voice, index) => {
        const option = document.createElement('option');
        option.value = index;
        option.textContent = `${voice.name} (${voice.lang})`;
        
        // Set selected if this is the current voice
        if (selectedVoice && voice.name === selectedVoice.name) {
            option.selected = true;
        }
        
        voiceSelector.appendChild(option);
    });
}

// Handle speak button click
function handleSpeakButtonClick() {
    const textInput = document.getElementById('textToSpeak');
    const text = textInput.value.trim();
    
    if (!text) {
        alert("Por favor, escribe algo para convertir a voz");
        return;
    }
    
    // Check if text is empty
    if (!textInput.value.trim()) {
        alert("Por favor, escribe un texto para hablar.");
        return;
    }
    
    // Check if face is detected
    if (!window.faceData) {
        // Try to detect face if image is uploaded but face not detected
        const avatarImage = window.debugAvatarImage;
        if (avatarImage) {
            const statusElement = document.getElementById("animation-status");
            statusElement.textContent = "Detectando rostro...";
            detectFace(avatarImage).then(faceDetected => {
                if (faceDetected) {
                    statusElement.textContent = "Rostro detectado. Iniciando animación...";
                    setTimeout(() => speak(text), 500);
                } else {
                    alert("No se pudo detectar un rostro en la imagen. Por favor, sube una imagen con un rostro visible.");
                    statusElement.textContent = "";
                }
            });
        } else {
            alert("Por favor, sube una imagen con un rostro visible primero.");
        }
        return;
    }
    
    // If we have face data, proceed with speech
    speak(text);
}

// Function to speak text with lip sync
function speak(text) {
    // Cancel any ongoing speech
    speechSynthesis.cancel();
    
    // Create utterance with customized options
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Apply voice settings
    if (selectedVoice) {
        utterance.voice = selectedVoice;
    }
    
    utterance.rate = voiceOptions.rate;
    utterance.pitch = voiceOptions.pitch;
    utterance.volume = voiceOptions.volume;
    utterance.lang = voiceOptions.language;
    
    // Add event listeners for debugging
    utterance.onstart = function() {
        console.log("Speech started");
        const statusElement = document.getElementById("animation-status");
        statusElement.textContent = "Hablando...";
    };
    
    utterance.onend = function() {
        console.log("Speech ended");
        const statusElement = document.getElementById("animation-status");
        statusElement.textContent = "Animación completada";
        setTimeout(() => {
            statusElement.textContent = "";
        }, 2000);
    };
    
    utterance.onerror = function(event) {
        console.error("Speech error:", event);
        const statusElement = document.getElementById("animation-status");
        statusElement.textContent = "Error en la síntesis de voz";
    };
    
    // Integrate with face animation
    const success = speakWithLipSync(text);
    
    if (!success) {
        // Fallback to regular speech if lip sync fails
        speechSynthesis.speak(utterance);
    }
}

// Initialize TTS when the page loads
document.addEventListener('DOMContentLoaded', initTTS);