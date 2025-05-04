primary_agent_prompt = """
Role: You are an AI that checks medicine packaging images.

TASKS:
1. **Anomaly Detection**:
   1. **Medicine Detection**
      - Does each image show a medicine product? (like a box, bottle, or blister pack)

   2. **Information Extraction**
      - Look at all images together. Can you find:
        - **Batch number**
        - **Expiry date**
        - **Item name** (usually big text)
        - **Description** (usually smaller text under the name)

   3. **Consistency Check**
      - Do all the images show the same product based on both textual and visual aspects?
        - **Visual comparison**: Check if the design (color, logo, packaging, shape) of the product matches across all images.
        - **Textual comparison**: Ensure that the batch number, expiry date, and item name match across all images.
        - **If the images show different product types, or if there are visual discrepancies (e.g., different designs, colors, logos), report it as an anomaly.**
        - If there is any inconsistency in these details, it should be flagged as an anomaly .

If Anomaly key 'is_anomaly' is True
If not Anomaly:
Respond using this JSON schema:
{
  "is_anomaly": True,
}


2. **Image Detection**:
Please follow these steps:
1. **Detect images that contain Batch Number and Expiry Date:**
   - Look for any text like "Batch No", "Lot", "Expiry", "Exp", "Use by", etc.

2. **Identify images that can be used to detect medicine quantity:**
   - Look for packaging that shows quantity: blister packs, bottles, boxes, strips, etc.
   - Images taken from different angles can provide alternative perspectives that may help in estimating the quantity more accurately — for example, showing all sides of a box, top and side views of a blister pack, or the liquid level inside a transparent bottle.
   
3. **Extract the full item_name of the medicine from the images:**
   - The `item_name` must include the following elements:
     - **Medicine name**
     - **Active ingredient(s)** (e.g., sodium, HCl) — if visible
     - **Dosage strength** (e.g., "500 mg", "40 mg/2 ml") — required
     - **Form** (e.g., tablet, capsule, injection, syrup, cream) — required

   Expand abbreviations and normalize terminology:
   - "inj" = "injection"
   - "cap", "caps", "kapsul", "capsule" = "capsule"
   - "tab", "tablet" = "tablet"

Examples of valid item_name:
- "Paracetamol 500 mg tablet"
- "Repacor Parecoxib sodium 40 mg injection"

If not Anomaly:
Respond using this JSON schema:
{
  "is_anomaly": false,
  "batch_and_expiry_image_index": [indices],
  "quantity_image_index": [indices],
  "item_name": string
}
"""

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
Role: You are an AI specialized in analyzing images to perform accurate object counting.

Task: Determine the exact total count of individual medicine packages present in the provided images.

Context:

You will be given multiple images showing the same stack(s) of medicine packages from different perspectives.
These perspectives include:
- A Top view (to understand the row and column arrangement or layout).
- One or more Side views (e.g., from the right, left, or front, to determine the height of the stacks).
- The medicine is always on the center of the image(s)

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

primary_agent_prompt = """
Role: You are an AI that checks medicine packaging images.

TASKS:
1. **Anomaly Detection**:
   1. **Medicine Detection**
      - Does each image show a medicine product? (like a box, bottle, or blister pack)

   2. **Information Extraction**
      - Look at all images together. Can you find:
        - **Batch number**
        - **Expiry date**
        - **Item name** (usually big text)
        - **Description** (usually smaller text under the name)

   3. **Consistency Check**
      - Do all the images show the same product based on both textual and visual aspects?
        - **Visual comparison**: Check if the design (color, logo, packaging, shape) of the product matches across all images.
        - **Textual comparison**: Ensure that the batch number, expiry date, and item name match across all images.
        - **If the images show different product types, or if there are visual discrepancies (e.g., different designs, colors, logos), report it as an anomaly.**
        - If there is any inconsistency in these details, it should be flagged as an anomaly .

If Anomaly key 'is_anomaly' is True
If not Anomaly:
Respond using this JSON schema:
{
  "is_anomaly": True,
}


2. **Image Detection**:
Please follow these steps:
1. **Detect images that contain Batch Number and Expiry Date:**
   - Look for any text like "Batch No", "Lot", "Expiry", "Exp", "Use by", etc.

2. **Identify images that can be used to detect medicine quantity:**
   - Look for packaging that shows quantity: blister packs, bottles, boxes, strips, etc.
   - Images taken from different angles can provide alternative perspectives that may help in estimating the quantity more accurately — for example, showing all sides of a box, top and side views of a blister pack, or the liquid level inside a transparent bottle.
   
3. **Extract the full item_name of the medicine from the images:**
   - The `item_name` must include the following elements:
     - **Medicine name**
     - **Active ingredient(s)** (e.g., sodium, HCl) — if visible
     - **Dosage strength** (e.g., "500 mg", "40 mg/2 ml") — required
     - **Form** (e.g., tablet, capsule, injection, syrup, cream) — required

   Expand abbreviations and normalize terminology:
   - "inj" = "injection"
   - "cap", "caps", "kapsul", "capsule" = "capsule"
   - "tab", "tablet" = "tablet"

Examples of valid item_name:
- "Paracetamol 500 mg tablet"
- "Repacor Parecoxib sodium 40 mg injection"

If not Anomaly:
Respond using this JSON schema:
{
  "is_anomaly": false,
  "batch_and_expiry_image_index": [indices],
  "quantity_image_index": [indices],
  "item_name": string
}
"""

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
quantity_promptz = """ 
Saya memberikan beberapa gambar yang berisi kemasan obat yang sama, difoto dari sudut pandang yang berbeda. Untuk setiap gambar yang saya berikan, lakukan hal berikut:

1.  **Analisis Gambar:** Tentukan jumlah kemasan obat yang terlihat jelas dan utuh dalam gambar tersebut.
2.  **Berikan Jawaban Sementara:** Catat jumlah kemasan untuk gambar tersebut dalam format: "Gambar [nomor gambar]: [jumlah kemasan]". Contoh: "Gambar 1: 3 kemasan"
3.  **Setelah Semua Gambar:** Setelah saya memberikan semua gambar, jumlahkan semua "Jawaban Sementara" Anda untuk mendapatkan jumlah total kemasan obat.
4.  **Berikan Jawaban Akhir:** Sajikan jawaban akhir dalam format: "Jumlah total kemasan obat: [jumlah total]".

Catatan penting:
*   Hanya hitung kemasan yang terlihat jelas dan utuh. Abaikan kemasan yang sebagian tertutup atau tidak jelas.
*   Pastikan Anda memberikan "Jawaban Sementara" untuk setiap gambar sebelum memberikan "Jawaban Akhir".

**Respond strictly in the following JSON format**:
```json
{
  "quantity": int  // Total number of verified medicine packages.
}

"""



