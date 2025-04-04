import os
import sys
import re
import glob
import traceback

def fix_numpy_float_in_file(file_path):
    """
    Replace np.float with np.float64 in the given file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace np.float with np.float64
        pattern = r'np\.float\b'
        replacement = 'np.float64'
        modified_content = re.sub(pattern, replacement, content)
        
        # Write the modified content back to the file
        if content != modified_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            print(f"Fixed np.float in {file_path}")
            return True
        else:
            print(f"No np.float found in {file_path}")
            return False
    except Exception as e:
        print(f"Error fixing {file_path}: {str(e)}")
        traceback.print_exc()
        return False

def fix_librosa_utils():
    """
    Fix the np.float issue in librosa utils.py
    """
    try:
        # Find the librosa utils.py file
        import librosa
        librosa_path = os.path.dirname(librosa.__file__)
        utils_path = os.path.join(librosa_path, 'util', 'utils.py')
        
        if os.path.exists(utils_path):
            print(f"Found librosa utils.py at {utils_path}")
            fixed = fix_numpy_float_in_file(utils_path)
            return fixed
        else:
            print(f"Could not find librosa utils.py at {utils_path}")
            
            # Try to find it using glob
            potential_paths = glob.glob(os.path.join(sys.prefix, "**", "librosa", "util", "utils.py"), recursive=True)
            if potential_paths:
                for path in potential_paths:
                    print(f"Found alternative path: {path}")
                    fixed = fix_numpy_float_in_file(path)
                    if fixed:
                        return True
            
            print("Could not find librosa utils.py. Please install librosa first.")
            return False
    except ImportError:
        print("Librosa is not installed. Please install it first.")
        return False
    except Exception as e:
        print(f"Error fixing librosa utils: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """
    Main function to fix numpy float issues in librosa
    """
    print("Fixing NumPy float issues in librosa...")
    success = fix_librosa_utils()
    
    if success:
        print("Successfully fixed NumPy float issues in librosa.")
    else:
        print("Failed to fix NumPy float issues in librosa.")

if __name__ == "__main__":
    main()
