# --- GraphController.py ---
from app.utils.Agent import (
    run_anomaly_check,
    run_image_detection,
    run_output_formatting,
    run_batch_and_expiry_agent,
    run_quantity_agent
)
from app.schemas.schemas import FinalOutput
from typing import List
from langgraph.graph import StateGraph
from typing import TypedDict, Annotated
from app.utils.HttpResponseUtils import response_success, response_error


# --- Graph State ---
class GraphState(TypedDict):
    images: Annotated[List[dict], "Input images"]
    anomaly_result: Annotated[bool, "Is anomaly detected"]
    detection_result: Annotated[dict, "Detection result"]
    batch_and_expiry_result: Annotated[dict, "Batch & expiry parsing result"]
    quantity_result: Annotated[int, "Quantity counting result"]

# --- Node Functions ---
def anomaly_node(state: GraphState):
    images = state["images"]
    anomaly = run_anomaly_check(images)
    print("ANOMALY PARSED:", anomaly)
    return {"anomaly_result": anomaly.is_anomaly}

def detection_node(state: GraphState):
    images = state["images"]
    detection = run_image_detection(images)

    # --- DETEKSI ANOMALI jika data kurang ---
    if (
        (not detection.item_name) or
        (not detection.batch_and_expiry_image) or
        (not detection.quantity_detection_images)
    ):
        return {
            "anomaly_result": True,
            "detection_result": {}
        }

    return {"detection_result": detection.model_dump(), "anomaly_result": False}

def batch_and_expiry_node(state: GraphState):
    images = state["images"]
    detection_result = state["detection_result"]
    selected_images = [images[idx] for idx in detection_result["batch_and_expiry_image"]]
    result = run_batch_and_expiry_agent(selected_images)
    return {
        "batch_and_expiry_result": {
            "batch_number": result.batch_number,
            "expiry_date": result.expiry_date
        }
    }

def quantity_node(state: GraphState):
    images = state["images"]
    detection_result = state["detection_result"]
    selected_images = [images[idx] for idx in detection_result["quantity_detection_images"]]
    result = run_quantity_agent(selected_images)
    return {"quantity_result": result.quantity}

def output_node(state: GraphState):
    anomaly = state.get("anomaly_result", False)

    if anomaly:
        # --- Jika anomaly, keluarkan kosong dan is_anomaly = True ---
        return FinalOutput(
            item_id=None,
            item_name=None,
            quantity=None,
            batch_number=None,
            expiry_date=None,
            is_anomaly=True
        )

    detection_result = state.get("detection_result", {})
    batch_and_expiry_result = state.get("batch_and_expiry_result", {})
    quantity_result = state.get("quantity_result", None)

    print("Detection Result:", detection_result)
    print("Batch and Expiry Result:", batch_and_expiry_result)
    print("Quantity Result:", quantity_result)

    final_dict = {
        "batch_number": batch_and_expiry_result.get("batch_number"),
        "expiry_date": batch_and_expiry_result.get("expiry_date"),
        "item_name": detection_result.get("item_name"),
        "quantity": quantity_result
    }

    return final_dict

# Fungsi eksplisit untuk menentukan jalur setelah anomaly check
def anomaly_check_condition(state):
    if state["anomaly_result"]:
        return "output"
    else:
        return "detection"
    
# Fungsi eksplisit untuk menentukan jalur setelah detection
def detection_condition(state):
    if state["anomaly_result"]:
        return "output"
    else:
        return "batch_and_expiry"
    


# --- Graph Building ---
graph = StateGraph(GraphState)

graph.add_node("anomaly_check", anomaly_node)
graph.add_node("detection", detection_node)
graph.add_node("batch_and_expiry", batch_and_expiry_node)
graph.add_node("quantity", quantity_node)
graph.add_node("output", output_node)

graph.set_entry_point("anomaly_check")

# --- CONDICIONAL FLOW ---
graph.add_conditional_edges(
    "anomaly_check",
    anomaly_check_condition
)
graph.add_conditional_edges(
    "detection",
    detection_condition
)

graph.add_edge("batch_and_expiry", "quantity")
graph.add_edge("quantity", "output")

graph.set_finish_point("output")

graph_pipeline = graph.compile()
