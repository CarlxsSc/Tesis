import os
import sys
import re
import traceback

def fix_librosa_utils_specific():
    """
    Fix the np.float issue in librosa utils.py specifically for the dtype_r2c function
    """
    try:
        # Find the librosa utils.py file
        import librosa
        librosa_path = os.path.dirname(librosa.__file__)
        utils_path = os.path.join(librosa_path, 'util', 'utils.py')
        
        if not os.path.exists(utils_path):
            print(f"Could not find librosa utils.py at {utils_path}")
            return False
            
        print(f"Found librosa utils.py at {utils_path}")
        
        # Read the file
        with open(utils_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find and fix the dtype_r2c function
        in_dtype_r2c = False
        fixed = False
        for i, line in enumerate(lines):
            if 'def dtype_r2c(' in line:
                in_dtype_r2c = True
                print(f"Found dtype_r2c function at line {i+1}")
            
            if in_dtype_r2c and 'np.float' in line:
                # This is the line we need to fix
                print(f"Found np.float at line {i+1}: {line.strip()}")
                lines[i] = line.replace('np.float', 'np.float64')
                print(f"Fixed to: {lines[i].strip()}")
                fixed = True
            
            if in_dtype_r2c and 'return' in line:
                in_dtype_r2c = False
        
        if fixed:
            # Write the fixed content back
            with open(utils_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print("Successfully fixed dtype_r2c function in librosa utils.py")
            return True
        else:
            print("Could not find np.float in dtype_r2c function")
            
            # Let's try to manually patch the function
            with open(utils_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Define the pattern to search for
            pattern = r'def dtype_r2c\(.*?\):\s+.*?return\s+{[^}]*?np\.float[^}]*?}'
            
            # Define the replacement
            replacement = '''def dtype_r2c(dtype):
    """Convert real dtype to complex dtype

    Parameters
    ----------
    dtype : np.dtype
        The real dtype to convert

    Returns
    -------
    np.dtype
        The complex dtype
    """
    mapping = {
        np.dtype(np.float32): np.complex64,
        np.dtype(np.float64): np.complex128,
    }

    dtype = np.dtype(dtype)

    if dtype.kind == 'c':
        return dtype

    return mapping.get(dtype, np.complex128)'''
            
            # Replace using regex with DOTALL flag to match across lines
            modified_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            
            if content != modified_content:
                with open(utils_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                print("Successfully replaced entire dtype_r2c function in librosa utils.py")
                return True
            else:
                print("Failed to find and replace the dtype_r2c function")
                return False
            
    except Exception as e:
        print(f"Error fixing librosa utils: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """
    Main function to fix numpy float issues in librosa
    """
    print("Fixing NumPy float issues in librosa utils.py...")
    success = fix_librosa_utils_specific()
    
    if success:
        print("Successfully fixed NumPy float issues in librosa.")
    else:
        print("Failed to fix NumPy float issues in librosa.")

if __name__ == "__main__":
    main()
