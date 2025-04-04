# Facial Animation with Lip Sync

This web application allows users to upload an image of a person and enter text to generate an animation where the person's lips move naturally based on the entered text. The application uses Wav2Lip for lip synchronization and gTTS for text-to-speech conversion.

## Features

- Upload an image of a person
- Enter text to be spoken
- Generate a video with synchronized lip movements
- Download the generated animation

## Technical Implementation

- **Backend**: Flask web server
- **Image Processing**: Pillow, OpenCV
- **Animation**: Wav2Lip for lip synchronization
- **Text-to-Speech**: gTTS (Google Text-to-Speech)
- **Video Generation**: imageio-ffmpeg
- **Frontend**: HTML, CSS, JavaScript with Bootstrap

## Setup and Installation

1. Install Python 3.7+ if not already installed

2. Clone this repository:
   ```
   git clone https://github.com/CarlxsSc/facial-animation-lip-sync.git
   cd facial-animation-lip-sync
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Download and set up Wav2Lip:
   - Follow the installation instructions at [Wav2Lip GitHub repository](https://github.com/Rudrabha/Wav2Lip)
   - Download the pre-trained model and place it in the `wav2lip_model` directory

5. Create the necessary directories:
   ```
   mkdir -p uploads results temp
   ```

6. Run the application:
   ```
   python app.py
   ```

7. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

1. Upload an image of a person (JPG, JPEG, or PNG format)
2. Enter the text you want the person to speak
3. Click "Generate Animation"
4. Wait for the animation to be generated (this may take a minute)
5. View and download the generated animation

## Wav2Lip Integration

This application uses Wav2Lip for high-quality lip synchronization. The integration includes several improvements:

### Setup

1. The Wav2Lip model should be placed in the `wav2lip_model/checkpoints/` directory
2. Run the fix scripts before first use:
   ```
   python fix_wav2lip.py      # Fixes NumPy compatibility issues
   python fix_wav2lip_paths.py  # Fixes path handling and audio loading
   ```

### Technical Details

- **Path Handling**: All paths are properly handled with absolute paths and correct quoting for Windows compatibility
- **Audio Processing**: Multiple fallback methods for audio loading (librosa, soundfile, scipy)
- **FFmpeg Integration**: Uses imageio_ffmpeg to locate the ffmpeg executable across platforms
- **Error Handling**: Comprehensive error logging and fallback mechanisms
- **Directory Management**: Automatically creates necessary temporary directories

### Troubleshooting

If you encounter issues with the Wav2Lip integration:

1. Check that the model file exists at `wav2lip_model/checkpoints/wav2lip_gan.pth`
2. Ensure ffmpeg is properly installed and accessible
3. Run the test script: `python test_wav2lip_direct.py`
4. Check the console output for detailed error messages

## Notes

- For best results, use a clear frontal image of a person's face
- The animation quality depends on the input image quality
- Longer text inputs will generate longer animations

## License

MIT License
