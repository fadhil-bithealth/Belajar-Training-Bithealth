from core.config import llm
from langchain_core.runnables import RunnableLambda
import json

def extract_image_details(image, index):
    prompt = f"""
Gambar berikut merupakan gambar obat dalam konteks input multi-gambar.

Gambar: {image}

Tugas kamu adalah menjawab dalam format JSON:
{{
  "has_batch_expiry": true/false,
  "can_detect_quantity": true/false,
  "item_name": "nama obat atau kosong"
}}

Ingat:
- has_batch_expiry = true jika gambar mengandung nomor batch dan tanggal kadaluarsa.
- can_detect_quantity = true jika gambar menunjukkan berapa banyak unit obatnya.
- item_name harus dikembalikan jika terlihat jelas dari label obat.
"""
    response = llm.invoke(prompt).content
    try:
        result = json.loads(response)
        return {
            "image_index": index,
            **result
        }
    except:
        return {
            "image_index": index,
            "has_batch_expiry": False,
            "can_detect_quantity": False,
            "item_name": ""
        }

def image_detection_step(state):
    images = state["images"]
    image_batch_expiry = []
    image_quantity = []
    detected_item_names = []

    for i, img in enumerate(images):
        result = extract_image_details(img, i)
        
        if result["has_batch_expiry"]:
            image_batch_expiry.append(i)
        if result["can_detect_quantity"]:
            image_quantity.append(i)
        if result["item_name"]:
            detected_item_names.append(result["item_name"])
    
    # Ambil nama yang paling banyak muncul
    item_name = max(set(detected_item_names), key=detected_item_names.count) if detected_item_names else ""

    return {
        **state,
        "image_for_batch_expiry": image_batch_expiry,
        "image_for_quantity": image_quantity,
        "item_name": item_name
    }

image_detection_step = RunnableLambda(image_detection_step)
