
from ..header import workspace, success, error, warning
from .file_handler import file_handler

from pathlib import Path
import shutil

from .text_filters import segment_filter, gratitude_filter, SegmentationType
from .text_formating import combine_short_and_disjointed_paragraphs


def compression_task(ws):
    # Compress the transcript
    print(f"- Compressing transcript of {ws.source_file}")

    # Define the I/O paths
    input_path = ws.config['COMPRESSION']['input_path']
    output_path = ws.config['COMPRESSION']['output_path']
    
    # Define the processing paths
    init_text_path = ws.config['COMPRESSION']['stages_dir'] + 'stage_0-initial_text.txt'
    grat_filt_path = ws.config['COMPRESSION']['stages_dir'] + 'stage_1-gratitude_filtered.txt'
    sent_comp_path = ws.config['COMPRESSION']['stages_dir'] + 'stage_2-sentence_compressed.txt'
    para_comp_path = ws.config['COMPRESSION']['stages_dir'] + 'stage_3-paragraph_compressed.txt'
    comb_text_path = ws.config['COMPRESSION']['stages_dir'] + 'stage_4-combined_text.txt'
    
    # Extract the text
    text = Path(input_path).read_text()

    # Try performing text filtering
    ERROR_FLAG = 0
    try:
        # Copy text file to processing directory (optional)
        text = file_handler(text, None, init_text_path, None)
        #
        # Filters out gratitude sentences
        text = file_handler(text, None, grat_filt_path, gratitude_filter)
        #
        # Light cleaning of non-essential sentences
        text = file_handler(text, None, sent_comp_path, segment_filter, segmentation_type=SegmentationType.SENTENCES)
        #
        # Hard cleaning of non-essential paragraphs
        text = file_handler(text, None, para_comp_path, segment_filter, segmentation_type=SegmentationType.PARAGRAPHS)
        #
        # Repair disjointed sentences and combine short paragraphs to make longer ones
        text = file_handler(text, None, comb_text_path, combine_short_and_disjointed_paragraphs)

    except ValueError as e:
        if len(text) == 0:
            # if transcript is empty, skip filtering and print the error
            ERROR_FLAG = error(f"Transcript file is empty for \"{ws.source_file}\"", type(e).__name__)
        else:
            # if unknown error, raise it
            raise e

    # Save the processed text
    Path(output_path).write_text(text)

    # Task completed
    if not ERROR_FLAG:
        success(f"Compression completed for \"{ws.source_file}\"")
    else:
        warning(f"Compression interruption for \"{ws.source_file}\"")



if __name__ == "__main__":
    # Define the source file
    source_file = "Screen Recording 2023-03-24 at 18.32.35.mov"

    # Create the workspace
    ws = workspace(source_file)

    # Compressing the transcript
    compression_task(ws)

    