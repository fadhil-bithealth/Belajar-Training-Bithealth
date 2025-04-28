# primary_agent.py
from langchain_core.messages import HumanMessage
from app.prompts import unified_prompt
from app.parser import final_parser
from app.config import llm
from app.schema import FinalOutput

def run_primary_agent(images) -> FinalOutput:
    messages = [HumanMessage(content=[{"type": "text", "text": unified_prompt}] + images)]
    response = llm.invoke(messages)
    parsed = final_parser.parse(response.content)
    return FinalOutput(**parsed)
