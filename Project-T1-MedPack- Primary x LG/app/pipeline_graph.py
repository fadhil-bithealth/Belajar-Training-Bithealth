#pipeline_graph.py
from langgraph.graph import StateGraph, END
from typing import List, Optional
from pydantic import BaseModel
from app.primary_agent import run_primary_agent
from app.batch_number_agent import run_batch_number_agent
from app.quantity_detection_agent import run_quantity_detection_agent
import json

# Define State
class GraphState(BaseModel):
    images: List
    primary_result: Optional[dict] = None
    batch_and_expiry_result: Optional[dict] = None
    quantity_result: Optional[dict] = None

# Nodes
def primary_node(state: GraphState):
    result = run_primary_agent(state.images)
    return {"primary_result": result.dict()}

def batch_number_node(state: GraphState):
    batch_images_idx = state.primary_result.get("batch_and_expiry_image", [])
    selected_images = [state.images[idx] for idx in batch_images_idx]
    response = run_batch_number_agent(selected_images)
    return {"batch_and_expiry_result": response}  # <<< langsung return parsed object

def quantity_node(state: GraphState):
    quantity_images_idx = state.primary_result.get("quantity_detection_images", [])
    selected_images = [state.images[idx] for idx in quantity_images_idx]
    print(f"Selected images for quantity detection: {selected_images}")
    # Convert images to Base64 for the quantity detection agent
    response = run_quantity_detection_agent(selected_images)
    return {"quantity_result": response} 


# Build Graph
graph = StateGraph(GraphState)

graph.add_node("primary_agent", primary_node)
graph.add_node("batch_number_agent", batch_number_node)
graph.add_node("quantity_detection_agent", quantity_node)

graph.set_entry_point("primary_agent")

graph.add_edge("primary_agent", "batch_number_agent")
graph.add_edge("batch_number_agent", "quantity_detection_agent")
graph.add_edge("quantity_detection_agent", END)

compiled_graph = graph.compile()

# Run Graph
def run_pipeline_graph(pil_images: List) -> dict:
    # Convert images to Base64
    image_inputs = []
    for img in pil_images:
        import io, base64
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        base64_img = base64.b64encode(buf.getvalue()).decode()
        image_inputs.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}
        })
    
    result = compiled_graph.invoke({"images": image_inputs})
    
    output = {
        "item_name": result["primary_result"]["item_name"],
        "batch_number": result["batch_and_expiry_result"]["batch_number"],
        "expired_date": result["batch_and_expiry_result"]["expired_date"],
        "item_quantity": result["quantity_result"]["quantity"],
    }

    return output
