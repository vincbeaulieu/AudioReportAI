

def file_handler(transcript=None, input_path=None, output_path=None, function=None, **kwargs):
    # Read text from the input path if there is no transcript provided
    if transcript is None:
        with open(input_path, 'r') as file:
            transcript = file.read()

    # Process the function with its keyword arguments
    if function is not None:
        transcript = function(transcript, **kwargs)

    # Write the compressed text at the output path if provided with the path
    if output_path is not None:
        with open(output_path, 'w') as file:
            file.writelines(transcript)

    # Return the result
    return transcript
