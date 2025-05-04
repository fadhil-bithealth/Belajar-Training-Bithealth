import os
from langchain_core.messages import HumanMessage
from app_v3_PAMLLG_FA.prompt import primary_agent_prompt, batch_expiry_prompt, quantity_prompt
from app_v3_PAMLLG_FA.image_utils import image_to_base64
from app_v3_PAMLLG_FA.parser import primary_agent_parser, batch_and_expiry_parser, quantity_parser
from app_v3_PAMLLG_FA.schema import PrimaryAgentOutput, BatchNumberOutput, QuantityOutput
from app_v3_PAMLLG_FA.config import llm
from app_v3_PAMLLG_FA.helper import ensure_primary_result_object



def primary_agent(image_paths: list[str]) -> PrimaryAgentOutput:
    # Cek apakah ada gambar yang diupload
    if not image_paths:
        print("Warning: No images uploaded.")  # Peringatan jika tidak ada gambar
        return None  # Bisa ganti dengan output default atau exception sesuai kebutuhan

    contents = [
        {"type": "text", "text": primary_agent_prompt + "\n" + primary_agent_parser.get_format_instructions()}
    ]
    for idx, path in enumerate(image_paths):
        try:
            # Cek apakah file gambar ada
            if not os.path.exists(path):
                print(f"Error: File {os.path.basename(path)} not found.")  # Error jika file tidak ada
                continue

            print(f"{idx} -> {os.path.basename(path)}")  # Print nomor dan nama gambar
            contents.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_to_base64(path)}"
                }
            })
        except Exception as e:
            print(f"An error occurred while processing {os.path.basename(path)}: {e}")

    print(f"Total images processed: {len(image_paths)}")  # Print total

    try:
        response = llm.invoke([HumanMessage(content=contents)])
        parsed = primary_agent_parser.parse(response.content)
        return parsed.dict() 
    except Exception as e:
        print(f"An error occurred during LLM invocation: {e}")
        return None  # Menangani error di bagian LLM


def detect_batch_and_expiry(image_paths: list[str], primary_result: dict) -> dict:
    """
    Deteksi batch number dan expiry date berdasarkan indeks dari hasil primary_agent.
    """
    primary = ensure_primary_result_object(primary_result)

    # Validasi input
    if not primary or not primary.batch_and_expiry_image_index:
        print("No batch_and_expiry_image_index found in primary_result.")
        return None

    batch_indices = primary.batch_and_expiry_image_index
    contents = [{"type": "text", "text": batch_expiry_prompt + "\n" + batch_and_expiry_parser.get_format_instructions()}]

    for idx in batch_indices:
        if idx < 0 or idx >= len(image_paths):
            print(f"Invalid index {idx} in batch_and_expiry_image_index.")
            continue

        image_path = image_paths[idx]
        try:
            if not os.path.exists(image_path):
                print(f"File not found: {image_path}")
                continue

            print(f"Processing batch/expiry image: {os.path.basename(image_path)}")
            contents.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_to_base64(image_path)}"
                }
            })
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            continue

    try:
        response = llm.invoke([HumanMessage(content=contents)])
        parsed = batch_and_expiry_parser.parse(response.content)
        return parsed.model_dump() 
    except Exception as e:
        print(f"LLM invocation error: {e}")
        return None



def detect_quantity(image_paths: list[str], primary_result: PrimaryAgentOutput) -> QuantityOutput:
    """
    Deteksi quantity berdasarkan indeks dari hasil primary_agent.
    """
    primary = ensure_primary_result_object(primary_result)
    if not primary or not primary.quantity_image_index:
        print("No quantity_image_index found in primary_result.")
        return None

    quantity_indices = primary.quantity_image_index
    contents = [{"type": "text", "text": quantity_prompt + "\n" + quantity_parser.get_format_instructions()}]

    for idx in quantity_indices:
        if idx < 0 or idx >= len(image_paths):
            print(f"Invalid index {idx} in quantity_image_index.")
            continue

        image_path = image_paths[idx]
        try:
            if not os.path.exists(image_path):
                print(f"File not found: {image_path}")
                continue

            print(f"Processing quantity image: {os.path.basename(image_path)}")
            contents.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_to_base64(image_path)}"
                }
            })
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            continue

    try:
        response = llm.invoke([HumanMessage(content=contents)])
        parsed = quantity_parser.parse(response.content)
        return parsed.model_dump() 
    except Exception as e:
        print(f"LLM invocation error: {e}")
        return None