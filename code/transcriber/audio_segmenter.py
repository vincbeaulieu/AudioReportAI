from pydub import AudioSegment
from pydub.silence import split_on_silence
import numpy as np

from ..header import workspace, info

def calculate_dBFS(audio_data):
    # Calculate the root mean square (RMS) of the audio data
    rms = np.sqrt(np.mean(np.square(audio_data)))
    
    # Calculate the amplitude in dBFS
    if rms != 0:
        dBFS = 20 * np.log10(rms / np.iinfo(audio_data.dtype).max)
    else:
        dBFS = -50 # -np.inf
    
    if dBFS < -70:
        dBFS = -70
    elif dBFS > -35:
        dBFS = - 35
    
    print("dBFS: " + str(dBFS))  # ~= -50 dBFS
    return dBFS

# min_silence_len: 1000 for a presentation, 500 for a scripted video
def segment_audio(input_path, combined_audio_path, output_dir):
    # Load the audio file
    audio = AudioSegment.from_wav(input_path)

    # Calculate the silence threshold
    audio_data = np.array(audio.get_array_of_samples())
    noise_baseline_dBFS = calculate_dBFS(audio_data)

    # Set the minimum silence length and silence threshold
    min_silence_len = 1000  # in milliseconds
    silence_thresh = noise_baseline_dBFS + 7 # in dBFS

    # Split the audio file based on silence
    chunks = split_on_silence(audio, 
                              min_silence_len=min_silence_len, 
                              silence_thresh=silence_thresh)

    # Export each chunk as a separate file and create a new combined audio file
    combined_audio = AudioSegment.empty()
    for i, chunk in enumerate(chunks):
        chunk.export(output_dir + f"chunk_{i}.wav", format="wav")
        combined_audio += chunk

    # Export the new audio file, without silent segment
    combined_audio.export(combined_audio_path, format="wav")

    # Return the segmented audio
    return chunks


def segmentation_task(ws):
    # Processing the segmentation
    print(f"- Segmenting audio from {ws.source_file}")
    
    # Defining the input and output path/directory
    input_path = ws.config["TRANSCRIPTION"]["input_path"]
    combined_audio_path = ws.config["TRANSCRIPTION"]["combined_audio_path"]
    segments_dir = ws.config["TRANSCRIPTION"]["segments_dir"]

    # Processing the segmentation
    segment_audio(input_path, combined_audio_path, segments_dir)

    # Task completed
    info(f"- Audio segmentation completed for \"{ws.source_file}\"")


if __name__ == "__main__":
    # Define the source file
    source_file = "MRI.wav"

    # Create the workspace
    ws = workspace(source_file)

    # Processing the segmentation
    segmentation_task(ws)
