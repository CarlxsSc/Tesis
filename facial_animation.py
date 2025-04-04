import os
import cv2
import numpy as np
import torch
import face_alignment
import tempfile
import subprocess
import shutil
import time
import uuid
import traceback
from PIL import Image
import imageio
import imageio_ffmpeg
from mutagen.mp3 import MP3
import sys
import logging

logger = logging.getLogger(__name__)

class FacialAnimator:
    def __init__(self, temp_folder):
        self.temp_folder = temp_folder
        # Initialize face alignment model for 3D landmark detection
        self.fa = face_alignment.FaceAlignment(
            face_alignment.LandmarksType._3D if hasattr(face_alignment.LandmarksType, '_3D') else face_alignment.LandmarksType.THREE_D,
            device='cuda' if torch.cuda.is_available() else 'cpu',
            flip_input=False
        )
        
        # Create necessary directories
        os.makedirs(temp_folder, exist_ok=True)
    
    def detect_landmarks(self, image):
        """Detect facial landmarks in the image"""
        try:
            if isinstance(image, str):
                # Load image if path is provided
                image = cv2.imread(image)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect landmarks
            landmarks = self.fa.get_landmarks(image)
            
            if landmarks is None or len(landmarks) == 0:
                print("No face detected in the image")
                return None
                
            # Return the first face's landmarks
            return landmarks[0]
        except Exception as e:
            print(f"Error in detect_landmarks: {str(e)}")
            traceback.print_exc()
            return None
    
    def calculate_head_pose(self, landmarks):
        """Calculate head pose (pitch, yaw, roll) from landmarks"""
        # This is a simplified version - in a real implementation, 
        # you would use more sophisticated methods
        try:
            # Get specific landmarks for pose estimation
            nose_tip = landmarks[30]
            chin = landmarks[8]
            left_eye = landmarks[36]
            right_eye = landmarks[45]
            left_mouth = landmarks[48]
            right_mouth = landmarks[54]
            
            # Calculate simple pose parameters
            # These are simplified calculations for demonstration
            pitch = np.arctan2(nose_tip[1] - chin[1], nose_tip[2] - chin[2])
            yaw = np.arctan2(right_eye[0] - left_eye[0], right_eye[2] - left_eye[2])
            roll = np.arctan2(right_mouth[1] - left_mouth[1], right_mouth[0] - left_mouth[0])
            
            return {
                'pitch': pitch,
                'yaw': yaw,
                'roll': roll
            }
        except Exception as e:
            print(f"Error in calculate_head_pose: {str(e)}")
            traceback.print_exc()
            return None
    
    def analyze_audio_for_phonemes(self, audio_path):
        """
        Analyze audio file to extract phoneme timing information
        This is a simplified version that simulates phoneme extraction
        """
        try:
            # Get audio duration
            audio = MP3(audio_path)
            audio_duration = audio.info.length
            
            # In a real implementation, you would use a phoneme recognition model
            # For now, we'll create a simulated pattern based on audio properties
            
            # Calculate number of frames based on duration (assuming 30fps)
            frame_count = int(audio_duration * 30)
            
            # Create phoneme patterns
            # We'll simulate different mouth shapes corresponding to phonemes
            phonemes = []
            
            # Generate a more realistic pattern that includes pauses and variations
            for i in range(frame_count):
                t = i / frame_count
                
                # Create a pattern with natural pauses and variations
                # This simulates the rhythm of natural speech
                
                # Base pattern with multiple frequencies
                pattern = 0.4 * np.sin(t * 2 * np.pi * 2.5)  # Base frequency
                pattern += 0.2 * np.sin(t * 2 * np.pi * 5)   # Higher frequency for details
                pattern += 0.1 * np.sin(t * 2 * np.pi * 8)   # Even higher frequency
                
                # Add natural pauses (when pattern is below threshold)
                if pattern < -0.2:
                    mouth_open = 0.1  # Almost closed during pauses
                else:
                    # Map to 0.1-1.0 range (mouth is never completely closed)
                    mouth_open = 0.1 + max(0, (pattern + 0.5)) * 0.9
                
                phonemes.append(mouth_open)
            
            return phonemes, frame_count
        except Exception as e:
            print(f"Error in analyze_audio_for_phonemes: {str(e)}")
            traceback.print_exc()
            return None, 30  # Default to 30 frames with no pattern

    def generate_animation_frames(self, image_path, audio_path, output_dir):
        """Generate animation frames with lip sync"""
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Load the input image
            img = cv2.imread(image_path)
            if img is None:
                print(f"Error: Could not load image from {image_path}")
                return False
                
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Detect facial landmarks
            landmarks = self.detect_landmarks(img_rgb)
            if landmarks is None:
                print("Error: Could not detect facial landmarks")
                return False
            
            # Get image dimensions
            height, width = img.shape[:2]
            
            # Improved parameters for facial animation
            # These parameters control the intensity of mouth and head movements
            mouth_open_scale = 0.7  # Scale factor for mouth opening (increased for better visibility)
            head_movement_scale = 0.3  # Scale factor for head movement
            blink_probability = 0.05  # Probability of blinking in each frame
            
            # Analyze audio to extract phoneme information for better lip sync
            mouth_patterns, frame_count = self.analyze_audio_for_phonemes(audio_path)
            
            if mouth_patterns is None:
                # Fallback to simple pattern if audio analysis fails
                frame_count = 30
                mouth_patterns = []
                for i in range(frame_count):
                    t = i / frame_count * 2 * np.pi * 3
                    mouth_open = (np.sin(t) + 1) / 2
                    mouth_patterns.append(mouth_open * mouth_open_scale)
            
            # Generate frames with animated facial features
            for i in range(frame_count):
                # Create a copy of the original image for this frame
                frame = img_rgb.copy()
                
                # Apply mouth movement based on the phoneme pattern
                mouth_open = mouth_patterns[i % len(mouth_patterns)]
                
                # Get mouth landmarks
                upper_lip = landmarks[51:54]  # Upper lip landmarks
                lower_lip = landmarks[57:60]  # Lower lip landmarks
                
                # Calculate mouth center
                mouth_center_x = int(np.mean([p[0] for p in upper_lip + lower_lip]))
                mouth_center_y = int(np.mean([p[1] for p in upper_lip + lower_lip]))
                
                # Calculate natural mouth width based on landmarks
                left_corner = landmarks[48]
                right_corner = landmarks[54]
                mouth_width = int(np.linalg.norm(np.array(right_corner) - np.array(left_corner)))
                
                # Calculate mouth height based on phoneme
                natural_mouth_height = int(np.mean([p[1] for p in lower_lip]) - np.mean([p[1] for p in upper_lip]))
                mouth_height = int(natural_mouth_height + (mouth_open * 15))  # Add dynamic opening
                
                # Create a mask for the mouth region
                mask = np.zeros((height, width), dtype=np.uint8)
                
                # Draw the mouth shape on the mask
                cv2.ellipse(mask, 
                           (mouth_center_x, mouth_center_y), 
                           (mouth_width // 2, mouth_height), 
                           0, 0, 360, 255, -1)
                
                # Apply head movement (slight random movement)
                # In a real implementation, this would be based on audio energy and content
                head_move_x = int(np.sin(i/10) * 5 * head_movement_scale)
                head_move_y = int(np.cos(i/12) * 3 * head_movement_scale)
                
                # Apply translation to simulate head movement
                M = np.float32([[1, 0, head_move_x], [0, 1, head_move_y]])
                frame = cv2.warpAffine(frame, M, (width, height))
                
                # Simulate blinking (random)
                if np.random.random() < blink_probability:
                    # Get eye landmarks
                    left_eye_top = landmarks[37:40]  # Top left eye landmarks
                    left_eye_bottom = landmarks[40:42]  # Bottom left eye landmarks
                    right_eye_top = landmarks[43:46]  # Top right eye landmarks
                    right_eye_bottom = landmarks[46:48]  # Bottom right eye landmarks
                    
                    # Calculate eye centers
                    left_eye_top_y = int(np.mean([p[1] for p in left_eye_top]))
                    left_eye_bottom_y = int(np.mean([p[1] for p in left_eye_bottom]))
                    right_eye_top_y = int(np.mean([p[1] for p in right_eye_top]))
                    right_eye_bottom_y = int(np.mean([p[1] for p in right_eye_bottom]))
                    
                    # Fix: Calculate eye centers separately to avoid shape mismatch
                    left_eye_x = int(np.mean([p[0] for p in left_eye_top] + [p[0] for p in left_eye_bottom]))
                    right_eye_x = int(np.mean([p[0] for p in right_eye_top] + [p[0] for p in right_eye_bottom]))
                    
                    # Draw closed eyes
                    cv2.line(frame, 
                            (left_eye_x - 15, (left_eye_top_y + left_eye_bottom_y) // 2),
                            (left_eye_x + 15, (left_eye_top_y + left_eye_bottom_y) // 2),
                            (0, 0, 0), 2)
                    cv2.line(frame, 
                            (right_eye_x - 15, (right_eye_top_y + right_eye_bottom_y) // 2),
                            (right_eye_x + 15, (right_eye_top_y + right_eye_bottom_y) // 2),
                            (0, 0, 0), 2)
                
                # Save the frame
                frame_path = os.path.join(output_dir, f"frame_{i:04d}.jpg")
                cv2.imwrite(frame_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            
            return True
        except Exception as e:
            print(f"Error in generate_animation_frames: {str(e)}")
            traceback.print_exc()
            return False
    
    def create_video_from_frames(self, frames_dir, audio_path, output_path, fps=30):
        """Create video from frames and add audio"""
        try:
            # Get audio duration
            audio = MP3(audio_path)
            audio_duration = audio.info.length
            
            # Count frames
            frame_files = sorted([f for f in os.listdir(frames_dir) if f.startswith("frame_") and f.endswith(".jpg")])
            frame_count = len(frame_files)
            
            # Calculate actual fps based on audio duration
            if frame_count > 0 and audio_duration > 0:
                calculated_fps = frame_count / audio_duration
                fps = min(calculated_fps, 30)  # Cap at 30 fps
            
            # Get the first frame to determine dimensions
            if not frame_files:
                print("No frames found in directory")
                return False
                
            first_frame_path = os.path.join(frames_dir, frame_files[0])
            first_frame = cv2.imread(first_frame_path)
            height, width, _ = first_frame.shape
            
            # Ensure dimensions are even (required for H.264 encoding)
            if width % 2 != 0:
                width -= 1
            if height % 2 != 0:
                height -= 1
                
            # Resize all frames to ensure even dimensions
            for frame_file in frame_files:
                frame_path = os.path.join(frames_dir, frame_file)
                frame = cv2.imread(frame_path)
                if frame is not None:
                    resized_frame = cv2.resize(frame, (width, height))
                    cv2.imwrite(frame_path, resized_frame)
            
            # Create temporary video without audio
            temp_video_path = os.path.join(self.temp_folder, f"{uuid.uuid4()}.mp4")
            
            # Use ffmpeg to create video from frames
            ffmpeg_cmd = [
                imageio_ffmpeg.get_ffmpeg_exe(),
                '-y',  # Overwrite output file if it exists
                '-framerate', str(fps),
                '-i', os.path.join(frames_dir, 'frame_%04d.jpg'),
                '-c:v', 'libx264',
                '-profile:v', 'high',
                '-crf', '20',
                '-pix_fmt', 'yuv420p',
                temp_video_path
            ]
            
            print(f"Running ffmpeg command: {' '.join(ffmpeg_cmd)}")
            subprocess.run(ffmpeg_cmd, check=True)
            
            # Add audio to video
            ffmpeg_audio_cmd = [
                imageio_ffmpeg.get_ffmpeg_exe(),
                '-y',
                '-i', temp_video_path,
                '-i', audio_path,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-shortest',
                output_path
            ]
            
            print(f"Running ffmpeg audio command: {' '.join(ffmpeg_audio_cmd)}")
            subprocess.run(ffmpeg_audio_cmd, check=True)
            
            # Clean up temporary video
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)
            
            return True
        except Exception as e:
            print(f"Error in create_video_from_frames: {str(e)}")
            traceback.print_exc()
            return False
    
    def generate_animation(self, image_path, audio_path, output_path):
        """Main function to generate lip-sync animation"""
        try:
            # Create a unique temporary directory for this process
            temp_dir = os.path.join(self.temp_folder, str(uuid.uuid4()))
            frames_dir = os.path.join(temp_dir, "frames")
            os.makedirs(frames_dir, exist_ok=True)
            
            # Generate animation frames
            if not self.generate_animation_frames(image_path, audio_path, frames_dir):
                return False
            
            # Create video from frames with audio
            if not self.create_video_from_frames(frames_dir, audio_path, output_path):
                return False
            
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            return True
        except Exception as e:
            print(f"Error in generate_animation: {str(e)}")
            traceback.print_exc()
            return False

def ensure_rgb_image(image_path, output_path=None):
    """Ensure the image is in RGB format with 3 channels"""
    try:
        logger.info(f"Processing image {image_path} to ensure RGB format")
        # Read the image
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if img is None:
            logger.error(f"Error: Could not read image at {image_path}")
            return None
        
        # Ensure it's RGB (OpenCV loads as BGR)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Convert back to BGR for saving with OpenCV
        img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
        
        # If output path is specified, save the processed image
        if output_path:
            cv2.imwrite(output_path, img_bgr)
            logger.info(f"Saved processed image to {output_path}")
            return output_path
        else:
            # Save to a temporary file
            temp_path = os.path.join(os.path.dirname(image_path), f"temp_rgb_{uuid.uuid4()}.jpg")
            cv2.imwrite(temp_path, img_bgr)
            logger.info(f"Saved processed image to {temp_path}")
            return temp_path
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        traceback.print_exc()
        return None

def integrate_wav2lip(image_path, audio_path, output_path, temp_folder):
    """
    Function to integrate with Wav2Lip directly using subprocess
    This is an alternative approach that calls the Wav2Lip inference script directly
    """
    try:
        logger.info(f"Starting Wav2Lip integration with image: {image_path}, audio: {audio_path}")
        
        # Create temp directory with absolute paths
        wav2lip_repo_path = os.path.abspath("wav2lip_repo")
        wav2lip_temp_dir = os.path.join(wav2lip_repo_path, "temp")
        os.makedirs(wav2lip_temp_dir, exist_ok=True)
        
        # Path to Wav2Lip inference script
        wav2lip_inference_path = os.path.join(wav2lip_repo_path, "inference.py")
        
        # Path to the model checkpoint
        checkpoint_path = os.path.abspath("wav2lip_model/checkpoints/wav2lip_gan.pth")
        
        # Check if Wav2Lip model exists
        if not os.path.exists(wav2lip_inference_path):
            logger.error(f"Wav2Lip inference script not found at {wav2lip_inference_path}")
            logger.info("Using fallback animation method instead.")
            return False
            
        if not os.path.exists(checkpoint_path):
            logger.error(f"Wav2Lip model checkpoint not found at {checkpoint_path}")
            logger.info("Using fallback animation method instead.")
            return False
        
        # Ensure image and audio paths are absolute
        image_path = os.path.abspath(image_path)
        audio_path = os.path.abspath(audio_path)
        output_path = os.path.abspath(output_path)
        
        # Process the image to ensure it's in RGB format (3 channels)
        processed_image_path = ensure_rgb_image(image_path)
        if not processed_image_path:
            logger.error("Failed to process the image for Wav2Lip")
            return False
        logger.info(f"Using processed image: {processed_image_path}")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Get ffmpeg executable path
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        logger.info(f"Using ffmpeg executable: {ffmpeg_exe}")
        
        # Create a direct command to run Wav2Lip
        cmd = [
            sys.executable,
            wav2lip_inference_path,
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
        
        # Set environment variables for ffmpeg
        env = os.environ.copy()
        env["PATH"] = os.path.dirname(ffmpeg_exe) + os.pathsep + env.get("PATH", "")
        
        logger.info(f"Running Wav2Lip with command: {' '.join(cmd)}")
        logger.info(f"Working directory: {wav2lip_repo_path}")
        
        # Run the command with the modified environment and working directory
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            env=env,
            cwd=wav2lip_repo_path  # Set working directory to wav2lip repo
        )
        
        stdout, stderr = process.communicate()
        
        logger.info(f"Wav2Lip stdout: {stdout}")
        if stderr:
            logger.error(f"Wav2Lip stderr: {stderr}")
        
        if process.returncode != 0:
            logger.error(f"Error running Wav2Lip: {stderr}")
            return False
        
        # Check if output file was created
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            logger.error(f"Wav2Lip failed to create output file: {output_path}")
            return False
        
        # Clean up temporary files
        try:
            if processed_image_path and os.path.exists(processed_image_path) and "temp_rgb_" in processed_image_path:
                os.remove(processed_image_path)
                logger.info(f"Removed temporary processed image: {processed_image_path}")
        except Exception as e:
            logger.warning(f"Warning: Failed to clean up temporary file: {str(e)}")
        
        logger.info(f"Wav2Lip successfully created output file: {output_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error in integrate_wav2lip: {str(e)}")
        traceback.print_exc()
        return False
