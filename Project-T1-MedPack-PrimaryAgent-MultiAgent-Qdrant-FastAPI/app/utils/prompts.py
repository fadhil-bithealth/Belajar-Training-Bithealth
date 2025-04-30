# app/prompts.py

from app.utils.parser import final_parser

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
3. Extract the item name includes the description below and the ml or mg value also the type of the drug (injection, tablet, syrup, etc.).

Reply only in JSON:
{
  "batch_and_expiry_image": [image_indices],
  "quantity_detection_images": [image_indices],
  "item_name": "string"
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

quantity_prompt1 = """
You are an expert AI that estimates medicine quantity from the given images.

Given the image(s) with different POV, estimate:
- Total quantity of items (count boxes, blisters, bottles, etc.)

Reply in JSON:
{
  "quantity": int
}
"""

quantity_prompt = """You're multimodal agentic llm created to counting drugs packs based on a given image. 
Each drug pack is a rectangular box, usually with a label, similar size across images.
If multiple boxes are stacked together, each visible front face counts as 1 pack.
Instructions:
1. Look at image 1 and count all visible drug packs.
2. Look at image 2 and count only the packs that are not visible in image 1.
3. Repeat for image 3, 4, etc.
4. Add up the total.
Count the number of packs in the image and provide the result in a structured JSON format as follows:
{{
    "total_quantity": <value | null>,
}}

And below is the uploaded images."""



rag_prompt = """
You are an expert in product identification. Given the name of a medical product `{item_name}`, select the most relevant official item name from the list below.

Available item names:
{item_names_list}

Please return only the most relevant item name from the list above.

You are a product classifier AI. You are given a list of item names from a database and you need to determine which item name is the most relevant. 

Here are the rules:
1. If there is more than one item name containing "/in" or "/js", do not select those, as they are typically associated with group names like inhealth or bpjs.
2. If there is only one item with "/in" or "/js", it's acceptable to select it.
3. If there is only one item name, choose the one that seems most relevant. For example, if an item name contains "/n", it's okay to select it.

Item Names: {item_names}

Please return the most relevant item name based on these criteria. 
"""
