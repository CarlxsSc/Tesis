import os
import sys
import re

def fix_librosa_numpy_complex():
    """
    Fix NumPy complex type issues in librosa library with precise replacement
    """
    try:
        # Path to the constantq.py file
        constantq_path = r"C:\Users\Killtro\AppData\Local\Programs\Python\Python311\Lib\site-packages\librosa\core\constantq.py"
        
        print(f"Fixing file: {constantq_path}")
        
        if not os.path.exists(constantq_path):
            print(f"Error: constantq.py not found at {constantq_path}")
            return False
        
        # Read the file
        with open(constantq_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Create a backup
        backup_path = constantq_path + '.bak2'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created backup at {backup_path}")
        
        # Use regex to precisely replace np.complex with np.complex128
        # This avoids creating np.complex128128
        if 'np.complex128128' in content:
            print("Found np.complex128128 in constantq.py, fixing it")
            modified_content = content.replace('np.complex128128', 'np.complex128')
            
            # Write the modified file
            with open(constantq_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            print(f"Fixed {constantq_path}")
            return True
        else:
            print("No np.complex128128 found in constantq.py")
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
        import sys
        if 'librosa' in sys.modules:
            del sys.modules['librosa']
        import librosa
        print("Librosa import successful after fix")
    except Exception as e:
        print(f"Librosa import still failing: {str(e)}")
