from anthropic import Anthropic
from anthropic.types.beta.messages.batch_create_params import Request
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from dotenv import load_dotenv
import os
import pandas as pd
from helper_tools import QA_TOOLS

def read_data(file_path: str):
    df = pd.read_csv(file_path)
    return df

def extract_batch_id(messages_batch):
    return messages_batch.id

def create_requests(df: pd.DataFrame, max_tokens: int = 8192, model: str = "claude-3-opus-20240229"):
    
    """Generate a list of requests to pass to Batch API."""

    qa_requests = []
    for idx, row in df.iterrows():
        question = f' QUESTION: {row["question"]}'
        answer_1 = f' RESPONSE A: {row["answer_1"]}'
        answer_2 = f' RESPONSE B: {row["answer_2"]}'

        output = Request(
            custom_id=f"request_{idx}",
            params=MessageCreateParamsNonStreaming(
                model=model,
                max_tokens=max_tokens,
                tools=QA_TOOLS,
                tool_choice={"type": "tool", "name": "evaluate_qa_pairs"},
                messages=[{
                    "role": "user",
                    "content": f"You are an expert in evaluating Q&A pairs. You are given a question and two responses to that question. You need to evaluate the two responses and determine which one is better. Below is the question and the two responses: {question}\n\n{answer_1}\n\n{answer_2}"
                }]
            )
        )
        qa_requests.append(output)
    
    return qa_requests

def execute_batch_run(qa_requests: list):
    
    """Execute batch run"""

    load_dotenv("/Users/netraranga/Desktop/Projects/.env")
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    response = client.beta.messages.batches.create(requests=qa_requests)
    return response


def extract_elements(messages_batch: str, element: str):
    responses = []
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    for result in client.beta.messages.batches.results(extract_batch_id(messages_batch),):
        
        responses.append(result.result.message.content[0].input[element])
    
    return responses
