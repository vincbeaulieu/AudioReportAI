import torch
from transformers import BartTokenizer, BartForConditionalGeneration
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import psutil
from ..header import workspace, success, Specs


def summarize_paragraph(paragraph, model, tokenizer, max_length=512):
    # Summarize a single paragraph
    inputs = tokenizer(paragraph, return_tensors='pt', max_length=1024, truncation=True)
    summary_ids = model.generate(
        inputs['input_ids'],
        num_return_sequences=1,
        max_length=max_length,
        early_stopping=True,
        num_beams=5,         # increase the number of beams
        temperature=0.7,     # decrease the temperature
        top_k=50             # increase the top_k value
        # These three parameters limits the freedom of text mutation to preserve the original text as much as possible
    )
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True, clean_up_tokenization_spaces=False)
    return summary


def summarize_transcript(transcript, model, tokenizer, max_length=512):
    # Multiprocess all paragraph to create a single summary
    paragraphs = transcript.split('\n\n')
    summaries = []

    # Multithread the process based on the maximum number of thread a cpu can take
    with ThreadPoolExecutor(max_workers=Specs.NUM_LOGICAL_CPU) as executor:
        tasks = [executor.submit(summarize_paragraph, paragraph, model, tokenizer, max_length) for paragraph in paragraphs if paragraph.strip()]
        for task in tasks:
            try:
                summary = task.result()
                summaries.append(summary)
            except Exception as e:
                print(f"Error during summarization: {e}")

    # Return the summarized text
    return summaries


def summarize_merged_text(input_path, output_path):
    # Load the transcript
    transcript = Path(input_path).read_text()

    # Initialize BART model and tokenizer
    model_name = 'facebook/bart-large-cnn'
    tokenizer = BartTokenizer.from_pretrained(model_name)
    model = BartForConditionalGeneration.from_pretrained(model_name)

    # Summarize the transcript paragraph by paragraph
    summaries = summarize_transcript(transcript, model, tokenizer)
    summary = "\n\n".join(summaries)

    # Write the summary to a text file
    Path(output_path).write_text(summary)

    # Return the summary
    return summary


def summarization_task(ws):
    # Summarize the compressed transcript
    print(f"- Summarize compressed transcript from \"{ws.source_file}\"")

    # Defining the input and output paths
    input_path = ws.config['SUMMARIZATION']['input_path']
    output_path = ws.config['SUMMARIZATION']['output_path']

    # Summarize the previously merged text
    summarize_merged_text(input_path, output_path)

    # Task completed
    success(f"- Compression completed for \"{ws.source_file}\"")


if __name__ == '__main__':
    # Define the source file
    source_file = "MRI.mp4"

    # Create the workspace
    ws = workspace(source_file)

    summarization_task(ws)


 