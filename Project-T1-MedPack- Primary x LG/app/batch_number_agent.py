# batch_number_agent.py
from langchain_core.messages import HumanMessage
from app.prompts import batch_number_prompt
from app.parser import batch_number_parser
from app.config import llm
import json
import re

def extract_json(text: str) -> str:
    """Extract the first JSON object found in the text."""
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in the text: {text}")
    return match.group(0)

def run_batch_number_agent(images):
    messages = [HumanMessage(content=[{"type": "text", "text": batch_number_prompt}] + images)]
    response = llm.invoke(messages)

    if not response.content.strip():
        raise ValueError("Empty response from model in batch_number_agent.")

    print("=== RAW LLM RESPONSE ===")
    print(response.content)
    print("=========================")

    try:
        clean_json = extract_json(response.content)
        parsed = batch_number_parser.parse(clean_json)
    except Exception as e:
        raise ValueError(f"Failed to parse batch number agent output: {e}\nContent: {response.content}")

    return parsed
