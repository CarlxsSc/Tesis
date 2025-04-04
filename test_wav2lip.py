import os
import sys
import subprocess
import traceback

def test_wav2lip_integration():
    """Test the Wav2Lip integration"""
    try:
        # Import necessary libraries
        import librosa
        print(f"Librosa import successful, version: {librosa.__version__}")
        
        # Check if Wav2Lip repo exists
        wav2lip_repo = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wav2lip_repo')
        if not os.path.exists(wav2lip_repo):
            print(f"Wav2Lip repository not found at {wav2lip_repo}")
            return False
        
        # Check if the inference script exists
        inference_script = os.path.join(wav2lip_repo, 'inference.py')
        if not os.path.exists(inference_script):
            print(f"Inference script not found at {inference_script}")
            return False
        
        print(f"Wav2Lip repository found at {wav2lip_repo}")
        print(f"Inference script found at {inference_script}")
        
        # Check if the model checkpoint exists
        checkpoint_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wav2lip_model', 'checkpoints', 'wav2lip_gan.pth')
        if not os.path.exists(checkpoint_path):
            print(f"Model checkpoint not found at {checkpoint_path}")
            return False
        
        print(f"Model checkpoint found at {checkpoint_path}")
        
        # Create test directories
        test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_wav2lip')
        os.makedirs(test_dir, exist_ok=True)
        
        # Use a sample image and audio from the uploads and temp folders
        uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
        
        # Find a sample image and audio
        image_files = [f for f in os.listdir(uploads_dir) if f.endswith('.png') or f.endswith('.jpg')]
        audio_files = [f for f in os.listdir(temp_dir) if f.endswith('.mp3') or f.endswith('.wav')]
        
        if not image_files:
            print("No sample images found in uploads directory")
            return False
        
        if not audio_files:
            print("No sample audio files found in temp directory")
            return False
        
        sample_image = os.path.join(uploads_dir, image_files[0])
        sample_audio = os.path.join(temp_dir, audio_files[0])
        output_video = os.path.join(test_dir, 'test_output.mp4')
        
        print(f"Using sample image: {sample_image}")
        print(f"Using sample audio: {sample_audio}")
        print(f"Output video will be saved to: {output_video}")
        
        # Create a script to run Wav2Lip
        run_script = os.path.join(test_dir, 'run_wav2lip.py')
        with open(run_script, 'w') as f:
            f.write(f"""
import os
import sys
import subprocess

print("Using device: cpu")

cmd = [
    sys.executable,
    r"{inference_script}",
    "--face", r"{sample_image}",
    "--audio", r"{sample_audio}",
    "--outfile", r"{output_video}",
    "--checkpoint_path", r"{checkpoint_path}",
    "--pads", "0", "0", "0", "0",
    "--resize_factor", "1",
    "--wav2lip_batch_size", "128",
    "--face_det_batch_size", "16",
    "--no_smooth"
]

print("Running command:", " ".join(cmd))
subprocess.run(cmd)

if os.path.exists(r"{output_video}"):
    print(f"Successfully generated video: {output_video}")
else:
    print(f"Failed to generate video: {output_video}")
""")
        
        # Run the script
        print("Running Wav2Lip test script...")
        result = subprocess.run([sys.executable, run_script], capture_output=True, text=True)
        
        print("Wav2Lip stdout:", result.stdout)
        print("Wav2Lip stderr:", result.stderr)
        
        # Check if the output video was created
        if os.path.exists(output_video):
            print(f"Successfully generated video: {output_video}")
            return True
        else:
            print(f"Failed to generate video: {output_video}")
            return False
        
    except Exception as e:
        print(f"Error testing Wav2Lip integration: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Wav2Lip integration...")
    success = test_wav2lip_integration()
    
    if success:
        print("Wav2Lip integration test successful!")
    else:
        print("Wav2Lip integration test failed!")
