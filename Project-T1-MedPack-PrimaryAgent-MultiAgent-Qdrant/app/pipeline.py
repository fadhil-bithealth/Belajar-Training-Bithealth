from app.agent import (
    run_anomaly_check, 
    run_image_detection, 
    run_output_formatting,
    run_batch_and_expiry_agent,
    run_quantity_agent
)
from app.schema import FinalOutput
from PIL import Image
from typing import List
import base64
import io
import os

from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
from qdrant_client import QdrantClient
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Inisialisasi Qdrant Client
client = QdrantClient(host='localhost', port=6333)

# Inisialisasi model embeddings
embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

class GraphState(TypedDict):
    images: Annotated[List[dict], "Input images"]
    anomaly_result: Annotated[bool, "Is anomaly detected"]
    detection_result: Annotated[dict, "Detection result"]
    batch_and_expiry_result: Annotated[dict, "Batch & expiry parsing result"]
    quantity_result: Annotated[int, "Quantity counting result"]

# Node functions

def anomaly_node(state: GraphState):
    images = state["images"]
    anomaly = run_anomaly_check(images)
    return {"anomaly_result": anomaly.is_anomaly}

def detection_node(state: GraphState):
    images = state["images"]
    detection = run_image_detection(images)
    return {"detection_result": detection.model_dump()}

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


# di output_node
def output_node(state: GraphState):
    anomaly = state["anomaly_result"]
    
    if anomaly:
        # If anomaly detected, output is empty
        return FinalOutput(
            batch_number=None,
            expiry_date=None,
            item_name=None,
            quantity=None
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

# Create graph
graph = StateGraph(GraphState)

graph.add_node("anomaly_check", anomaly_node)
graph.add_node("detection", detection_node)
graph.add_node("batch_and_expiry", batch_and_expiry_node)
graph.add_node("quantity", quantity_node)
graph.add_node("output", output_node)

graph.set_entry_point("anomaly_check")

graph.add_conditional_edges(
    "anomaly_check",
    lambda state: "output" if state["anomaly_result"] else "detection"
)

graph.add_edge("detection", "batch_and_expiry")
graph.add_edge("batch_and_expiry", "quantity")
graph.add_edge("quantity", "output")

graph.set_finish_point("output")

graph_pipeline = graph.compile()

# Helper function

import pandas as pd

# Load the dataset of drugs items
df = pd.read_csv("Dataset/drugs_items_filtered.csv")

def run_pipeline(pil_images: List[Image.Image]) -> FinalOutput:
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

    # Menjalankan pipeline dan mendapatkan hasil
    result = graph_pipeline.invoke({"images": image_inputs})

    final_output_data = {}
    
    # Extract item name from the result
    item_name = result.get("detection_result", {}).get("item_name", None)
    
    # Jika item_name ditemukan, gunakan Qdrant untuk mencari item_id
    if item_name:
        # Convert item_name to embedding
        item_name_embedding = embedding_model.embed_query(item_name)


        # Lakukan pencarian di Qdrant
        search_result = client.search(
            collection_name="item_collection",
            query_vector=item_name_embedding,
            limit=1  # Batasi hanya 1 hasil yang paling relevan
        )
        
        # Ambil item_id dari hasil pencarian
        if search_result and search_result[0].payload.get("item_code"):
            final_output_data["item_id"] = search_result[0].payload["item_code"]
        else:
            final_output_data["item_id"] = None
    
    # Add other data to final output
    final_output_data["item_name"] = item_name
    final_output_data["quantity"] = result.get("quantity_result", None)
    final_output_data["batch_number"] = result.get("batch_and_expiry_result", {}).get("batch_number", None)
    final_output_data["expiry_date"] = result.get("batch_and_expiry_result", {}).get("expiry_date", None)
    
    print("Final Output:", final_output_data)
    
    return final_output_data
