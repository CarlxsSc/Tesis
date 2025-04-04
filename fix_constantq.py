import os
import re

# Path to the constantq.py file
constantq_path = r"C:\Users\Killtro\AppData\Local\Programs\Python\Python311\Lib\site-packages\librosa\core\constantq.py"

print(f"Fixing file: {constantq_path}")

# Read the file
with open(constantq_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Create a backup
backup_path = constantq_path + '.original'
if not os.path.exists(backup_path):
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created backup at {backup_path}")

# First fix any invalid complex128128128 patterns
invalid_pattern = r'np\.complex\d{6,}'
if re.search(invalid_pattern, content):
    print("Found invalid np.complex pattern (e.g., np.complex128128128), fixing...")
    content = re.sub(invalid_pattern, 'np.complex128', content)

# Now fix any remaining np.complex patterns
pattern = r'np\.complex(?!128)(\b|,|\))'
replacement = r'np.complex128\1'

if re.search(pattern, content):
    print("Found np.complex in constantq.py, replacing with np.complex128")
    modified_content = re.sub(pattern, replacement, content)
    
    # Write the modified file
    with open(constantq_path, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print(f"Fixed {constantq_path}")
else:
    # Still write the content in case we fixed invalid patterns
    with open(constantq_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("No additional np.complex patterns found to fix")

# Verify the fix
with open(constantq_path, 'r', encoding='utf-8', errors='ignore') as f:
    new_content = f.read()

if 'np.complex128128' in new_content or 'np.complex128128128' in new_content:
    print("WARNING: Still found invalid complex patterns in the file")
elif 'np.complex128' in new_content:
    print("Verification successful: np.complex128 found in the file")
else:
    print("Verification failed: np.complex128 not found in the file")
