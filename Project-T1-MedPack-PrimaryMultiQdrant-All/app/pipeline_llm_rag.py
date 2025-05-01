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
import pandas as pd
from app.schema import ItemMatch
from app.parser import output_parser
from langgraph.graph import StateGraph
from typing import TypedDict, Annotated
from qdrant_client import QdrantClient
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.HttpResponseUtils import response_success, response_error

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

# --- Dataset Load ---
#df = pd.read_csv("Dataset/drugs_items_filtered.csv")
from typing import List, Optional
from pydantic import BaseModel # type: ignore
from langchain.output_parsers import PydanticOutputParser
from app.config import llm, embedding_model
from app.HttpResponseUtils import response_success, response_error
from app.prompts import get_item_selection_prompt

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
        print("Item Name:", item_name)
        query_for_rag = str(item_name)

        ################ RAG #######################
        if item_name:
            item_name_embedding = embedding_model.embed_query(item_name)
            search_result = client.search(
                collection_name="item_collection",
                query_vector=item_name_embedding,
                limit=10
            )
            # Step 3: Ambil item_name dan item_code dari hasil pencarian
            results = []
    # Step 1: Define schema as a class
            for hit in search_result:
                payload = hit.payload
                item_name = payload.get("item_name", "Unknown")
                item_code = payload.get("item_code", "Unknown")
                results.append({"item_name": item_name, "item_code": item_code})
            
            print("Search Results:", search_result)

            class ItemMatch(BaseModel):
                item_name: Optional[str] = None
                item_code: Optional[str] = None

            # Step 2: Create output parser
            output_parser = PydanticOutputParser(pydantic_object=ItemMatch)

            # Format list of items
            item_list_str = "\n".join([
                f"{i+1}. {item['item_name']} (item_code: {item['item_code']})"
                for i, item in enumerate(results)
            ])

            print("Item List String:", item_list_str)

            prompt = get_item_selection_prompt(
                item_name=query_for_rag,
                item_list_str=item_list_str,
                output_parser=output_parser
            )

            # Step 4: Invoke LLM and parse output
            response = llm.invoke(prompt)
            parsed = output_parser.parse(response.content)
            hasil = parsed.model_dump() 
            final_output_data["item_name"] = hasil['item_name']
            final_output_data["item_id"] = hasil['item_code']

    
        else:
            final_output_data["item_id"] = None

        final_output_data["item_name"] = hasil['item_name']
        final_output_data["quantity"] = result.get("quantity_result", None)
        final_output_data["batch_number"] = result.get("batch_and_expiry_result", {}).get("batch_number", None)
        final_output_data["expiry_date"] = result.get("batch_and_expiry_result", {}).get("expiry_date", None)

        print("Final Output:", final_output_data)

        return response_success(final_output_data)
    except Exception as e:
            return response_error(e)
