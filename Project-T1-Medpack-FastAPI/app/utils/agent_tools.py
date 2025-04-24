# app/utils/agent_tools.py

from langchain_core.tools import tool

@tool
def tool(name: str) -> str:
    """ tool for agents """
    return f"Hello, {name}."
