# quantity_detection_agent.py
from app.prompts import quantity_detection_prompt
from langchain_core.messages import HumanMessage
from app.config import llm
from app.parser import quantity_parser
import re

def extract_json(text):
    # Cari pattern JSON
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in the text: {text}")
    return match.group(0)

def run_quantity_detection_agent(images):
    messages = [HumanMessage(content=[{"type": "text", "text": quantity_detection_prompt}] + images)]
    response = llm.invoke(messages)

    # Coba parsing response
    try:
        clean_json = extract_json(response.content)
        parsed = quantity_parser.parse(clean_json)
    except Exception as e:
        # Kalau gagal, retry 1x dengan explicit instruction
        messages = [HumanMessage(content=[{"type": "text", "text": "STRICT: Reply ONLY with pure JSON. No explanation."}, {"type": "text", "text": quantity_detection_prompt}] + images)]
        response = llm.invoke(messages)
        try:
            clean_json = extract_json(response.content)
            parsed = quantity_parser.parse(clean_json)
        except Exception as e2:
            raise ValueError(f"Failed to parse quantity detection agent output after retry: {e2}\nContent: {response.content}")

    return parsed
