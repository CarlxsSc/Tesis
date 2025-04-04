import os

def fix_numpy_complex_issues(directory):
    """
    Fix NumPy complex type issues in Wav2Lip code
    """
    print(f"Searching for files in {directory}...")
    
    # Walk through all Python files in the directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                print(f"Checking file: {file_path}")
                
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Replace np.complex with np.complex128
                if 'np.complex' in content:
                    print(f"Found np.complex in {file_path}, replacing with np.complex128")
                    modified_content = content.replace('np.complex', 'np.complex128')
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(modified_content)
                    
                    print(f"Fixed {file_path}")
    
    return True

def main():
    """
    Main function to fix NumPy compatibility issues in Wav2Lip
    """
    wav2lip_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wav2lip_repo')
    
    if not os.path.exists(wav2lip_dir):
        print(f"Wav2Lip directory not found at {wav2lip_dir}")
        return False
    
    print(f"Fixing NumPy compatibility issues in {wav2lip_dir}")
    success = fix_numpy_complex_issues(wav2lip_dir)
    
    # Also check librosa installation
    try:
        import librosa
        print(f"Librosa version: {librosa.__version__}")
    except ImportError:
        print("Librosa not installed")
    
    print("Completed fixing NumPy compatibility issues")
    return success

if __name__ == "__main__":
    main()
