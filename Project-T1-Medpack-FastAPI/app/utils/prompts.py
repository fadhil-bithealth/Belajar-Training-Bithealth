
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
4. All images combined should provide:
   - Batch Number
   - Expiry Date
   - Item Name and description below
   - ml or mg value
5. If any of the above is missing, it's an anomaly.

If no image includes the Batch Number and Expiry Date, set is_anomaly to true.
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
