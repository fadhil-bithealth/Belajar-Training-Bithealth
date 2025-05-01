# app/prompts.py

from app.parser import final_parser

anomaly_check_prompt = """
You are an AI that reviews medicine packaging images.

Given one or more images:
1. Determine if each image is a medicine product image.
2. Check if the combination of images provides:
   - Batch Number
   - Expiry Date
   - Item Name and description below
3. Check that all images depict only one kind of medicine. If an image contains multiple medicines, or different medicines across images, it's an anomaly.

Reply only in JSON:
{
  "is_anomaly": true or false
}
"""

image_detection_prompt = """
You are an AI that analyzes valid medicine packaging images.

Given the image context:
1. Identify which image(s) contain the Batch Number and Expiry Date.
2. Identify image(s) that can be used to count the quantity of the medicine.
3. Extract the item name includes the description below and the ml or mg value.

Reply only in JSON:
{
  "batch_and_expiry_image": [image_indices],
  "quantity_detection_images": [image_indices],
  "item_name": "string"
}
"""


primary_agent_prompt ="""
You are an AI that reviews medicine packaging images.

there are two task :
1. anomaly check
  Given one or more images:
  step 1. Determine if each image is a medicine product image.
  step 2. Check if the combination of images provides:
        - Batch Number
        - Expiry Date
        - Item Name and description below
  step 3. Check that all images depict only one kind of medicine. If an image contains multiple medicines, or different medicines across images, it's an anomaly.

2. image detection
  step 1. Identify which image(s) whose the Batch Number (e.g. Batch No. or BN format) and Expiration Date (e.g. EXP or ED format) **are visible**.\n
  step 2. Identify which image(s) can be used to count the quantity of the medicine.\n
  step 3. Extract the item name includes the description below and the ml or mg value.\n


Reply only in JSON:

{
  "item_name": "string",  
  "is_anomaly": true or false,
  "batch_and_expiry_image": [image_indices],
  "quantity_detection_images": [image_indices],
}


"""

final_output_prompt = (
    "You are formatting the final output. Given anomaly check and detection data, generate this format:\n\n"
    + final_parser.get_format_instructions()
)

# Tambahkan 2 prompt baru

batch_expiry_prompt = """
You are an expert AI that reads batch number and expiry date from a medicine image.

Given the image(s), extract:
- Batch Number | Batch No | Lot Number
- Expiry Date | Expiry | Exp | Exp. Date | Expires on | Use by
- Date of Expiry | Best Before | Best Before End

If there is no date, return the DD as 01
Reply in JSON:
{
  "batch_number": "string",
  "expiry_date": "string" With format DD/MM/YYYY
}
"""

quantity_prompt = """
You are an expert AI that estimates medicine quantity from the given images.

Given the image(s) with different POV, estimate:
- Total quantity of items (count boxes, blisters, bottles, etc.)

Reply in JSON:
{
  "quantity": int
}
"""


# prompts/item_selection_prompt.py

def get_item_selection_prompt(item_name: str, item_list_str: str, output_parser) -> str:
    return f"""
You are a product classifier AI. Your task is to find the most relevant inventory item based on the user's query about a medical product.

Instructions:
1. Match the item that best corresponds to the query, focusing primarily on the item name.
2. The name is usually the first word in the product (e.g., NARFOZ, PARACETAMOL).
3. Pay close attention to the milligram (mg), volume (ml), and item form (e.g., Injection, Tablet, Syrup). For example, 4MG/2ML means 4mg in 2ml.
4. Avoid selecting items with "/in" or "/js" in the name, as these may refer to grouped insurance names (e.g., inhealth, bpjs). If only one such item exists, it's acceptable.
5. Return only **one** item with the closest match from the list.

{output_parser.get_format_instructions()}

### User Query:
{item_name}

### List of Retrieved Items (from vector search):
{item_list_str}

### Your Answer:
"""
