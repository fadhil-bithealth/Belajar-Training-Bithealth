# app/controller/GraphController.py

from langgraph.graph import StateGraph, END, START
from langchain_core.runnables import RunnableLambda
from typing import TypedDict, List
from PIL import Image

from app.controller.AgentController import agentController
from app.schemas.response_schema import AnomalyResult, DetectionResult, FinalOutput

# State untuk Graph
class GraphState(TypedDict):
    images: List[Image.Image]
    anomaly_result: AnomalyResult
    detection_result: DetectionResult
    final_output: FinalOutput

# Graph Controller
class GraphController:
    def __init__(self):
        self.graph = self.build_graph()

    def build_graph(self):
        builder = StateGraph(GraphState)

        # Tambahkan node
        builder.add_node("anomaly_check", RunnableLambda(self.anomaly_check_node))
        builder.add_node("image_detection", RunnableLambda(self.image_detection_node))
        builder.add_node("format_output", RunnableLambda(self.final_output_node))

        # Kondisional edge
        builder.add_conditional_edges(
            "anomaly_check",
            self.should_skip_detection,
            {
                "anomaly": "format_output",
                "no_anomaly": "image_detection"
            }
        )

        # Edges biasa
        builder.add_edge("image_detection", "format_output")
        builder.add_edge("format_output", END)

        # Start node
        builder.add_edge(START, "anomaly_check")
        builder.set_entry_point("anomaly_check")

        return builder.compile()

    # Node Functions
    def anomaly_check_node(self, state: GraphState) -> GraphState:
        result = agentController.run_anomaly_check(state["images"])
        return {**state, "anomaly_result": result}

    def image_detection_node(self, state: GraphState) -> GraphState:
        result = agentController.run_image_detection(state["images"])
        return {**state, "detection_result": result}

    def final_output_node(self, state: GraphState) -> GraphState:
        output = agentController.run_output_formatting(
            state["anomaly_result"],
            state.get("detection_result")
        )
        return {**state, "final_output": output}

    # Function untuk cek anomaly
    def should_skip_detection(self, state: GraphState) -> str:
        return "anomaly" if state["anomaly_result"].is_anomaly else "no_anomaly"

    # Function untuk invoke graph
    def invoke(self, inputs: dict) -> dict:
        return self.graph.invoke(inputs)

# Buat 1 instance global
graphController = GraphController()
