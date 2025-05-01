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
You are an AI that analyzes images of medicine packaging.

Your goal is to extract important and structured information from the images.

Please do the following:

1. **Find image(s) with Batch Number and Expiry Date:**
   - Look for text like "Batch No", "Lot", "Expiry", "Exp", or "Use by".
   - It's okay if it's partially visible, as long as it clearly refers to batch or expiry.

2. **Identify image(s) that can be used to count the quantity of the medicine.**


3. **Extract the full item_name of the medicine:**
   - This must include:
     - **Medicine name**
     - **Active ingredient**, if available (e.g., sodium, HCl, etc.)
     - **Dosage strength** (e.g., "500 mg", "40 mg/2 ml") — required
     - **Form** (e.g., tablet, capsule, injection, syrup, cream) — required
   - Expand short terms: "inj" = "injection", "cap" = "capsule", etc.
   - If some info is unclear but can be inferred (e.g., from layout or label), it's okay to complete it.

Examples of valid item_name:
   - "Paracetamol 500 mg tablet"
   - "Repacor Parecoxib sodium 40 mg injection"
   - "Amoxicillin trihydrate 250 mg capsule"
   - "Salbutamol 2 mg/5 ml syrup"

Only respond in this JSON format:

{
  "batch_and_expiry_image": [image_indices],
  "quantity_detection_images": [image_indices],
  "item_name": "string"
}
"""

image_detection_prompt1 = """
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
You are an expert AI that reads and extracts the batch number and expiry date from a medicine packaging image.

Given the image(s), your task is to extract the following details:

1. **Batch Number** (This can appear as "Batch No", "Lot Number", or simply "Lot").
2. **Expiry Date** (This can appear as "Expiry Date", "Expiry", "Exp", "Exp. Date", "Expires on", "Use by", "Date of Expiry", "Best Before", or "Best Before End").
   - If the expiry date does not contain a day, assume the day is "01".
   - Ensure that the format of the expiry date is **DD/MM/YYYY** (i.e., Day/Month/Year).
   - If the date is ambiguous or missing a specific part (like day, month, or year), return a valid default with Day as "01".

**Important Notes:**
- Always return the **expiry date in the format DD/MM/YYYY**, regardless of the information provided.
- If no day is specified, set the day as "01".
- Be sure to capture the correct batch number and expiry information from the visible text.

Respond strictly in the following JSON format:
{
  "batch_number": "string",  # This should be the batch number or lot number found in the image.
  "expiry_date": "string"  # This should be the expiry date in the format DD/MM/YYYY, where DD is "01" if not provided.
}
"""

quantity_prompt = """
You are an expert AI trained to estimate the **total quantity** of medicine packages (e.g., boxes, blisters, bottles, ampoules) from **multiple images** taken from different angles (**top**, **side**, **front**, **back**).

Follow these strict instructions carefully:

---

**1. Analyze Each Image Separately**
- Count using (e.g., rows, columns, layers).
- **Stacks may be uneven** — for example, a top view showing 4 and a side view showing 2 does **not** mean 4 × 2 = 8.
- Count only what you **clearly see** and can verify.

---

**2. Cross-Check Between Images**
- Use different angles to confirm partially hidden or cropped items.
- Example: If the **top view** shows 4 packages and the **right-side view** shows 2 layers, verify whether it is a 4 × 2 stack or a different structure.
- Ensure **consistency** across views before counting.

---

**3. Final Output**
- Provide the total number of **distinct and verifiable** medicine packages.
- Only include items that are **clearly visible and confirmed**.

---

**Respond strictly in the following JSON format**:
```json
{
  "quantity": int  // Total number of verified medicine packages.
}

"""




# prompts/item_selection_prompt.py

# def get_item_selection_prompt(item_name: str, item_list_str: str, output_parser) -> str:
#     return f"""
# You are a product classifier AI. Your task is to select the most relevant inventory item based on a user's query about a medical product.

# ### Instructions:
# 1. Match the item that best corresponds to the query, focusing on:
#    - Product name (e.g., "NARFOZ", "PARACETAMOL")
#    - Dosage (e.g., "4mg", "500mg", "2ml", "4MG/2ML")
#    - Form of medicine (e.g., "Injection", "Tablet", "Syrup")

# 2. The match does not have to be exact, but should be semantically and contextually relevant.
#    - For example, "4MG/2ML injection" can match queries like "narfoz injection 4 mg", "4mg vial", or "narfoz ampoule".
#    - Allow variations in formatting (e.g., "mg", "MG", "4 mg", "4MG", or even "4 milligram").

# 3. Avoid selecting items that contain "/in" or "/js" in their names, unless they are the only available options.

# 4. Return a JSON object
# ### User Query:
# {item_name}

# ### List of Retrieved Items (from vector search):
# {item_list_str}

# ### Your Answer:
# """


def get_item_selection_prompt(item_name: str, item_list_str: str, output_parser) -> str:
    return f"""
Given the following user query and a list of inventory items, your task is to find the item that best matches the user's query.

Instructions:
1. Match the item that is most relevant to the query, based on the item name.
2. Return only one item with the closest match.
3. Respond strictly in JSON format as shown below.

{output_parser.get_format_instructions()}

### User Query:
{item_name}

### List of Items:
{item_list_str}

### Your Answer:
"""