
from ..header import workspace, error
from .file_handler import file_handler

import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from collections import defaultdict
from enum import Enum


# Try to load the en_core_web_sm model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # If the model is not found, download it
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

class SegmentationType(Enum):
    SENTENCES = 1
    PARAGRAPHS = 2

def keyword_occurences(doc):    
    # Compute keyword occurences of each token
    keyword_counts = defaultdict(int)
    for token in doc:
        if token.text.lower() not in STOP_WORDS and token.is_alpha:  # see NOTE at EOF
            keyword_counts[token.text.lower()] += 1
    return keyword_counts


def scorer(doc, keyword_counts):
    # Compute the score of the segment based on keyword occurrences
    score = 0
    for token in doc:
        if token.text.lower() not in STOP_WORDS and token.is_alpha:  # see NOTE at EOF
            score += keyword_counts[token.text.lower()]
    return score


# Remove text segments that do not add value to the main topic
def segment_filter(transcript, segmentation_type=SegmentationType.SENTENCES, user_defined_threshold_ratio=None):
    # Process the text segment to create a doc object
    doc = nlp(transcript)

    # Define the algorithm parameters
    if segmentation_type == SegmentationType.SENTENCES:
        segments = list(doc.sents)
        delimiter = " "
        threshold_ratio = 0.20
    elif segmentation_type == SegmentationType.PARAGRAPHS:
        segments = transcript.split('\n\n')
        delimiter = '\n\n'
        threshold_ratio = 0.90

    # Override the default threshold ratio if provided
    threshold_ratio = user_defined_threshold_ratio or threshold_ratio

    # Compute keyword occurences of each token in the doc
    keyword_count = keyword_occurences(doc)

    # Find the maximum keyword count and compute the threshold value
    threshold = max(keyword_count.values()) * threshold_ratio  # NOTE: Will throw an exception if transcript is empty

    # Score each segments and add it to the list of useful segments when greater than the threshold
    useful_segments = []
    for segment in segments:
        # Convert the segment to a string if it's a Span object
        if isinstance(segment, spacy.tokens.Span):
            segment = segment.text

        # Evaluate the usefulness of the segment
        doc = nlp(segment)

        # Append to useful segments list if above threshold
        if scorer(doc, keyword_count) > threshold:
            useful_segments.append(segment)

    # Combine the useful text into a single string and return the result
    transcript = delimiter.join(useful_segments).replace("\n ", "\n")
    
    # Return the result
    return transcript


def gratitude_filter(transcript=None):
    # TODO: Filter out useless sentences from Useless_sentences.txt

    # Define gratitude keywords
    # unessential_keywords = {'thank', 'thanks', 'thankful', 'appreciate', 'appreciation', 'grateful', 'gratitude'}

    # Define unessential keywords # TODO: Test this line
    with open("Useless_sentences.txt", 'r') as file:
        unessential_keywords = {line.strip() for line in file}

    # Evaluate if sentence is gratitude type
    def is_unessential_sentence(sentence):
        return any(token.text.lower() in unessential_keywords for token in nlp(sentence))

    # Create a comprehension list that filters out gratitude sentences
    non_unessential_sentences = [sent.text for sent in nlp(transcript).sents if not is_unessential_sentence(sent.text)]

    # Join the list using the join method
    transcript = " ".join(non_unessential_sentences).replace("\n ", "\n")

    # Return the result
    return transcript


if __name__ == "__main__":
    # Define the source file
    source_file = "Screen Recording 2023-03-24 at 18.32.35.mov"

    # Create the workspace
    ws = workspace(source_file)

    # Define the I/O paths
    input_path = ws.config['COMPRESSION']['input_path']
    output_path = ws.config['COMPRESSION']['output_path']
    
    # Define the processing paths
    init_text_path = ws.config['COMPRESSION']['stages_dir'] + 'stage_0-initial_text.txt'
    grat_filt_path = ws.config['COMPRESSION']['stages_dir'] + 'stage_1-gratitude_filtered.txt'
    sent_comp_path = ws.config['COMPRESSION']['stages_dir'] + 'stage_2-sentence_compressed.txt'
    para_comp_path = ws.config['COMPRESSION']['stages_dir'] + 'stage_3-paragraph_compressed.txt'
    comb_text_path = ws.config['COMPRESSION']['stages_dir'] + 'stage_4-combined_text.txt'

    # Process filtering
    text = ""
    try:
        text = file_handler(None, input_path, sent_comp_path, segment_filter, segmentation_type=SegmentationType.SENTENCES)
        text = file_handler(text, None, para_comp_path, segment_filter, segmentation_type=SegmentationType.PARAGRAPHS)
        text = file_handler(text, None, grat_filt_path, gratitude_filter)

    except ValueError as e:
        if len(text) == 0:
            error(f"ValueError: {e} - transcript has no content")
        else:
            raise e


# NOTE:
# Stop words include articles, prepositions, pronouns, and conjunctions.