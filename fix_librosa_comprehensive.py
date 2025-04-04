import os
import sys
import re
import traceback

def fix_librosa_utils_comprehensive():
    """
    Fix both np.float and np.complex issues in librosa utils.py
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
            content = f.read()
        
        # Replace np.complex with np.complex128
        complex_pattern = r'np\.complex\b'
        content = re.sub(complex_pattern, 'np.complex128', content)
        
        # Write back the file
        with open(utils_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Fixed np.complex references in librosa utils.py")
        
        # Now let's specifically fix the dtype_r2c function
        with open(utils_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find the dtype_r2c function and fix it
        in_dtype_r2c = False
        dtype_r2c_start = -1
        dtype_r2c_end = -1
        
        for i, line in enumerate(lines):
            if 'def dtype_r2c(' in line:
                in_dtype_r2c = True
                dtype_r2c_start = i
            
            if in_dtype_r2c and 'return' in line and '{' in line:
                # This is the mapping dictionary
                mapping_start = i
            
            if in_dtype_r2c and '}' in line and dtype_r2c_start != -1:
                dtype_r2c_end = i
                in_dtype_r2c = False
        
        if dtype_r2c_start != -1 and dtype_r2c_end != -1:
            print(f"Found dtype_r2c function from line {dtype_r2c_start+1} to {dtype_r2c_end+1}")
            
            # Replace the mapping dictionary with a fixed version
            fixed_mapping = [
                "    mapping = {\n",
                "        np.dtype(np.float32): np.complex64,\n",
                "        np.dtype(np.float64): np.complex128,\n",
                "    }\n"
            ]
            
            # Replace the lines
            new_lines = lines[:mapping_start] + fixed_mapping + lines[dtype_r2c_end+1:]
            
            # Write back the file
            with open(utils_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            print("Fixed dtype_r2c function in librosa utils.py")
            return True
        else:
            print("Could not find the dtype_r2c function boundaries")
            
            # Try a direct replacement of the function
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

    return mapping.get(dtype, np.complex128)
'''
            
            # Find the function using regex
            pattern = r'def dtype_r2c\(.*?\):.*?return mapping\.get\(dtype, np\.complex.*?\)'
            
            # Replace using regex with DOTALL flag to match across lines
            modified_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            
            if content != modified_content:
                with open(utils_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                print("Successfully replaced entire dtype_r2c function in librosa utils.py")
                return True
            else:
                print("Failed to find and replace the dtype_r2c function")
                
                # Last resort: manually edit the file
                print("Attempting manual edit...")
                try:
                    # Create a backup of the original file
                    backup_path = utils_path + '.bak'
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Created backup at {backup_path}")
                    
                    # Direct modification using file path
                    with open(utils_path, 'w', encoding='utf-8') as f:
                        # Replace the problematic line with a fixed version
                        fixed_content = content.replace(
                            "np.dtype(np.float64): np.complex,", 
                            "np.dtype(np.float64): np.complex128,"
                        )
                        f.write(fixed_content)
                    
                    print("Manually fixed the problematic line")
                    return True
                except Exception as e:
                    print(f"Error during manual edit: {str(e)}")
                    traceback.print_exc()
                    
                    # Restore from backup if available
                    if os.path.exists(backup_path):
                        with open(backup_path, 'r', encoding='utf-8') as f:
                            original = f.read()
                        with open(utils_path, 'w', encoding='utf-8') as f:
                            f.write(original)
                        print("Restored from backup")
                    
                    return False
            
    except Exception as e:
        print(f"Error fixing librosa utils: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """
    Main function to fix numpy complex and float issues in librosa
    """
    print("Fixing NumPy complex and float issues in librosa utils.py...")
    success = fix_librosa_utils_comprehensive()
    
    if success:
        print("Successfully fixed NumPy issues in librosa.")
    else:
        print("Failed to fix NumPy issues in librosa.")

if __name__ == "__main__":
    main()
