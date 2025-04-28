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

final_output_prompt = (
    "You are formatting the final output. Given anomaly check and detection data, generate this format:\n\n"
    + final_parser.get_format_instructions()
)

# Tambahkan 2 prompt baru

batch_expiry_prompt = """
You are an expert AI that reads batch number and expiry date from a medicine image.

Given the image(s), extract:
- Batch Number
- Expiry Date

Reply in JSON:
{
  "batch_number": "string",
  "expiry_date": "string"
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