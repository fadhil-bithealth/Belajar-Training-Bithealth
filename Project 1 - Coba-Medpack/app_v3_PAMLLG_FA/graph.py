from langgraph.graph import StateGraph
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
from app_v3_PAMLLG_FA.agent import primary_agent, detect_batch_and_expiry, detect_quantity


class Medpack(TypedDict):
    images: Annotated[List[dict], "Input images in format [{'path': ...}]"]
    primary_agent_result: Annotated[dict, "Detect anomaly and identify indices"]
    batch_and_expiry_result: Annotated[dict, "Batch & expiry parsing result"]
    quantity_result: Annotated[int, "Quantity counting result"]


def primary_agent_node(state: Medpack) -> Medpack:
    image_paths = [img["path"] for img in state["images"]]
    result = primary_agent(image_paths)
    
    return {
        **state,
        "primary_agent_result": result if result else {}
    }

def batch_expiry_node(state: Medpack) -> Medpack:
    image_paths = [img["path"] for img in state["images"]]
    primary_result = state["primary_agent_result"]

    result = detect_batch_and_expiry(image_paths, primary_result)
    return {
        **state,
        "batch_and_expiry_result": result if result else {}
    }

def quantity_node(state: Medpack) -> Medpack:
    image_paths = [img["path"] for img in state["images"]]
    primary_result = state["primary_agent_result"]

    result = detect_quantity(image_paths, primary_result)
    return {
        **state,
        "quantity_result": result.get("quantity") if result else None
    }

def output_node(state: Medpack) -> Medpack:
    print("\nFinal Medpack State:")
    print(state)
    return state

def check_anomaly(state: Medpack) -> str:
    result = state.get("primary_agent_result", {})
    if result.get("is_anomaly", False):
        return "Output"  # langsung keluar jika anomaly
    return "BatchExpiry"  # lanjut proses normal


def build_medpack_graph():
    graph = StateGraph(Medpack)

    # Tambah node
    graph.add_node("PrimaryAgent", primary_agent_node)
    graph.add_node("BatchExpiry", batch_expiry_node)
    graph.add_node("Quantity", quantity_node)
    graph.add_node("Output", output_node)

    # Set entry
    graph.set_entry_point("PrimaryAgent")

    # Kondisi setelah primary agent
    graph.add_conditional_edges("PrimaryAgent", check_anomaly)

    # Jalur normal
    graph.add_edge("BatchExpiry", "Quantity")
    graph.add_edge("Quantity", "Output")

    # Set selesai
    graph.set_finish_point("Output")

    return graph.compile()
