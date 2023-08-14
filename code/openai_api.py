import os
import openai

from tokens import OPENAI_API_KEY

# Load your API key from an environment variable or secret management service
openai.api_key = os.getenv(OPENAI_API_KEY)

import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

def load_summary(file_path):
    with open(file_path, 'r') as file:
        summary = file.read()
    return summary

def generate_report(summary, structure, model, tokenizer, max_length=512):
    prompt = structure.format(summary=summary)
    inputs = tokenizer.encode(prompt, return_tensors='pt', max_length=max_length, truncation=True)
    outputs = model.generate(inputs, max_length=max_length, num_return_sequences=1, no_repeat_ngram_size=3, temperature=0.8, top_p=0.9, early_stopping=True)
    report = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return report

def main():
    # Load your summary
    summary_file = 'work/EEG/summary.txt'
    summary = load_summary(summary_file)

    # Define the report structure
    report_structure = """Executive Report:
    {summary}

    Introduction:
    [Write an introduction here based on the summary.]

    Background:
    [Provide background information related to the summary.]

    Analysis:
    [Analyze the main points from the summary and provide insights.]

    Conclusion:
    [Summarize your findings and provide recommendations based on the summary.]
    """

    # Initialize GPT-4 model and tokenizer for report generation
    gpt_model_name = 'openai/gpt-4'
    gpt_tokenizer = GPT2Tokenizer.from_pretrained(gpt_model_name)
    gpt_model = GPT2LMHeadModel.from_pretrained(gpt_model_name)

    # Generate the report
    report = generate_report(summary, report_structure, gpt_model, gpt_tokenizer)
    print('Generated Report:')
    print(report)

    with open("work/EEG/report.txt", "w") as file:
        file.writelines("\n\n".join(report))

if __name__ == '__main__':
    main()
