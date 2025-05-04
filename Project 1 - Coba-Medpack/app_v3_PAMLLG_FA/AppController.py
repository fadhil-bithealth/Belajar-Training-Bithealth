from app_v3_PAMLLG_FA.graph import build_medpack_graph
from app_v3_PAMLLG_FA.prompt import build_item_matching_prompt
from app_v3_PAMLLG_FA.schema import ItemMatch
from app_v3_PAMLLG_FA.utils import (
    extract_med_info, upper, search_items_from_query, merge_unique_results
)
from langchain.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tracers import LangChainTracer
from langchain.callbacks import tracing_v2_enabled
import os
from qdrant_client import QdrantClient

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT")

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GOOGLE_API_KEY)
parser = PydanticOutputParser(pydantic_object=ItemMatch)
client = QdrantClient(host='localhost', port=6333)

def process_images(image_paths):
    graph = build_medpack_graph()
    initial_state = {
        "images": [{"path": path} for path in image_paths],
        "primary_agent_result": {},
        "batch_and_expiry_result": {},
        "quantity_result": 0
    }

    final_state = graph.invoke(initial_state)
    item_name = final_state["primary_agent_result"].get("item_name")
    
    # Variasi pencarian
    info = extract_med_info(item_name)
    first_word = upper(info["A"])
    last_word = upper(info["B"])
    first_two_word = upper(f"{info['C']} {last_word}")
    simple_word = upper(info["D"])

    results = merge_unique_results(
        search_items_from_query(first_word, 10),
        search_items_from_query(first_two_word, 10),
        search_items_from_query(simple_word, 10),
    )

    # Build prompt dan pakai LangSmith tracing
    prompt = build_item_matching_prompt(item_name, results, parser)
    with tracing_v2_enabled(project_name=LANGSMITH_PROJECT):
        response = llm.invoke(prompt)

    parsed = parser.parse(response.content)

    return {
        "item_name": parsed.item_name,
        "item_code": parsed.item_code,
        "batch_number": final_state["batch_and_expiry_result"].get("batch_number"),
        "expiry_date": final_state["batch_and_expiry_result"].get("expiry_date"),
        "quantity": final_state["quantity_result"]
    }
