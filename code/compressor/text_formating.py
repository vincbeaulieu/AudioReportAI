
from ..header import workspace
from .file_handler import file_handler


CLOSING_PUNCTUATION = {'.', '!', '?'}


def combine_short_and_disjointed_paragraphs(text, min_length=500, use_closing_punctuation=True):
    # Split the input text into paragraphs
    paragraphs = text.split('\n\n')
    combined_paragraphs = []
    buffer = ""

    # Iterate through each paragraph in the input text
    for paragraph in paragraphs:
        paragraph = paragraph.strip()

        # Combine the current paragraph with the previous one in the buffer, if any, then clear the buffer
        if buffer:
            paragraph = buffer + ' ' + paragraph
            buffer = ""

        # Check if missing punctuation
        missing_closing_punctuation = (use_closing_punctuation and paragraph[-1] not in CLOSING_PUNCTUATION)
        
        # If paragraph length is less than min_length or missing closing punctuation, store in buffer
        if len(paragraph) < min_length or missing_closing_punctuation:
            buffer = paragraph
            continue

        # Append the combined paragraph to the result list
        combined_paragraphs.append(paragraph)

    # If there's a paragraph remaining in the buffer, append it to the result list
    if buffer:
        combined_paragraphs.append(buffer)

    # Return the combined paragraphs as a string with double newlines as separators
    return '\n\n'.join(combined_paragraphs)


if __name__ == '__main__':
    # Define the source file
    source_file = "EEG.mp4"

    # Create the workspace
    ws = workspace(source_file)

    # Define the paths
    input_path = ws.paths["compression_path"]
    output_path = ws.files["regrouped_text_file"]

    # Merge small paragraphs to make longer paragraphs
    text = file_handler(None, input_path, output_path, combine_short_and_disjointed_paragraphs)



    