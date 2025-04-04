
import os
import sys
import subprocess

print("Using device: cpu")

cmd = [
    sys.executable,
    r"C:\Users\Killtro\Desktop\Tesis 2.0\wav2lip_repo\inference.py",
    "--face", r"C:\Users\Killtro\Desktop\Tesis 2.0\uploads\037c6c3e-3849-47c7-adb0-ab2070000c2e.png",
    "--audio", r"C:\Users\Killtro\Desktop\Tesis 2.0\temp\037c6c3e-3849-47c7-adb0-ab2070000c2e.mp3",
    "--outfile", r"C:\Users\Killtro\Desktop\Tesis 2.0\test_wav2lip\test_output.mp4",
    "--checkpoint_path", r"C:\Users\Killtro\Desktop\Tesis 2.0\wav2lip_model\checkpoints\wav2lip_gan.pth",
    "--pads", "0", "0", "0", "0",
    "--resize_factor", "1",
    "--wav2lip_batch_size", "128",
    "--face_det_batch_size", "16",
    "--no_smooth"
]

print("Running command:", " ".join(cmd))
subprocess.run(cmd)

if os.path.exists(r"C:\Users\Killtro\Desktop\Tesis 2.0\test_wav2lip\test_output.mp4"):
    print(f"Successfully generated video: C:\Users\Killtro\Desktop\Tesis 2.0\test_wav2lip\test_output.mp4")
else:
    print(f"Failed to generate video: C:\Users\Killtro\Desktop\Tesis 2.0\test_wav2lip\test_output.mp4")
