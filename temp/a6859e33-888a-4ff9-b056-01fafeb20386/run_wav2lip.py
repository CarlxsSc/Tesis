
import sys
import os
import subprocess

# Add the Wav2Lip repo to the Python path
sys.path.append(r"C:\Users\Killtro\Desktop\Tesis 2.0\wav2lip_repo")

# Import required modules
import torch
from models import Wav2Lip

# Set device
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Using device: {device}")

# Run the inference script
cmd = [
    sys.executable,
    r"C:\Users\Killtro\Desktop\Tesis 2.0\wav2lip_repo\inference.py",
    "--face", r"C:\Users\Killtro\Desktop\Tesis 2.0\uploads\434fe859-0eae-4a3a-aa18-a61d86867804.png",
    "--audio", r"C:\Users\Killtro\Desktop\Tesis 2.0\temp\434fe859-0eae-4a3a-aa18-a61d86867804.mp3",
    "--outfile", r"C:\Users\Killtro\Desktop\Tesis 2.0\results\434fe859-0eae-4a3a-aa18-a61d86867804.mp4",
    "--checkpoint_path", r"C:\Users\Killtro\Desktop\Tesis 2.0\wav2lip_model\checkpoints\wav2lip_gan.pth",
    "--pads", "0", "0", "0", "0",
    "--resize_factor", "1",
    "--wav2lip_batch_size", "128",
    "--face_det_batch_size", "16",
    "--no_smooth"
]

print("Running command:", ' '.join(cmd))
subprocess.run(cmd)
