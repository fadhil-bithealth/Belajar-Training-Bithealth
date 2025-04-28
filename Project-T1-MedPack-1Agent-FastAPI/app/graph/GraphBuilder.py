# app/graph/graph_builder.py

from langgraph.graph import StateGraph, END
from app.controller.AgentController import agentController
from typing import TypedDict, List, Optional
from PIL import Image
from app.schemas.response_schema import AnomalyResult, DetectionResult, FinalOutput
import logging

# Setup basic logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# 1. Define custom state
class PipelineState(TypedDict, total=False):
    images: List[Image.Image]
    anomaly_result: AnomalyResult
    detection_result: Optional[DetectionResult]
    final_output: dict

# 2. Define async node functions
async def anomaly_check(state: PipelineState):
    logger.info("[Pipeline] Starting Anomaly Check...")
    images = state['images']
    anomaly_result = await agentController.run_anomaly_check(images)
    logger.info(f"[Pipeline] Anomaly Check Result: {anomaly_result.is_anomaly}")
    state['anomaly_result'] = anomaly_result
    return state

async def image_detection(state: PipelineState):
    logger.info("[Pipeline] Starting Image Detection...")
    images = state['images']
    detection_result = await agentController.run_image_detection(images)
    logger.info(f"[Pipeline] Detection Result: Item Name = {detection_result.item_name}")
    state['detection_result'] = detection_result
    return state

async def final_output(state: PipelineState):
    logger.info("[Pipeline] Starting Final Output Formatting...")
    anomaly_result = state['anomaly_result']
    detection_result = state.get('detection_result')
    images = state['images']
    final_output = await agentController.run_output_formatting(anomaly_result, detection_result, images)
    logger.info(f"[Pipeline] Final Output: Item = {final_output.item_name}, Batch = {final_output.batch_number}")
    state['final_output'] = final_output
    return state

# 3. Define router function
def anomaly_router(state: PipelineState):
    logger.info("[Pipeline] Routing based on Anomaly Result...")
    if state['anomaly_result'].is_anomaly:
        logger.info("[Pipeline] Anomaly detected, skipping image detection.")
        return "format_final_output"
    else:
        logger.info("[Pipeline] No anomaly, continue to image detection.")
        return "image_detection"

# 4. Build graph
def build_graph():
    graph = StateGraph(PipelineState)

    graph.add_node("anomaly_check", anomaly_check)
    graph.add_node("image_detection", image_detection)
    graph.add_node("format_final_output", final_output)

    graph.set_entry_point("anomaly_check")

    graph.add_conditional_edges(
        "anomaly_check",
        anomaly_router,
    )

    graph.add_edge("image_detection", "format_final_output")
    graph.add_edge("format_final_output", END)

    logger.info("[Pipeline] Graph compiled successfully.")

    return graph.compile()

# 5. Buat instance siap pakai
pipeline_graph = build_graph()
