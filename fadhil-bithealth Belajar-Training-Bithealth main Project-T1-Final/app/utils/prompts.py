# app/prompts.py

from app.utils.parser import final_parser

anomaly_check_prompt0000 = """
You are an AI that reviews medicine packaging images.

Given one or more images:

Note: Some photos may be upside down or taken from unusual angles. You can rotate as many as you want

Please do the following:
1. Check if each image likely shows a medicine product (e.g., box, bottle, blister, etc.).
2. Check if the combined images contain:
   - A Batch Number
   - An Expiry Date
   - An Item Name (usually large text) and its description (usually smaller text below it)
3. Verify whether all images represent the same medicine product.
   - If different medicines or mixed products are detected, mark this as an anomaly.


Reply only in JSON:
{
  "is_anomaly": true or false
}
"""

anomaly_check_prompt = """
You are an AI that looks at medicine packaging images to check for issues.

Sometimes the photos may be upside down or taken from unusual angles — feel free to mentally rotate or adjust your view if needed.

Please check the following:
1. Does each image show a medicine product? (like a box, bottle, blister pack, etc.)
2. When looking at all the images together, can you find:
   - A batch number
   - An expiry date
   - An item name (usually in big text) and its description (usually smaller text below)
3. Do all the images appear to show the same product?

If you notice images of different medicines or mixed products, that would count as an anomaly.

Just reply in this JSON format:

{
  "is_anomaly": true or false
}
"""


image_detection_prompt_work = """
You are an AI assistant that analyzes images of medicine packaging.

Your task is to extract structured information from one or more images.

Please follow these steps:

1. **Detect images that contain Batch Number and Expiry Date:**
   - Look for any text like "Batch No", "Lot", "Expiry", "Exp", "Use by", etc.
   - Partial visibility is acceptable as long as the meaning is clear.
   - **Important: Only include valid image indexes. Indexing starts from 0.**
   - For example, if there are 4 images, valid indexes are 0, 1, 2, and 3.

2. **Identify images that can be used to detect medicine quantity:**
   - Look for packaging that shows quantity: blister packs, bottles, boxes, strips, etc.
   - Again, only use valid indexes from 0 to N-1 where N is the number of input images.

3. **Extract the full item_name of the medicine from the images:**
   The `item_name` *must* include the following elements:
   - **Medicine name**
   - **Active ingredient(s)** (e.g., sodium, HCl) — if visible
   - **Dosage strength** (e.g., "500 mg", "40 mg/2 ml") — **required**
   - **Form** (e.g., tablet, capsule, injection, syrup, cream) — **required**

   Expand abbreviations and normalize terminology:
   - "inj" = "injection"
   - "cap", "caps", "kapsul", "capsule" = "capsule"
   - "tab", "tablet" = "tablet"
   - Translate or normalize terms in other languages to English

**Examples of valid item_name:**
   - "Paracetamol 500 mg tablet"
   - "Repacor Parecoxib sodium 40 mg injection"
   - "Amoxicillin trihydrate 250 mg capsule"
   - "Salbutamol 2 mg/5 ml syrup"

**Return your response strictly in the following JSON format:**

{
  "batch_and_expiry_image": [list of valid image indexes],
  "quantity_detection_images": [list of valid image indexes],
  "item_name": "string"
}
"""

image_detection_prompt= """
You are an AI assistant that analyzes images of medicine packaging.

Your task is to extract structured information from one or more images.

Please follow these steps:

### STEP 1: Detect Images with Batch Number and Expiry Date
- Identify which images **clearly show** either a Batch Number or an Expiry Date.
- Look for labels or patterns such as:
  - "Batch No", "Batch Number", "Lot", "Lot No", "Lot Number"
  - "Expiry", "Exp", "Exp Date", "Use by", "EXP", etc.
- Text may be partially visible, as long as the intent is **clear and unambiguous**.
- Return only the **indexes of images** that show either or both of these fields.
- **Indexing starts from 0.** For example, if there are 4 images, valid indexes are: 0, 1, 2, and 3.

---

### STEP 2: Identify Images Useful for Quantity Detection
- Determine which image(s) can be used to **identify the number of medicine boxes** or units in the package.
- Focus on images that clearly show the **packaging** (e.g., box stacks, blisters, container groups).
- Select **only as many images as necessary** to estimate the quantity.
  - If one or two images already provide sufficient evidence, **exclude the rest** even if they are technically valid.
- Again, return only **valid image indexes**, ranging from 0 to N-1 where N is the total number of images.

---

### STEP 3: Extract Full `item_name` of the Medicine
Extract the **full standardized name** of the medicine using visible text in the images. The `item_name` must contain:

1. **Medicine name** (e.g., Paracetamol, Amoxicillin)
2. **Active ingredient(s)** (if visible) – e.g., sodium, hydrochloride, trihydrate
3. **Dosage strength** – e.g., "500 mg", "40 mg/2 ml" (**mandatory**)
4. **Form** – e.g., tablet, capsule, injection, syrup, cream (**mandatory**)

   Expand abbreviations and normalize terminology:
   - "inj" = "injection"
   - "cap", "caps", "kapsul", "capsule" = "capsule"
   - "tab", "tablet" = "tablet"
   - Translate or normalize terms in other languages to English

**Examples of valid item_name:**
   - "Paracetamol 500 mg tablet"
   - "Repacor Parecoxib sodium 40 mg injection"
   - "Amoxicillin trihydrate 250 mg capsule"
   - "Salbutamol 2 mg/5 ml syrup"

**Return your response strictly in the following JSON format:**

{
  "batch_and_expiry_image": [list of valid image indexes],
  "quantity_detection_images": [list of valid image indexes],
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
  "
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
quantity_prompt_x = """
Role: You are an AI specialized in analyzing images to perform accurate object counting.

