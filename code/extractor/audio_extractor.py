
from pydub import AudioSegment
import os

from ..header import workspace, success


def extract_audio(input_path, output_path):
    # Extracting the input and output format
    input_format = os.path.splitext(input_path)[1][1:]
    output_format = os.path.splitext(output_path)[1][1:]

    try:
        # Extract the audio
        audio = AudioSegment.from_file(input_path, input_format)

        # If the WAV file does not exist
        if not os.path.exists(output_path):
            # Export the audio to the WAV file
            audio.export(output_path, format=output_format)

    except (FileNotFoundError, TypeError, OSError) as e:
        print(str(e))
        exit()

    # Return the audio data
    return audio


def extraction_task(ws):
    # Starting the extraction task
    print(f"- Extracting audio from \"{ws.source_file}\"")
    
    # Defining the input and output parameters
    input_path = ws.config["EXTRACTION"]["input_path"]
    output_path = ws.config["EXTRACTION"]["output_path"]

    # Perform the audio extraction from the source file
    extract_audio(input_path, output_path)

    # Task completed
    success(f"- Audio extraction completed for \"{ws.source_file}\"")


if __name__ == "__main__":
    # Define the source file
    source_file = "MRI.mp4"

    # Create the workspace
    ws = workspace(source_file)

    # Perform the audio extraction
    extraction_task(ws)


    