import os
import sys
import subprocess

def find_librosa_constantq():
    """Find the librosa constantq.py file path"""
    try:
        # Run a command to get the site-packages directory
        result = subprocess.run(
            [sys.executable, "-c", "import site; print(site.getsitepackages()[0])"],
            capture_output=True,
            text=True,
            check=True
        )
        site_packages = result.stdout.strip()
        
        # Construct the path to librosa constantq.py
        librosa_path = os.path.join(site_packages, 'librosa')
        constantq_path = os.path.join(librosa_path, 'core', 'constantq.py')
        
        if os.path.exists(constantq_path):
            return constantq_path
        else:
            print(f"constantq.py not found at {constantq_path}")
            
            # Try to find it using a more general approach
            for root, dirs, files in os.walk(site_packages):
                if 'constantq.py' in files and 'librosa' in root:
                    path = os.path.join(root, 'constantq.py')
                    print(f"Found constantq.py at: {path}")
                    return path
            
            return None
    except Exception as e:
        print(f"Error finding librosa constantq.py: {str(e)}")
        return None

def fix_librosa_numpy_complex(constantq_path):
    """Fix NumPy complex type issues in librosa constantq.py"""
    try:
        print(f"Fixing file: {constantq_path}")
        
        # Read the file
        with open(constantq_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Create a backup
        backup_path = constantq_path + '.bak'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created backup at {backup_path}")
        
        # Replace np.complex with np.complex128
        if 'np.complex' in content:
            print("Found np.complex in constantq.py, replacing with np.complex128")
            modified_content = content.replace('np.complex', 'np.complex128')
            
            # Write the modified file
            with open(constantq_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            print(f"Fixed {constantq_path}")
            return True
        else:
            print("No np.complex found in constantq.py")
            return False
    
    except Exception as e:
        print(f"Error fixing constantq.py: {str(e)}")
        return False

def find_librosa_utils():
    """Find the librosa utils.py file path"""
    try:
        # Run a command to get the site-packages directory
        result = subprocess.run(
            [sys.executable, "-c", "import site; print(site.getsitepackages()[0])"],
            capture_output=True,
            text=True,
            check=True
        )
        site_packages = result.stdout.strip()
        
        # Construct the path to librosa utils.py
        librosa_path = os.path.join(site_packages, 'librosa')
        utils_path = os.path.join(librosa_path, 'util', 'utils.py')
        
        if os.path.exists(utils_path):
            return utils_path
        else:
            print(f"utils.py not found at {utils_path}")
            
            # Try to find it using a more general approach
            for root, dirs, files in os.walk(site_packages):
                if 'utils.py' in files and 'librosa' in root and 'util' in root:
                    path = os.path.join(root, 'utils.py')
                    print(f"Found utils.py at: {path}")
                    return path
            
            return None
    except Exception as e:
        print(f"Error finding librosa utils.py: {str(e)}")
        return None

def fix_librosa_utils_numpy_complex(utils_path):
    """Fix NumPy complex type issues in librosa utils.py"""
    try:
        print(f"Fixing file: {utils_path}")
        
        # Read the file
        with open(utils_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Create a backup
        backup_path = utils_path + '.bak'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created backup at {backup_path}")
        
        # Replace np.complex with np.complex128
        modified_content = content.replace('np.complex,', 'np.complex128,')
        
        # Check if any changes were made
        if modified_content != content:
            # Write the modified content back to the file
            with open(utils_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            print("Successfully fixed np.complex in utils.py")
            return True
        else:
            print("No instances of 'np.complex,' found in utils.py")
            return False
    except Exception as e:
        print(f"Error fixing utils.py: {str(e)}")
        return False

if __name__ == "__main__":
    print("Finding and fixing NumPy compatibility issues in librosa...")
    
    constantq_path = find_librosa_constantq()
    if constantq_path:
        fixed_constantq = fix_librosa_numpy_complex(constantq_path)
        if fixed_constantq:
            print("Successfully fixed NumPy complex issues in librosa constantq.py")
        else:
            print("Failed to fix NumPy complex issues in librosa constantq.py")
    else:
        print("Could not find librosa constantq.py")
    
    utils_path = find_librosa_utils()
    if utils_path:
        fixed_utils = fix_librosa_utils_numpy_complex(utils_path)
        if fixed_utils:
            print("Successfully fixed NumPy complex issues in librosa utils.py")
        else:
            print("Failed to fix NumPy complex issues in librosa utils.py")
    else:
        print("Could not find librosa utils.py")
