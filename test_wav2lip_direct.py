import os
import sys
import subprocess
import uuid
import time
import imageio_ffmpeg
import traceback
import cv2
import numpy as np
from gtts import gTTS

def create_test_audio(audio_path, text):
    tts = gTTS(text, lang='en')
    tts.save(audio_path)

def ensure_rgb_image(image_path, output_path=None):
    """Ensure the image is in RGB format with 3 channels"""
    try:
        # Read the image
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if img is None:
            print(f"Error: Could not read image at {image_path}")
            return None
        
        # Ensure it's RGB (OpenCV loads as BGR)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Convert back to BGR for saving with OpenCV
        img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
        
        # If output path is specified, save the processed image
        if output_path:
            cv2.imwrite(output_path, img_bgr)
            print(f"Saved processed image to {output_path}")
            return output_path
        else:
            # Save to a temporary file
            temp_path = os.path.join(os.path.dirname(image_path), f"temp_rgb_{uuid.uuid4()}.jpg")
            cv2.imwrite(temp_path, img_bgr)
            print(f"Saved processed image to {temp_path}")
            return temp_path
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        traceback.print_exc()
        return None

def test_wav2lip_direct():
    """Test the Wav2Lip integration directly"""
    print("Testing Wav2Lip integration directly...")
    
    # Use a sample image
    image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads", "037c6c3e-3849-47c7-adb0-ab2070000c2e.png")
    if not os.path.exists(image_path):
        print(f"Test image not found at {image_path}")
        return False
    print(f"Using image: {image_path}")
    
    # Process the image to ensure it's RGB
    processed_image_path = ensure_rgb_image(image_path)
    if not processed_image_path:
        print("Failed to process the image")
        return False
    print(f"Processed image: {processed_image_path}")
    
    # Create test output directory
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_wav2lip_output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a test audio file
    audio_path = os.path.join(output_dir, "test_audio.mp3")
    create_test_audio(audio_path, "This is a test of the Wav2Lip integration.")
    print(f"Created test audio: {audio_path}")
    
    # Set output path
    output_uuid = str(uuid.uuid4())
    output_path = os.path.join(output_dir, f"test_output_{output_uuid}.mp4")
    print(f"Output will be saved to: {output_path}")
    
    # Get ffmpeg path
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"Using ffmpeg from: {ffmpeg_exe}")
    
    # Set up environment for ffmpeg
    env = os.environ.copy()
    env["PATH"] = os.path.dirname(ffmpeg_exe) + os.pathsep + env.get("PATH", "")
    
    # Create temp directory in wav2lip repo
    wav2lip_repo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wav2lip_repo")
    temp_dir = os.path.join(wav2lip_repo_path, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Wav2Lip model path
    checkpoint_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                  "wav2lip_model", "checkpoints", "wav2lip_gan.pth")
    
    # Create command
    cmd = [
        sys.executable,
        os.path.join(wav2lip_repo_path, "inference.py"),
        "--face", processed_image_path,
        "--audio", audio_path,
        "--outfile", output_path,
        "--checkpoint_path", checkpoint_path,
        "--pads", "0", "0", "0", "0",
        "--resize_factor", "1",
        "--wav2lip_batch_size", "128",
        "--face_det_batch_size", "16",
        "--nosmooth"
    ]
    
    cmd_str = " ".join(cmd)
    print(f"Running command: {cmd_str}")
    
    # Run the command with a timeout of 5 minutes (300 seconds)
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            env=env,
            cwd=wav2lip_repo_path
        )
        
        stdout, stderr = process.communicate(timeout=300)  # 5 minute timeout
        
        print(stdout)
        if stderr:
            print(f"Errors: {stderr}")
        
        # Check if output file was created
        if os.path.exists(output_path):
            print(f"Success! Output file created at: {output_path}")
            print(f"File size: {os.path.getsize(output_path)} bytes")
            return True
        else:
            print(f"Error: Output file not created at {output_path}")
            return False
            
    except subprocess.TimeoutExpired:
        process.kill()
        print("Process timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"Error running Wav2Lip: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_wav2lip_direct()
    if success:
        print("Wav2Lip integration test successful!")
    else:
        print("Wav2Lip integration test failed!")
