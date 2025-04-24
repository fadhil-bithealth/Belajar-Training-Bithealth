from core.config import llm
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.messages import AIMessage


def make_multimodal_prompt(text: str, image_data_url: str):
    return [
        {"type": "text", "text": text},
        {"type": "image_url", "image_url": {"url": image_data_url}}
    ]

def detect_if_obat(image_data_url: str):
    prompt = make_multimodal_prompt(
        "Kamu adalah asisten yang sangat teliti. Tugasmu adalah menentukan apakah gambar ini adalah gambar obat. Jawab 'yes' atau 'no'.",
        image_data_url
    )
    response = llm.invoke([{"role": "user", "content": prompt}])
    return "yes" in response.content.lower()

def detect_info(img_data_url):
    return llm.invoke([
        SystemMessage(content="Kamu adalah asisten yang bisa membaca gambar."),
        HumanMessage(
            content=[
                {"type": "text", "text": """Lihat gambar dan deteksi informasi berikut:
1. Nomor batch
2. Tanggal kadaluarsa
3. Nama item/obat

Jawab dalam format:
{
  "batch_number": true/false,
  "expiry_date": true/false,
  "item_name": true/false
}
"""}, 
                {"type": "image_url", "image_url": {"url": img_data_url}}
            ]
        )
    ]).content
    return llm.invoke(prompt).content

def detect_multiple_items(image_data_url: str):
    prompt = make_multimodal_prompt(
        "Gambar ini adalah gambar obat. Apakah gambar ini mengandung lebih dari satu jenis obat? Jawab 'yes' atau 'no'.",
        image_data_url
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    return "yes" in response.content.lower()


def anomaly_step(state):
    print("[DEBUG] [anomaly_step] Input State:", state)
    images = state["images"]
    reasons = []
    has_anomaly = False
    total_item_names = set()

    for idx, img_data_url in enumerate(images):
        if not detect_if_obat(img_data_url):
            has_anomaly = True
            reasons.append(f"Gambar ke-{idx+1} bukan gambar obat.")
            continue

        info_raw = detect_info(img_data_url)
        print(f"[DEBUG] Info response (gambar {idx+1}):", info_raw)
        try:
            info = eval(info_raw)
        except:
            info = {"batch_number": False, "expiry_date": False, "item_name": False}
            reasons.append(f"Format JSON tidak valid untuk gambar ke-{idx+1}.")

        if not all(info.values()):
            has_anomaly = True
            reasons.append(f"Gambar ke-{idx+1} tidak mengandung informasi lengkap.")

        if detect_multiple_items(img_data_url):
            has_anomaly = True
            reasons.append(f"Gambar ke-{idx+1} mengandung lebih dari satu jenis obat.")

        if info.get("item_name"):
            total_item_names.add(info["item_name"])

    if len(total_item_names) > 1:
        has_anomaly = True
        reasons.append("Terdapat lebih dari satu jenis obat di antara semua gambar.")

    return {
        **state,
        "is_anomaly": has_anomaly,
        "reason": "; ".join(reasons) if has_anomaly else None
    }

anomaly_step = RunnableLambda(anomaly_step)
