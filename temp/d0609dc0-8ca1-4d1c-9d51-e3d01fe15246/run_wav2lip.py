
import sys
import os
import subprocess
import time

# Add the Wav2Lip repo to the Python path
sys.path.append(r"C:\Users\Killtro\Desktop\Tesis 2.0\wav2lip_repo")

# Set environment variables for ffmpeg
os.environ['PATH'] = r"C:\Users\Killtro\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries" + os.pathsep + os.environ.get('PATH', '')

# Print current working directory and paths
print(f"Current working directory: {os.getcwd()}")
print(f"Image path exists: {os.path.exists(r'C:\Users\Killtro\Desktop\Tesis 2.0\uploads\f8e2e9a4-106b-4348-bca3-f5fade70d587.png')}")
print(f"Audio path exists: {os.path.exists(r'C:\Users\Killtro\Desktop\Tesis 2.0\temp\f8e2e9a4-106b-4348-bca3-f5fade70d587.mp3')}")
print(f"Checkpoint path exists: {os.path.exists(r'C:\Users\Killtro\Desktop\Tesis 2.0\wav2lip_model\checkpoints\wav2lip_gan.pth')}")

# Set device
import torch
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Using device: {device}")

# Run the inference script
cmd = [
    sys.executable,
    r"C:\Users\Killtro\Desktop\Tesis 2.0\wav2lip_repo\inference.py",
    "--face", r"C:\Users\Killtro\Desktop\Tesis 2.0\uploads\f8e2e9a4-106b-4348-bca3-f5fade70d587.png",
    "--audio", r"C:\Users\Killtro\Desktop\Tesis 2.0\temp\f8e2e9a4-106b-4348-bca3-f5fade70d587.mp3",
    "--outfile", r"C:\Users\Killtro\Desktop\Tesis 2.0\results\f8e2e9a4-106b-4348-bca3-f5fade70d587.mp4",
    "--checkpoint_path", r"C:\Users\Killtro\Desktop\Tesis 2.0\wav2lip_model\checkpoints\wav2lip_gan.pth",
    "--pads", "0", "0", "0", "0",
    "--resize_factor", "1",
    "--wav2lip_batch_size", "128",
    "--face_det_batch_size", "16",
    "--nosmooth"
]

print("Running command:", ' '.join(cmd))
result = subprocess.run(cmd, capture_output=True, text=True)

print("Return code:", result.returncode)
print("Output:", result.stdout)

if result.returncode != 0:
    print("Error:", result.stderr)
    sys.exit(1)

# Check if output file was created
if os.path.exists(r"C:\Users\Killtro\Desktop\Tesis 2.0\results\f8e2e9a4-106b-4348-bca3-f5fade70d587.mp4"):
    print(f"Successfully created output file: C:\Users\Killtro\Desktop\Tesis 2.0\results\f8e2e9a4-106b-4348-bca3-f5fade70d587.mp4")
    print(f"File size: {os.path.getsize(r'C:\Users\Killtro\Desktop\Tesis 2.0\results\f8e2e9a4-106b-4348-bca3-f5fade70d587.mp4')}")
else:
    print(f"Failed to create output file: C:\Users\Killtro\Desktop\Tesis 2.0\results\f8e2e9a4-106b-4348-bca3-f5fade70d587.mp4")
    sys.exit(1)
