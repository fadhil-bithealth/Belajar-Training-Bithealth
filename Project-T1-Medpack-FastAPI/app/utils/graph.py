# app/utils/graph.py

from langgraph.graph import StateGraph, END, START
from langchain_core.runnables import RunnableLambda
from app.utils.agent import run_anomaly_check, run_image_detection, run_output_formatting
from app.schemas.response_schema import AnomalyResult, DetectionResult, FinalOutput
from typing import TypedDict, List
from PIL import Image

class GraphState(TypedDict):
    images: List
    anomaly_result: AnomalyResult
    detection_result: DetectionResult
    final_output: FinalOutput

def anomaly_check_node(state: GraphState) -> GraphState:
    result = run_anomaly_check(state["images"])
    return {**state, "anomaly_result": result}

def should_skip_detection(state: GraphState) -> str:
    return "anomaly" if state["anomaly_result"].is_anomaly else "no_anomaly"

def image_detection_node(state: GraphState) -> GraphState:
    result = run_image_detection(state["images"])
    return {**state, "detection_result": result}

def final_output_node(state: GraphState) -> GraphState:
    output = run_output_formatting(
        state["anomaly_result"],
        state.get("detection_result")
    )
    return {**state, "final_output": output}

def build_graph():
    builder = StateGraph(GraphState)

    builder.add_node("anomaly_check", RunnableLambda(anomaly_check_node))
    builder.add_node("image_detection", RunnableLambda(image_detection_node))
    builder.add_node("format_output", RunnableLambda(final_output_node))

    builder.add_conditional_edges(
        "anomaly_check",
        should_skip_detection,
        {
            "anomaly": "format_output",
            "no_anomaly": "image_detection"
        }
    )

    builder.add_edge("image_detection", "format_output")
    builder.add_edge("format_output", END)
    builder.add_edge(START, "anomaly_check")
    builder.set_entry_point("anomaly_check")

    return builder.compile()
