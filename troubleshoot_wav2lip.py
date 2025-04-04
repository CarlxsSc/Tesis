import os
import sys
import subprocess
import shutil
import platform
import traceback

def check_file_exists(file_path, description):
    """Check if a file exists and print the result"""
    exists = os.path.exists(file_path)
    print(f"[{'OK' if exists else 'MISSING'}] {description}: {'Found' if exists else 'Not found'} at {file_path}")
    return exists

def check_directory_exists(dir_path, description):
    """Check if a directory exists and print the result"""
    exists = os.path.isdir(dir_path)
    print(f"[{'OK' if exists else 'MISSING'}] {description}: {'Found' if exists else 'Not found'} at {dir_path}")
    return exists

def check_ffmpeg():
    """Check if ffmpeg is available and print the version"""
    try:
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        print(f"[OK] FFmpeg: Found at {ffmpeg_exe}")
        
        # Try to run ffmpeg to get version
        try:
            result = subprocess.run([ffmpeg_exe, "-version"], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   text=True,
                                   timeout=5)
            version_line = result.stdout.split('\n')[0]
            print(f"  FFmpeg version: {version_line}")
            return True
        except Exception as e:
            print(f"  Warning: FFmpeg found but could not get version: {str(e)}")
            return True
    except Exception as e:
        print(f"[ERROR] FFmpeg: Not found - {str(e)}")
        return False

def check_numpy_complex():
    """Check if NumPy complex type is properly defined"""
    try:
        import numpy as np
        try:
            # Try to create a complex number using np.complex128
            c = np.complex128(1 + 2j)
            print(f"[OK] NumPy complex: Using np.complex128 successfully")
            return True
        except Exception as e:
            print(f"[ERROR] NumPy complex: Error with np.complex128 - {str(e)}")
            
            # Check if np.complex is available (deprecated)
            try:
                c = np.complex(1 + 2j)
                print(f"  Warning: Using deprecated np.complex")
                print(f"  Run fix_wav2lip.py to update to np.complex128")
                return False
            except:
                print(f"[ERROR] NumPy complex: Both np.complex128 and np.complex failed")
                return False
    except ImportError:
        print(f"[ERROR] NumPy: Not installed")
        return False

def check_librosa():
    """Check if librosa is installed and working"""
    try:
        import librosa
        print(f"[OK] Librosa: Installed (version {librosa.__version__})")
        
        # Try to load a simple audio file
        try:
            # Create a simple test audio file
            test_audio = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_audio.wav")
            if not os.path.exists(test_audio):
                # Use ffmpeg to create a simple test audio file
                import imageio_ffmpeg
                ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
                cmd = f'"{ffmpeg_exe}" -f lavfi -i sine=frequency=1000:duration=1 -c:a pcm_s16le "{test_audio}"'
                subprocess.run(cmd, shell=True, check=True)
            
            # Try to load it with librosa
            audio, sr = librosa.load(test_audio, sr=16000)
            print(f"  Librosa audio loading: Working")
            
            # Clean up test file
            if os.path.exists(test_audio):
                os.remove(test_audio)
                
            return True
        except Exception as e:
            print(f"  Warning: Librosa installed but audio loading failed: {str(e)}")
            print(f"  Run fix_wav2lip.py to fix compatibility issues")
            return False
    except ImportError:
        print(f"[ERROR] Librosa: Not installed")
        return False

def check_wav2lip_setup():
    """Check if Wav2Lip is properly set up"""
    print("\nChecking Wav2Lip setup...")
    
    # Check for Wav2Lip repository
    wav2lip_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wav2lip_repo")
    repo_exists = check_directory_exists(wav2lip_dir, "Wav2Lip repository")
    
    # Check for model file
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                             "wav2lip_model", "checkpoints", "wav2lip_gan.pth")
    model_exists = check_file_exists(model_path, "Wav2Lip model")
    
    # Check for inference script
    inference_path = os.path.join(wav2lip_dir, "inference.py")
    inference_exists = check_file_exists(inference_path, "Inference script")
    
    # Check for temp directory
    temp_dir = os.path.join(wav2lip_dir, "temp")
    if not os.path.exists(temp_dir):
        print(f"[MISSING] Temp directory: Not found at {temp_dir}")
        print(f"  Creating temp directory...")
        try:
            os.makedirs(temp_dir, exist_ok=True)
            print(f"[OK] Temp directory: Created at {temp_dir}")
        except Exception as e:
            print(f"[ERROR] Failed to create temp directory: {str(e)}")
    else:
        print(f"[OK] Temp directory: Found at {temp_dir}")
    
    return repo_exists and model_exists and inference_exists

def check_environment():
    """Check the environment for Wav2Lip dependencies"""
    print("\nChecking environment...")
    
    # Check Python version
    python_version = platform.python_version()
    print(f"[INFO] Python version: {python_version}")
    
    # Check operating system
    os_name = platform.system()
    print(f"[INFO] Operating system: {os_name}")
    
    # Check for FFmpeg
    ffmpeg_ok = check_ffmpeg()
    
    # Check for NumPy complex
    numpy_ok = check_numpy_complex()
    
    # Check for Librosa
    librosa_ok = check_librosa()
    
    return ffmpeg_ok and numpy_ok and librosa_ok

def main():
    """Main function to troubleshoot Wav2Lip setup"""
    print("Wav2Lip Troubleshooting Tool")
    print("============================")
    
    # Check environment
    env_ok = check_environment()
    
    # Check Wav2Lip setup
    setup_ok = check_wav2lip_setup()
    
    # Print summary
    print("\nTroubleshooting Summary")
    print("======================")
    print(f"Environment check: {'PASSED' if env_ok else 'FAILED'}")
    print(f"Wav2Lip setup check: {'PASSED' if setup_ok else 'FAILED'}")
    
    if not env_ok or not setup_ok:
        print("\nRecommended actions:")
        if not env_ok:
            print("1. Run 'pip install -r requirements.txt' to install dependencies")
            print("2. Run 'python fix_wav2lip.py' to fix NumPy compatibility issues")
        if not setup_ok:
            print("3. Run 'python setup_wav2lip.py' to set up Wav2Lip properly")
        print("4. Run 'python fix_wav2lip_paths.py' to fix path handling issues")
    else:
        print("\nAll checks passed! Wav2Lip should be working correctly.")
        print("To test the integration, run 'python test_wav2lip_direct.py'")

if __name__ == "__main__":
    main()