Task: Determine the exact total count of individual medicine packages present in the provided images.

Context:

You will be given multiple images (e.g., 3 images) showing the same stack(s) of medicine packages from different perspectives.
These perspectives include:
- A Top view (to understand the row and column arrangement or layout).
- One or more Side views (e.g., from the right, left, or front, to determine the height of the stacks).

The medicine packages are stacked, meaning one package can be placed on top of another.

Crucially: The stacks might be irregular or uneven. For example:
- A top view might suggest a 4x4 arrangement.
- However, the side view(s) might reveal that stacks in the first row are 4 packages high, while stacks in the second row are only 3 packages high.

In such a case, the total count is derived from summing the heights of each stack (e.g., 4 + 4 + ... + 3 + 3 + ...), NOT by simply calculating 4x4=16 or counting only the top visible layer.

Instructions:

---

**1. Analyze Each Image Separately**
- Use top view(s) to identify the layout of stack positions.
- Use side or angled views to determine the number of vertically stacked items per position.
- Account for irregularities in height across different stacks.
- Count only what you **clearly see** and can **verify**.

---

**2. Cross-Check Between Views**
- Validate stack positions using consistent visual cues.
- Infer missing or partially visible parts using evidence from other perspectives.
- Avoid double-counting or assuming uniform stack height.

---

**3. Final Output**
- Provide the total number of **distinct and verifiable** medicine packages.
- Only include items that are **clearly visible and confirmed** from the image set.

---

**Respond strictly in the following JSON format**:
```json
{
  "quantity": int  // Total number of verified medicine packages.
} """


quantity_prompt = """
Role: You are an AI specialized in analyzing images to accurately count pharmaceutical packages of various shapes.

Context:
You will receive one or more images of the **same pharmaceutical item**, possibly from different perspectives (e.g., top view, side view, angled). These packages may be in various **physical forms**, such as:
- Box
- Bottle
- Blister pack
- Sachet
- Tube
- Others

These packages may be **stacked** in a **2D layout** (on a single plane) or in a **3D arrangement** (multiple layers). The stacks may be **irregular**, meaning they vary in height.

Important Rules:
- Count only the **main pharmaceutical items** shown in the foreground. **Ignore background objects**.
- If only 1 image is provided, assume it shows a **2D stacked** layout.
- Use **top view(s)** to determine the grid layout (X and Y).
- Use **side or angled views** to determine the **height (Z)** of each stack.
- Do not assume the stacks are uniform; some positions may have taller or shorter stacks.
- Always count what is **clearly visible and verifiable**. Use all views to confirm positions and stack heights.
- Do not double-count items seen from multiple angles.
- Consider the **form of the item** (box, bottle, etc.) when determining stack boundaries and structure.

---

Tasks:

1. How many images do you see?
2. What type(s) of pharmaceutical item form(s) are visible? (e.g., box, bottle, sachet)
3. Is the arrangement 2D stacked or 3D stacked?

If 2D:
4. What is the X and Y grid dimension based on the visible layout?
5. How many additional grids (item packs/boxes) are in the image? (Write the positive value)
   How many missing grids (based on the lowest observed stack)? (Write the negative value)
6. Calculate the total number of medicine packages using verified visible evidence and the above data.

If 3D:
4. From each image, determine the X and Y grid dimensions (as seen from different perspectives).
5. Combine the perspectives to estimate the full 3D grid (X, Y, Z).
6. Identify any **additional** or **missing** grids due to uneven stacks.
7. Calculate the total number of verifiable medicine packages.

---

### STEP 3: Return the Final Output

Respond strictly in the following JSON format:

```json
{
  "quantity": int  // Final total count of verified medicine packages
}
"""


quantity_promptzzzz= """
You are a vision-language assistant specialized in analyzing multiple images of medication packaging. 
Your job is to estimate the total number of visible medication packages based on images taken from different perspectives. 
The packages may be of various shapes, such as:

- Square or rectangular boxes
- Cylindrical bottles (e.g., syrups)

Important conditions to consider:
- Images may show different angles (e.g., front, side, top).
- Some images may only show part of a stack (e.g., 2 boxes in front, 5 deep seen from the side → total = 10).
- The stack may be incomplete (e.g., row 1 has 4 boxes, row 2 has 3 → total = 7).
- Packages may be partially blocked or only partially visible.
- Package layout may resemble a grid or matrix structure such as 2x2, 3x3, 4x4, and so on.
- Some positions in the grid may be empty due to a package being sold or removed, so count only the visible boxes, and estimate realistically based on this structure.

Your task:
1. Carefully examine each image and identify the packages.
2. Combine visual clues from all angles to compute the most accurate total.
3. When applicable, imagine the arrangement of packages as a table/grid.
4. Consider possible gaps or holes in the grid caused by missing packages.
5. Describe your reasoning clearly.


Examples:
- Image 1 shows 2 boxes in front and image 2 shows 5 stacked behind → total = 2 × 5 = 10
- One image shows a 2-row stack: row 1 = 4, row 2 = 3 → total = 7
- A 3x3 grid is visible, but one slot is empty → total = 8

Respond strictly in the following JSON format:

```json
{
  "quantity": int  // Final total count of verified medicine packages
}

"""

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