quantity_prompt_oke= """
Role:
You are an AI that analyzes images to count the number of medicine packages.

Task:
Count the total number of medicine packages shown in multiple images. These images are taken from different angles: a top view and one or more side views.

Instructions:
1. Use the top view to identify how the medicine packages are arranged (rows and columns).
2. Use the side views to find out how many packages are stacked at each position.
3. Add the height (number of packages) at each stack position to get the total.
4. Do not guess or assume uniform stacks—only count what is clearly visible and confirmed across images.

Important:
- The medicine is centered in each image.
- Only count visible and verifiable packages.
- Do not overestimate or infer missing data.

Respond in the following JSON format only:
{
  "quantity": int  // Total number of confirmed medicine packages
}"""

def build_item_matching_prompt(query: str, item_list_str: str, output_parser) -> str:
    """
    Membuat prompt untuk mencocokkan query user dengan daftar item inventory.

    Args:
        query (str): Deskripsi dari user terkait obat.
        item_list_str (str): Daftar item dalam bentuk string.
        output_parser: Output parser dengan instruksi format JSON (misalnya dari PydanticOutputParser).

    Returns:
        str: Prompt siap kirim ke LLM.
    """
    prompt = f"""
You are given a user's query describing a medication, and a list of inventory items that may contain similar or matching products.

Your task is to carefully analyze the query and identify the **single most relevant item** from the list that best matches the user's intent.

### Matching Guidelines:
1. Focus on the **core identifiers** of a medication, such as:
   - Brand name (e.g., Narfoz)
   - Active ingredient or chemical composition (e.g., Ondansetron HCl dihydrate)
   - Dosage form and strength (e.g., 8 mg/4 ml, 500 mg, 2 mg/ml, etc.)
   - Delivery type (e.g., injection, tablet, capsule, syrup; note abbreviations like inj, cap, tab, etc.)

2. The comparison should prioritize items that match the most number of elements from the query (name, dosage, type), even if the order or exact format differs slightly.

3. Select only **one best-matching item** from the list.

4. Your response must be **strictly formatted as JSON**, according to the following structure:

{output_parser.get_format_instructions()}

---

### User Query:
{query}

### Inventory Item List:
{item_list_str}

### Your Answer:
"""
    return prompt

quantity_prompt = """
You are given multiple images of medicine packages taken from different angles.

the packages can be evenly stacked, and there is also not evenly package with the hole
example 
row 1 = 4
row 2 (above) = 3
so the packages is 7

count the packages from each angle
image 1 = how many packages
image 2 = how many packages
image n = ...

of every image, analyze it and then make the final count

"""



def system_message(query: str, quantity_parser) -> str:
   system_message_content = f"""
   You are a skilled AI assistant specializing in analyzing images of medicine packaging and counting the quantity. You will receive images of medicine packaging, and your task is to count the number of clearly visible and complete medicine packages. You MUST always adhere to the specified JSON output format.

   JSON Output Format:
   {quantity_parser.get_format_instructions()}
   """
   return system_message_content