from app.schemas.schemas import FinalOutput
from typing import List
import base64
import io
import pandas as pd
from app.utils.HttpResponseUtils import response_success, response_error
from app.controller.GraphController_Agent import graph_pipeline
from typing import List, Optional
from pydantic import BaseModel # type: ignore
from langchain.output_parsers import PydanticOutputParser
from app.utils.prompts import get_item_selection_prompt
from PIL import Image
from config import resources
from app.schemas.schemas import ItemMatch

# LLM, Qdrant, embedding model initialization
llm = resources.llm
llm_rag = resources.llm_rag
embedding_model = resources.embedding_model
client = resources.client

  
import re

def normalize_item_name(item_name: str) -> str:
    """
    Ambil kata pertama (brand name), kata yang mengandung angka atau satuan seperti mg/ml, 
    dan bentuk obat (form) dalam versi pendek.
    """

    form_map = {
        "tablet": "tab", "tab": "tab", "tablets": "tab",
        "capsule": "cap", "cap": "cap", "caps": "cap", "kapsul": "cap",
        "syrup": "syr", "syr": "syr", "sirup": "syr", "sir": "syr",
        "injection": "inj", "inj": "inj", "inject": "inj",
        "cream": "cream", "krim": "cream",
        "drop": "drop", "drops": "drop", "tetes": "drop",
        "suspension": "susp", "susp": "susp", "suspensi": "susp",
        "powder": "pwd", "serbuk": "pwd", "serbuk oral": "pwd",
        "oral powder": "pwd", "sach": "pwd", "sachet": "pwd", 
        "serbuk oral sach": "pwd", "oral sachet": "pwd", "serbuk sachet": "pwd",
        "granule": "gran", "granules": "gran", "granul": "gran",
        "gel": "gel",
        "ointment": "oint", "salep": "oint",
        "solution": "sol", "solusi": "sol",
        "elixir": "elx", "eliksir": "elx",
        "emulsion": "emul", "emulsi": "emul",
        "spray": "spray", "semprot": "spray",
        "lozenge": "loz", "isap": "loz"
    }

    words = item_name.split()
    brand_name = words[0]

    # Cari kata yang mengandung angka atau satuan umum seperti mg, ml, IU, dll
    dose_words = [w for w in words if re.search(r'\d', w) or re.match(r'^\d*(mg|ml|iu|mcg)$', w.lower())]

    # Normalisasi form
    form = next(
        (form_map[w.lower()] for w in words if w.lower() in form_map),
        None
    )

    parts = [brand_name] + dose_words
    if form:
        parts.append(form)

    return " ".join(parts).strip()


# --- Main Runner ---
def run_pipeline_agent(pil_images: List[Image.Image]) -> FinalOutput:
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
        rag_query = item_name
        print("Rag query:", rag_query)
        first_word = item_name.split()[1]
        print("first_word:", first_word)
        query_for_search_first = first_word
        normalized_query = normalize_item_name(item_name)  # atau detection_output["short_name"]
        print("Normalized Query:", normalized_query)

        ################ RAG #######################
        if item_name:
            item_name_embedding = embedding_model.embed_query(normalized_query)
            search_result = client.search(
                collection_name="item_collection",
                query_vector=item_name_embedding,
                limit=25,
            )

            item_name_embedding = embedding_model.embed_query(query_for_search_first)
            search_result_2 = client.search(
                collection_name="item_collection",
                query_vector=item_name_embedding,
                limit=25,
            )
            # Step 3: Ambil item_name dan item_code dari hasil pencarian
            results = []
            result_2 = []
    # Step 1: Define schema as a class
            for hit in search_result:
                payload = hit.payload
                item_name = payload.get("item_name", "Unknown")
                item_code = payload.get("item_code", "Unknown")
                results.append({"item_name": item_name, "item_code": item_code})
            
            for hit in search_result_2:
                payload = hit.payload
                item_name = payload.get("item_name", "Unknown")
                item_code = payload.get("item_code", "Unknown")
                result_2.append({"item_name": item_name, "item_code": item_code})
            
            print("###########################################################/n")
            # Step 2: Create output parser
            output_parser = PydanticOutputParser(pydantic_object=ItemMatch)

            # # Format list of items
            # item_list_str = "\n".join([
            #     f"{i+1}. {item['item_name']} (item_code: {item['item_code']})"
            #     for i, item in enumerate(results)
            # ])

            combined_results = {}
            for item in results + result_2:
                item_code = item.get("item_code", "Unknown")
                if item_code not in combined_results:
                    combined_results[item_code] = item  # Simpan hanya yang pertama
            unique_results = list(combined_results.values())

            item_list_str = "\n".join([
                f"{i+1}. {item['item_name']} (item_code: {item['item_code']})"
                for i, item in enumerate(unique_results)
            ])
            print("item_name LLM :", item_name)
            print("Item List String:/n", item_list_str)
            print("RAG Query : ", rag_query)
            prompt = get_item_selection_prompt(
                item_name=rag_query,
                item_list_str=item_list_str,
                output_parser=output_parser
            )

            # Step 4: Invoke LLM and parse output
            response = llm_rag.invoke(prompt)
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
