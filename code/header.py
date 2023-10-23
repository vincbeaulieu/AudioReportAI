import os
import shutil
import psutil

# Some print formats:
def warning(input_str):  # Yellow
    print(f"\033[33m[WARNING] {input_str}\033[0m")

def success(input_str):  # Green
    print(f"\033[32m[SUCCESS] {input_str}\033[0m")

def info(input_str):  # Cyan
    print(f"\033[36m[INFO] {input_str}\033[0m")

def error(input_str, error_type):  # Red
    print(f"\033[91m[{error_type}] {input_str}\033[0m")
    return 1

input_dir = "input"

class Specs:
    # Calculate the numbers of threads per cpu
    NUM_PHYSICAL_CPU = psutil.cpu_count(logical=False)  # 8
    NUM_LOGICAL_CPU = psutil.cpu_count(logical=True)  # 16
    NUM_THREAD_PER_CPU = int(NUM_LOGICAL_CPU / NUM_PHYSICAL_CPU)  # 2


class Header:
    def __init__(self, source_file):
        # Obtaining the file name
        self.source_file = source_file
        source_name = os.path.splitext(source_file)[0]

        # Define the main output directory
        work_dir = f"work/{source_name}"
        # code_dir = "code/"

        # Look if there is already and existing one, rename if needed
        i = 2
        while os.path.exists(work_dir):
            work_dir = f"work/{source_name} {i}"
            i += 1

        # Define the other directories and paths
        process_dir  = f"{work_dir}/.process"
        input_path   = f"{input_dir}/{source_file}"
        self.source_path  = f"{work_dir}/{source_file}"

        self.config = {
            'WORKSPACE': {
                'work_dir': f'{work_dir}/',
                'process_dir': f'{process_dir}/',
                'input_path': input_path,
                'source_path': self.source_path,
            },
            'EXTRACTION': {
                # I/O paths
                'input_path' : self.source_path,
                'output_path' : f'{work_dir}/{source_name}.wav',
                'normalised_path' : f'{work_dir}/normalised.wav',
                'vocal_path' : f'{work_dir}/vocal.wav',
            },
            'DIARIZATION': {
                # I/O paths
                'input_path' : f'{work_dir}/{source_name}.wav',
                'output_path' : f'{work_dir}/transcript.txt',
            },
            'SEGMENTATION': {
                # Processing directories
                'audio_jobs_dir' : f'{process_dir}/transcriber/jobs/',
            },
            'TRANSCRIPTION': {
                # I/O paths
                'input_path' : f'{work_dir}/{source_name}.wav',
                'combined_audio_path' : f'{work_dir}/chunks.wav',
                'output_path' : f'{work_dir}/transcript.txt',
                
                # Processing directories
                'segments_dir' : f'{process_dir}/transcriber/segments/',
                'models_dir' : f'{process_dir}/transcriber/models/',
                'captions_dir' : f'{process_dir}/transcriber/captions/',
            },
            'COMPRESSION': {
                # I/O paths
                'input_path': f'{work_dir}/transcript.txt',
                'output_path': f'{work_dir}/compressed.txt',

                # Code directory
                # 'useless_sentences': f'{code_dir}/compressor/useless_sentences.txt',

                # Processing directories
                'stages_dir' : f'{process_dir}/compressor/stages/',
            },
            'SUMMARIZATION': {
                # I/O paths
                'input_path': f'{work_dir}/compressed.txt',
                'output_path': f'{work_dir}/summary.txt',
            },
        }

    # Creating the workspace
    def build_workspace(self):
        # If directory already exist, prompt to overwrite
        if os.path.exists(self.config['WORKSPACE']['work_dir']):
            overwrite = input(f"The path already exist for \"{self.source_file}\" - Do you want to overwrite it? (y/n): ")
            if overwrite.lower().startswith("y"):
                shutil.rmtree(self.config['WORKSPACE']['work_dir'])
            # TODO: else change the name of the source file by appending a number (1...inf)
            else: 
                if os.path.exists(source_path):
                    i = 1
                    new_name = source_path
                    base, ext = os.path.splitext(new_name)
                    while os.path.isfile(new_name):
                        new_name = f"{base} {i}{ext}"
                        i += 1
                    os.rename(source_path, new_name)
                    print(f"The file '{source_path}' has been renamed to '{new_name}'.")
                else:
                    print(f"The file '{source_path}' does not exist.")
                    exit()

        # Creating the directories
        for section in self.config:
            for key, value in self.config[section].items():
                if key.endswith("_dir"):
                    os.makedirs(value, exist_ok=True)

        # Copy the original file in the workspace
        try:
            input_path = self.config['WORKSPACE']['input_path']
            source_path = self.config['WORKSPACE']['source_path']
            shutil.copy2(input_path, source_path)
        except (FileNotFoundError, shutil.Error) as e:
            print(str(e))


    def cleanup(self):
        # Remove the original file after processing is completed
        os.remove(self.config['WORKSPACE']['input_path'])


def workspace(source_file, build=True):
    # Initialize the workspace
    header = Header(source_file)

    # Build the workspace if build is true
    if build:
        header.build_workspace()

    # Return the workspace
    return header


if __name__ == "__main__":
    # Define the source file
    source_file = "MRI.mp4"

    # Create the workspace
    ws = workspace(source_file)

    # Print the directories for testing 
    from pprint import pprint
    pprint(ws.config)


