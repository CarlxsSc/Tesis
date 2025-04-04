import os
import re
import shutil
import sys
import traceback

def fix_wav2lip_inference_script():
    """
    Fix path handling in the Wav2Lip inference script
    """
    wav2lip_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wav2lip_repo')
    inference_path = os.path.join(wav2lip_dir, 'inference.py')
    
    if not os.path.exists(inference_path):
        print(f"Wav2Lip inference script not found at {inference_path}")
        return False
    
    # Create a backup
    backup_path = inference_path + '.bak'
    shutil.copy2(inference_path, backup_path)
    print(f"Created backup at {backup_path}")
    
    # Read the inference script
    with open(inference_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Fix 1: Fix indentation in the main function
    main_pattern = r"def main\(\):"
    if main_pattern in content:
        # Get the first few lines of the main function
        main_start_pos = content.find("def main():")
        next_line_pos = content.find("\n", main_start_pos) + 1
        
        # Insert directory creation at the beginning of the main function with proper indentation
        temp_dir_creation = "\n\t# Create temp directory if it doesn't exist\n\tos.makedirs('temp', exist_ok=True)\n\tos.makedirs(os.path.dirname(args.outfile), exist_ok=True)\n"
        content = content[:next_line_pos] + temp_dir_creation + content[next_line_pos:]
    
    # Fix 2: Update the ffmpeg command for audio extraction
    audio_extraction_pattern = r"if not args\.audio\.endswith\('\.wav'\):"
    if audio_extraction_pattern in content:
        # Find the position of the audio extraction code
        audio_pos = content.find("if not args.audio.endswith('.wav'):")
        next_line_pos = content.find("\n", audio_pos) + 1
        
        # Replace the audio extraction code with improved version
        improved_audio_extraction = """
	if not args.audio.endswith('.wav'):
		print('Extracting raw audio...')
		# Create absolute path for temp.wav
		temp_wav = os.path.abspath(os.path.join('temp', 'temp.wav'))
		print(f"Creating temp wav file at: {temp_wav}")
		
		# Use the full ffmpeg path from imageio
		import imageio_ffmpeg
		ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
		
		command = f'"{ffmpeg_exe}" -y -i "{args.audio}" -strict -2 "{temp_wav}"'
		print(f"Running command: {command}")
		
		subprocess.call(command, shell=True)
		args.audio = temp_wav
"""
        # Find the end of the audio extraction block
        end_audio_pos = content.find("wav = audio.load_wav(args.audio, 16000)")
        content = content[:audio_pos] + improved_audio_extraction + content[end_audio_pos:]
    
    # Fix 3: Update the final ffmpeg command for video generation
    final_ffmpeg_pattern = r"command = 'ffmpeg -y -i {} -i {} -strict -2 -q:v 1 {}'\.format\(args\.audio, 'temp/result\.avi', args\.outfile\)"
    if re.search(final_ffmpeg_pattern, content):
        # Replace the final ffmpeg command with improved version
        improved_final_ffmpeg = """
	# Use the full ffmpeg path from imageio
	import imageio_ffmpeg
	ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
	
	print(f"Creating final output video at: {args.outfile}")
	command = f'"{ffmpeg_exe}" -y -i "{args.audio}" -i "temp/result.avi" -strict -2 -q:v 1 "{args.outfile}"'
	print(f"Running command: {command}")
	
	subprocess.call(command, shell=True)
"""
        content = re.sub(r"command = 'ffmpeg.*?subprocess\.call\(command, shell=.*?\)", improved_final_ffmpeg, content, flags=re.DOTALL)
    
    # Write the modified content back
    with open(inference_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated {inference_path} with path fixes")
    return True

def fix_wav2lip_audio_script():
    """
    Fix audio handling in the Wav2Lip audio script
    """
    wav2lip_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wav2lip_repo')
    audio_path = os.path.join(wav2lip_dir, 'audio.py')
    
    if not os.path.exists(audio_path):
        print(f"Wav2Lip audio script not found at {audio_path}")
        return False
    
    # Create a backup
    backup_path = audio_path + '.bak'
    shutil.copy2(audio_path, backup_path)
    print(f"Created backup at {backup_path}")
    
    # Read the audio script
    with open(audio_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Fix: Improve audio loading with better error handling
    improved_load_wav = """
def load_wav(path, sr):
    try:
        # First try with librosa
        return librosa.core.load(path, sr=sr)[0]
    except Exception as e:
        print(f"Error loading audio with librosa: {str(e)}")
        try:
            # Try with soundfile directly
            import soundfile as sf
            data, samplerate = sf.read(path)
            if samplerate != sr:
                import resampy
                data = resampy.resample(data, samplerate, sr)
            return data
        except Exception as e2:
            print(f"Error loading audio with soundfile: {str(e2)}")
            # Last resort: try with scipy
            try:
                from scipy.io import wavfile
                samplerate, data = wavfile.read(path)
                if samplerate != sr:
                    import resampy
                    data = resampy.resample(data, samplerate, sr)
                return data
            except Exception as e3:
                print(f"All audio loading methods failed. Last error: {str(e3)}")
                raise
"""
    
    # Replace the load_wav function
    load_wav_pattern = r"def load_wav\(path, sr\):.*?return librosa\.core\.load\(path, sr=sr\)\[0\]"
    if re.search(load_wav_pattern, content, re.DOTALL):
        content = re.sub(load_wav_pattern, improved_load_wav, content, flags=re.DOTALL)
    else:
        # If we can't find the exact pattern, look for any load_wav function
        load_wav_pattern = r"def load_wav\(path, sr\):.*?(?=def |$)"
        if re.search(load_wav_pattern, content, re.DOTALL):
            content = re.sub(load_wav_pattern, improved_load_wav, content, flags=re.DOTALL)
    
    # Write the modified content back
    with open(audio_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated {audio_path} with better error handling")
    return True

def main():
    """
    Main function to fix Wav2Lip path handling
    """
    print("Fixing Wav2Lip path handling...")
    
    # Fix inference script
    inference_success = fix_wav2lip_inference_script()
    
    # Fix audio script
    audio_success = fix_wav2lip_audio_script()
    
    if inference_success and audio_success:
        print("Successfully fixed Wav2Lip path handling!")
        return True
    else:
        print("Failed to fix Wav2Lip path handling!")
        return False

if __name__ == "__main__":
    main()
