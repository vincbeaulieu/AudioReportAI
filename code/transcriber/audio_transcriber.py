
import os
import numpy as np
import whisper
from glob import glob
from concurrent.futures import ThreadPoolExecutor

from ..header import workspace, success, Specs

class Parameters:
    OVERWRITE = True
    NUM_WORKERS = Specs.NUM_LOGICAL_CPU

    # Define the model parameters
    whisper_parameters = {
        "model_name" : "base",
        "language" : "english",
    }

# Process used to transcribe a batch of audio captions
def transcribe_batch(segments_dir, models_dir, captions_dir, output_path):


    # TODO: Implement a progression bar.
    # TODO: If transcript already exist, suggest the user to skip this step with a prompt.
    
    segments_path = glob(f"{segments_dir}/chunk_*.wav")
    indexes = range(len(segments_path))  
    models_dir = [f"{models_dir}{index}/" for index in indexes]
    captions_path = [f"{captions_dir}{index}.txt" for index in indexes]
    
    transcript = [None] * len(indexes)
    for index in indexes:
        args = index, segments_path[index], models_dir[index], captions_path[index]
        ind, cap = transcribe_audio(args)
        transcript[ind] = cap

    # Merge the transcript into a single string
    transcript = "\n\n".join(transcript).replace("\n ", "\n")
    
    # Generate the transcript
    with open(output_path, "w") as f:
        f.writelines(transcript)

    # Return the transcript
    return transcript


# Process used to transcribe an audio file
def transcribe_audio(args):
    # Unpack arguments
    index, segment_path, model_dir, caption_path = args

    # Create the directory
    os.makedirs(model_dir, exist_ok=True)

    # Fetch the model parameters
    model_name = Parameters.whisper_parameters["model_name"]
    model_language = Parameters.whisper_parameters["language"]

    # Define the model path
    model_path = f"{model_dir}{model_name}.npy"

    # if model does not exist
    if not os.path.isfile(model_path) or Parameters.OVERWRITE:
        # Load model, transcribe audio, and save the model
        model = whisper.load_model(model_name)
        result = model.transcribe(segment_path, fp16=False, language=model_language)
        np.save(model_path, np.array(list(result.items()), dtype=object))
    else:
        # Load the result
        result = dict(np.load(model_path, allow_pickle=True))

    # Extract the caption from the result (see NOTE at EOF)
    text = result["text"][1:]

    # Save the transcript to a ".txt" file
    with open(caption_path, "w") as f:
        for i in text:
            f.writelines(i)
    
    # Return the index, and the transcript
    return index, text


def transcription_task(ws):
    # Transcribing the data
    print(f"- Transcribing from \"{ws.source_file}\"")
    
    # Defining the paths and directories
    segments_dir = ws.config["TRANSCRIPTION"]["segments_dir"]
    models_dir = ws.config["TRANSCRIPTION"]["models_dir"] + "whisper/"
    captions_dir = ws.config["TRANSCRIPTION"]["captions_dir"]
    output_path = ws.config["TRANSCRIPTION"]["output_path"]

    # Process the batch of audio segment into captions and transcript
    transcribe_batch(segments_dir, models_dir, captions_dir, output_path)

    # TODO: Implement a progress bar
    # TODO: if transcript exist, suggest user to skip this step with a prompt. (WARNING)
    
    # Task completed
    success(f"- Transcription completed for \"{ws.source_file}\"")


if __name__ == "__main__":
    # Define the source file
    source_file = "lab 4 part 2.wav"

    # Create the workspace
    ws = workspace(source_file)

    # Transcribing the data
    transcription_task(ws)


"""
Notes:
We need to remove the first white space [1:].
This is to alleviate a bug with "whisper", which is returning a white space at the beginning of each translation.
This may be resolved in the future, in which case, the [1:] shall be removed.

whisper version:
    openai-whisper==20230308

-- Vincent Beaulieu (14/03/2022) --
"""

