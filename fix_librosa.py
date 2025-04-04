import os
import sys
import re

def fix_librosa_numpy_complex():
    """
    Fix NumPy complex type issues in librosa library
    """
    try:
        import librosa
        import numpy as np
        
        # Find the constantq.py file path
        librosa_path = os.path.dirname(librosa.__file__)
        constantq_path = os.path.join(librosa_path, 'core', 'constantq.py')
        
        print(f"Librosa version: {librosa.__version__}")
        print(f"NumPy version: {np.__version__}")
        print(f"Fixing file: {constantq_path}")
        
        if not os.path.exists(constantq_path):
            print(f"Error: constantq.py not found at {constantq_path}")
            return False
        
        # Read the file
        with open(constantq_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Replace np.complex with np.complex128
        if 'np.complex' in content:
            print("Found np.complex in constantq.py, replacing with np.complex128")
            modified_content = content.replace('np.complex', 'np.complex128')
            
            # Create a backup
            backup_path = constantq_path + '.bak'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Created backup at {backup_path}")
            
            # Write the modified file
            with open(constantq_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            print(f"Fixed {constantq_path}")
            return True
        else:
            print("No np.complex found in constantq.py")
            return False
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Fixing NumPy compatibility issues in librosa...")
    success = fix_librosa_numpy_complex()
    
    if success:
        print("Successfully fixed librosa NumPy compatibility issues")
    else:
        print("Failed to fix librosa NumPy compatibility issues")
        
    # Try importing librosa again to verify fix
    try:
        import importlib
        import librosa
        importlib.reload(librosa)
        print("Librosa import successful after fix")
    except Exception as e:
        print(f"Librosa import still failing: {str(e)}")
