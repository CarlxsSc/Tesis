import os
import sys
import subprocess
import shutil
import zipfile
import urllib.request
import argparse

def download_file(url, destination):
    """Download a file from a URL to a destination path"""
    print(f"Downloading {url} to {destination}...")
    try:
        urllib.request.urlretrieve(url, destination)
        print(f"Downloaded {destination} successfully")
        return True
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Setup Wav2Lip for facial animation")
    parser.add_argument('--skip-clone', action='store_true', help='Skip cloning the Wav2Lip repository')
    parser.add_argument('--skip-model', action='store_true', help='Skip downloading the pre-trained model')
    parser.add_argument('--skip-fixes', action='store_true', help='Skip applying compatibility fixes')
    args = parser.parse_args()
    
    # Create necessary directories
    os.makedirs('wav2lip_model', exist_ok=True)
    os.makedirs('wav2lip_model/checkpoints', exist_ok=True)
    os.makedirs('wav2lip_repo/temp', exist_ok=True)
    
    # Clone Wav2Lip repository if not skipped
    if not args.skip_clone:
        print("Cloning Wav2Lip repository...")
        subprocess.run(
            ["git", "clone", "https://github.com/Rudrabha/Wav2Lip.git", "wav2lip_repo"],
            check=True
        )
        
        # Copy necessary files to our model directory
        print("Copying necessary files to wav2lip_model directory...")
        src_files = [
            "wav2lip_repo/models/wav2lip_gan.pth",
            "wav2lip_repo/face_detection/detection/sfd/sfd_detector.py",
            "wav2lip_repo/face_detection/detection/sfd/sfd_face_detector.py",
            "wav2lip_repo/face_detection/api.py",
            "wav2lip_repo/models/lipsync_expert.py",
            "wav2lip_repo/audio.py",
            "wav2lip_repo/inference.py",
            "wav2lip_repo/hparams.py"
        ]
        
        for src_file in src_files:
            if os.path.exists(src_file):
                # Create destination directory if it doesn't exist
                dst_dir = os.path.dirname(os.path.join("wav2lip_model", os.path.relpath(src_file, "wav2lip_repo")))
                os.makedirs(dst_dir, exist_ok=True)
                
                # Copy the file
                shutil.copy2(src_file, os.path.join("wav2lip_model", os.path.relpath(src_file, "wav2lip_repo")))
    
    # Download pre-trained model if not skipped
    if not args.skip_model:
        # The original URL is no longer valid, using an alternative source
        # model_url = "https://github.com/Rudrabha/Wav2Lip/raw/master/checkpoints/wav2lip_gan.pth"
        model_url = "https://iiitaphyd-my.sharepoint.com/personal/radrabha_m_research_iiit_ac_in/_layouts/15/download.aspx?share=EdjI7bZlgApMqsVoEUUXpLsBxqXbn5z8VTmoxp55YNDcIA"
        model_path = os.path.join("wav2lip_model", "checkpoints", "wav2lip_gan.pth")
        
        # Create checkpoints directory
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Download the model
        print(f"Downloading pre-trained Wav2Lip model...")
        print(f"Note: This is a large file (~150MB) and might take some time to download.")
        print(f"If the download fails, you can manually download it from:")
        print(f"https://iiitaphyd-my.sharepoint.com/personal/radrabha_m_research_iiit_ac_in/_layouts/15/download.aspx?share=EdjI7bZlgApMqsVoEUUXpLsBxqXbn5z8VTmoxp55YNDcIA")
        print(f"and place it in: {model_path}")
        
        download_file(model_url, model_path)
    
    # Apply fixes if not skipped
    if not args.skip_fixes:
        print("\nApplying compatibility fixes...")
        
        # Fix NumPy compatibility issues
        print("Fixing NumPy compatibility issues...")
        try:
            import fix_wav2lip
            fix_wav2lip.main()
            print("NumPy compatibility fixes applied successfully")
        except Exception as e:
            print(f"Error applying NumPy compatibility fixes: {str(e)}")
        
        # Fix path handling issues
        print("Fixing path handling issues...")
        try:
            import fix_wav2lip_paths
            fix_wav2lip_paths.main()
            print("Path handling fixes applied successfully")
        except Exception as e:
            print(f"Error applying path handling fixes: {str(e)}")
    
    print("\nSetup completed!")
    print("You can now use the Wav2Lip model for facial animation.")
    print("\nTo test the Wav2Lip integration, run:")
    print("python test_wav2lip_direct.py")

if __name__ == "__main__":
    main()
