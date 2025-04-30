from app.controller.AgentController import (
    run_anomaly_check,
    run_image_detection,
    run_output_formatting,
    run_batch_and_expiry_agent,
    run_quantity_agent
)
from app.schemas.schemas import FinalOutput
from PIL import Image
from typing import List
import base64
import io
import os
import pandas as pd
from app.utils.HttpResponseUtils import response_success, response_error
from langgraph.graph import StateGraph
from typing import TypedDict, Annotated
from qdrant_client import QdrantClient
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# --- Qdrant & Embedding Setup ---
client = QdrantClient(host='localhost', port=6333)
embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

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
    lambda state: "output" if state["anomaly_result"] else "detection"
)

graph.add_conditional_edges(
    "detection",
    lambda state: "output" if state["anomaly_result"] else "batch_and_expiry"
)

graph.add_edge("batch_and_expiry", "quantity")
graph.add_edge("quantity", "output")

graph.set_finish_point("output")

graph_pipeline = graph.compile()

# --- Dataset Load ---
#df = pd.read_csv("Dataset/drugs_items_filtered.csv")

# --- Main Runner ---
def run_pipeline(pil_images: List[Image.Image]) -> FinalOutput:
    try:
        image_inputs = []
        for img in pil_images:
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            base64_img = base64.b64encode(buf.getvalue()).decode()
            image_inputs.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_img}"
                }
            })

        # Run graph
        result = graph_pipeline.invoke({"images": image_inputs})

        final_output_data = {}

        if result.get("anomaly_result", False):
            try: 
                return response_success(FinalOutput(
                    item_id=None,
                    item_name=None,
                    quantity=None,
                    batch_number=None,
                    expiry_date=None,
                    is_anomaly=True)   
                )    
            except Exception as e:
                return response_error(e)    

        # Jika tidak anomaly, cari item_id dari item_name
        item_name = result.get("detection_result", {}).get("item_name", None)
        
        if item_name:
            item_name_embedding = embedding_model.embed_query(item_name)
            search_result = client.search(
                collection_name="item_collection",
                query_vector=item_name_embedding,
                limit=1
            )
            if search_result and search_result[0].payload.get("item_code"):
                final_output_data["item_id"] = search_result[0].payload["item_code"]
                final_output_data["item_name"] = search_result[0].payload.get("item_name", item_name)
            else:
                final_output_data["item_id"] = None
                final_output_data["item_name"] = item_name  # fallback ke input
        else:
            final_output_data["item_id"] = None
            final_output_data["item_name"] = None
        
        final_output_data["item_name"] = search_result[0].payload.get("item_name", item_name)
        final_output_data["quantity"] = result.get("quantity_result", None)
        final_output_data["batch_number"] = result.get("batch_and_expiry_result", {}).get("batch_number", None)
        final_output_data["expiry_date"] = result.get("batch_and_expiry_result", {}).get("expiry_date", None)

        print("Final Output:", final_output_data)

        return response_success(FinalOutput(**final_output_data).model_dump())
    except Exception as e:
            return response_error(e)
