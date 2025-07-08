import os
import uuid
import traceback
import time
import logging
import subprocess
import shutil
import sys
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
from werkzeug.utils import secure_filename
import numpy as np
import cv2
from PIL import Image
import torch
import imageio
import imageio_ffmpeg
from gtts import gTTS
import tempfile
from mutagen.mp3 import MP3
from facial_animation import FacialAnimator, integrate_wav2lip

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Create necessary directories
UPLOAD_FOLDER = os.path.abspath('./uploads')
RESULT_FOLDER = os.path.abspath('./results')
TEMP_FOLDER = os.path.abspath('./temp')

for folder in [UPLOAD_FOLDER, RESULT_FOLDER, TEMP_FOLDER]:
    os.makedirs(folder, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER
app.config['TEMP_FOLDER'] = TEMP_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def text_to_speech(text, output_path):
    """Convert text to speech using gTTS"""
    try:
        tts = gTTS(text=text, lang='es', slow=False)
        tts.save(output_path)
        return True
    except Exception as e:
        logger.error(f"Error in text_to_speech: {str(e)}")
        traceback.print_exc()
        return False

def generate_animation(image_path, audio_path, output_path):
    """Generate lip-sync animation using the FacialAnimator class"""
    logger.info(f"Starting animation generation for {image_path} with audio {audio_path}")
    
    # Create a temporary directory for processing
    temp_folder = os.path.join(app.config['TEMP_FOLDER'], str(uuid.uuid4()))
    os.makedirs(temp_folder, exist_ok=True)
    
    try:
        # FORCE WAV2LIP: Skip FacialAnimator and directly try Wav2Lip integration
        logger.info("Forcing Wav2Lip integration for testing...")
        
        # Import the Wav2Lip integration function
        from facial_animation import integrate_wav2lip
        
        # Try to use Wav2Lip integration
        if integrate_wav2lip(image_path, audio_path, output_path, temp_folder):
            logger.info("Animation generated successfully using Wav2Lip")
            logger.info(f"Output file exists: {os.path.exists(output_path)}")
            logger.info(f"Output file size: {os.path.getsize(output_path) if os.path.exists(output_path) else 0} bytes")
            return True
        
        # If Wav2Lip fails, try fallback
        logger.warning("Wav2Lip integration failed, attempting fallback animation...")
        
        # Try fallback animation
        if create_fallback_animation(image_path, audio_path, output_path):
            logger.info("Fallback animation successful")
            logger.info(f"Output file exists: {os.path.exists(output_path)}")
            logger.info(f"Output file size: {os.path.getsize(output_path) if os.path.exists(output_path) else 0} bytes")
            return True
        
        logger.error("All animation methods failed")
        return False
        
    except Exception as e:
        logger.error(f"Error in generate_animation: {str(e)}")
        traceback.print_exc()
        
        # Try fallback as last resort
        try:
            logger.info("Attempting emergency fallback animation after exception...")
            if create_fallback_animation(image_path, audio_path, output_path):
                logger.info("Emergency fallback animation successful")
                logger.info(f"Output file exists: {os.path.exists(output_path)}")
                logger.info(f"Output file size: {os.path.getsize(output_path) if os.path.exists(output_path) else 0} bytes")
                return True
        except Exception as fallback_error:
            logger.error(f"Emergency fallback also failed: {str(fallback_error)}")
            traceback.print_exc()
        
        return False

def create_fallback_animation(image_path, audio_path, output_path):
    """Create a very simple animation when other methods fail"""
    try:
        logger.info("Starting fallback animation generation...")
        
        # Create a temporary directory for frames
        temp_dir = os.path.join(app.config['TEMP_FOLDER'], str(uuid.uuid4()))
        frames_dir = os.path.join(temp_dir, "frames")
        os.makedirs(frames_dir, exist_ok=True)
        
        # Load the image
        img = Image.open(image_path)
        
        # Convert RGBA to RGB if needed
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        
        # Ensure the image has even dimensions (required by some video codecs)
        width, height = img.size
        if width % 2 == 1:
            width -= 1
        if height % 2 == 1:
            height -= 1
        
        if width != img.width or height != img.height:
            img = img.resize((width, height))
        
        # Create simple frames (just the static image)
        frame_count = 30
        for i in range(frame_count):
            frame_path = os.path.join(frames_dir, f"frame_{i:04d}.jpg")
            img.save(frame_path, quality=95)
        
        # Get audio duration
        audio = MP3(audio_path)
        audio_duration = audio.info.length
        
        # Calculate fps based on audio duration
        fps = frame_count / max(1, audio_duration)
        
        # Create video from frames
        temp_video_path = os.path.join(app.config['TEMP_FOLDER'], f"{uuid.uuid4()}.mp4")
        
        # Use ffmpeg directly with simpler parameters
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        
        # Create video without audio first
        ffmpeg_cmd = [
            ffmpeg_exe,
            '-y',
            '-framerate', str(fps),
            '-i', os.path.join(frames_dir, 'frame_%04d.jpg'),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            temp_video_path
        ]
        
        logger.info("Running ffmpeg command: %s", ' '.join(ffmpeg_cmd))
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error("FFmpeg error: %s", result.stderr)
            raise Exception(f"FFmpeg error: {result.stderr}")
        
        # Add audio to video
        ffmpeg_audio_cmd = [
            ffmpeg_exe,
            '-y',
            '-i', temp_video_path,
            '-i', audio_path,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-shortest',
            output_path
        ]
        
        logger.info("Running ffmpeg audio command: %s", ' '.join(ffmpeg_audio_cmd))
        result = subprocess.run(ffmpeg_audio_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error("FFmpeg audio error: %s", result.stderr)
            raise Exception(f"FFmpeg audio error: {result.stderr}")
        
        # Clean up
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        logger.info("Fallback animation completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error in create_fallback_animation: {str(e)}")
        traceback.print_exc()
        return False

animations = []

@app.route('/')
def index():
    # Get list of recent videos
    videos = []
    try:
        result_files = os.listdir(app.config['RESULT_FOLDER'])
        video_files = [f for f in result_files if f.endswith('.mp4')]
        
        # Sort by creation time (newest first)
        video_files.sort(key=lambda x: os.path.getctime(os.path.join(app.config['RESULT_FOLDER'], x)), reverse=True)
        
        # Limit to 5 most recent videos
        recent_videos = video_files[:5]
        
        for video in recent_videos:
            video_path = os.path.join(app.config['RESULT_FOLDER'], video)
            creation_time = os.path.getctime(video_path)
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(creation_time))
            
            videos.append({
                'filename': video,
                'path': f"/results/{video}",
                'timestamp': timestamp
            })
    except Exception as e:
        logger.error(f"Error getting video list: {str(e)}")
        traceback.print_exc()
    
    return render_template('index.html', videos=videos)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and animation generation"""
    try:
        logger.info("Received upload request")
        # Check for both 'file' and 'image' field names for compatibility
        if 'file' in request.files:
            file = request.files['file']
        elif 'image' in request.files:
            file = request.files['image']
        else:
            logger.error("No file part in the request")
            return jsonify({'error': 'No file part'}), 400
        
        if file.filename == '':
            logger.error("No file selected")
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            logger.error(f"File type not allowed: {file.filename}")
            return jsonify({'error': 'File type not allowed. Please upload a PNG or JPG image.'}), 400
        
        # Get the text from the form
        text = request.form.get('text', '')
        if not text:
            logger.error("No text provided")
            return jsonify({'error': 'Please enter some text for the animation'}), 400
        
        # Generate unique filenames
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())
        
        # Save the uploaded file
        filename = secure_filename(file.filename)
        base, ext = os.path.splitext(filename)
        image_filename = f"{unique_id}{ext}"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        file.save(image_path)
        logger.info(f"Saved uploaded file to {image_path}")
        
        # Create audio file from text
        audio_filename = f"{unique_id}.mp3"
        audio_path = os.path.join(app.config['TEMP_FOLDER'], audio_filename)
        
        if not text_to_speech(text, audio_path):
            logger.error("Failed to convert text to speech")
            return jsonify({'error': 'Failed to convert text to speech'}), 500
        
        logger.info(f"Created audio file at {audio_path}")
        
        # Generate output filename
        output_filename = f"{unique_id}.mp4"
        output_path = os.path.join(app.config['RESULT_FOLDER'], output_filename)
        
        logger.info(f"Starting animation generation with image: {image_path}, audio: {audio_path}, output: {output_path}")
        
        # Generate the animation
        if not generate_animation(image_path, audio_path, output_path):
            logger.error("Failed to generate animation")
            return jsonify({'error': 'Failed to generate animation'}), 500
        
        logger.info(f"Animation generated successfully at {output_path}")
        logger.info(f"Output file exists: {os.path.exists(output_path)}")
        logger.info(f"Output file size: {os.path.getsize(output_path) if os.path.exists(output_path) else 0} bytes")
        
        # Add to animations list
        animations.append({
            'id': unique_id,
            'image': url_for('uploaded_file', filename=image_filename),
            'video': url_for('result_file', filename=output_filename),
            'text': text,
            'timestamp': timestamp
        })
        
        # Return success response with video URL
        return jsonify({
            'success': True,
            'message': 'Animation generated successfully',
            'video_url': url_for('result_file', filename=output_filename),
            'id': unique_id
        })
        
    except Exception as e:
        logger.error(f"Error in upload_file: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/results/<filename>')
def result_file(filename):
    return send_from_directory(app.config['RESULT_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
