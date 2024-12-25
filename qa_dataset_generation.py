from anthropic import Anthropic
import os
from dotenv import load_dotenv
import base64
import pandas as pd
import json
from typing import Dict
import time

def extract_message_content(message_cache: str):
    return message_cache.content[0].text

def generate_cache_usage(message_cache: str):
    for field in message_cache.usage:
        print(field)

def format_prompt(start_idx: int, end_idx: int):
    return f"""You are an expert at analyzing financial reports and generating question-answer pairs. For the provided PDF (the Cerulli report):

        1. Analyze pages {start_idx} to {end_idx} and for **each** of those 10 pages:
            - Identify the **exact page title** as it appears on that page (e.g., "Exhibit 4.03 Core Market Databank, 2023").
            - If the page includes a chart, graph, or diagram, create a question that references that visual element. Otherwise, create a question about the textual content.
            - Generate two distinct answers to that question ("answer_1" and "answer_2"), both supported by the page’s content.
            - Identify the correct page number as indicated in the bottom left corner of the page.
        2. Return exactly 10 results as a valid JSON array (a list of dictionaries). Each dictionary should have the keys: “page” (int), “page_title” (str), “question” (str), “answer_1” (str), and “answer_2” (str). The page title typically includes the word "Exhibit" followed by a number.
        3. Do not include any other text or comments.

        Below is an example of the output format:

        [
            {{
                "page": {start_idx},
                "page_title": "Exhibit 1.03 Core Market Databank, 2023",
                "question": "How does the distribution model highlighted in the chart reflect changes in investor behavior?",
                "answer_1": "The chart suggests a gradual shift toward hybrid channels, indicating that investors are looking for more flexible advisory models.",
                "answer_2": "It illustrates that more clients prefer a combination of digital engagement and traditional advice, reflecting evolving investor expectations."
            }},
            {{
                "page": {end_idx},
                "page_title": "Exhibit 2.18 Opinions on Advisor Technology, 2023",
                "question": "What does the data on this page suggest about advisors' willingness to adopt new technology tools?",
                "answer_1": "Advisors are becoming more open to integrating advanced planning software, reflecting increased comfort with digital solutions.",
                "answer_2": "The data shows a growing recognition among advisors that technology can streamline their workflows and enhance client experiences."
            }}
        ]

        Double-check your output to ensure each of the 10 JSON objects includes the correct page number, exact page title, a non-obvious question, and two supported answers."""

def execute_synthesis(start_idx: int, end_idx: int, file_path: str, model: str = "claude-3-5-sonnet-20241022"):

    load_dotenv("/Users/netraranga/Desktop/Projects/.env")
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    with open(file_path, 'rb') as f:
        pdf_data = base64.standard_b64encode(f.read()).decode('utf-8')

    message_cache = client.beta.messages.create(
        model=model,
        betas=["pdfs-2024-09-25", "prompt-caching-2024-07-31"],
        max_tokens=8192,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_data
                        },
                        "cache_control": {"type": "ephemeral"}
                    },
                    {
                        "type": "text",
                        "text": format_prompt(start_idx, end_idx)
                    
                    }]}],)
    return message_cache

def generate_qa_dataset_for_all_files(file_ranges: Dict):
    final_df = pd.DataFrame()
    
    for path, (start_page, end_page) in file_ranges.items():
        for idx in range(start_page, end_page, 10):
            end_idx = min(idx + 10, end_page)  
            qa_pairs = execute_synthesis(idx, end_idx, path)
            print(generate_cache_usage(qa_pairs))
            parsed_output = json.loads(extract_message_content(qa_pairs))
            
            if final_df.empty:
                final_df = pd.DataFrame(parsed_output)
                final_df["file_name"] = path
            else:
                df = pd.DataFrame(parsed_output)
                df["file_name"] = path
                final_df = pd.concat([final_df, df])
            
            if idx + 10 < end_page:  
                print("60 second buffer between batches due to Tier 2 rate limits")
                time.sleep(60)

    return final_df

if __name__ == "__main__":
    file_ranges = {
        "knowledge_base/cerulli_part1.pdf": (17, 66)
        # "knowledge_base/cerulli_part2.pdf": (67, 116),
        # "knowledge_base/cerulli_part3.pdf": (117, 166),
        # "knowledge_base/cerulli_part4.pdf": (167, 216)
    }
    final_test_set = generate_qa_dataset_for_all_files(file_ranges)
    final_test_set.to_csv("report_qa_pairs.csv")