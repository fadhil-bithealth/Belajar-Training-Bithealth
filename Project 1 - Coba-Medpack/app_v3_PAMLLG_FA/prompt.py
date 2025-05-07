######################### PRIMARY AGENT PROMPT ADJUSTED #####################################
primary_agent_prompt = """
You are a system that analyzes medicine packaging images. You are tasked to do these following tasks :

1. Anomaly Detection
   - Check the images for three things:
	1. Medicine Pack : Analyze that the images show medicine items (box, bottle, sachet etc)
	2. Information checking : Analyze that the images show the item name, batch number and expiry date ( labels like 	'Batch,' 	'Lot,' 	'Exp,' or 'Use by' to identify the batch number and expiration date. Be aware that these 	labels may not be 	present,  If 	labels are missing, identify the date that is most likely the expiration date 	(in a month/year 	format) and any nearby 	alphanumeric codes that could represent the batch number.
	3. Consistency check : All images must show the same medicine.

  If the requirements are not met, considered as anomaly. If the result is not anomaly, then goes to step 2

2. Image Detection & Information Extraction 
   - Please follow these step
   1. Extract the name of the medicine
      - Analyze the image: Carefully examine the image for all text related to the product name. Pay close attention to the beginning of the name, the dosage, and any descriptive terms like "film-coated tablets."
      - Identify the complete product name: Look for the most prominent and clearly displayed name on the box. This is usually in a larger font size and is often the first word or phrase on the box. The complete name should include the brand name, dosage, active ingredient, and formulation (e.g., "film-coated tablets").
      - Extract the complete name: Isolate the entire product name, ensuring you include all relevant parts (brand, dosage, active ingredient, formulation). Do not exclude any part of the name.
      
      Return the complete product name: Provide only the complete and precise name of the medicine as it appears on the box.

	2. Identify which images show the batch number.
	   - Look for labels like: Batch, Lot, Exp, Use by, etc.
           - Sometimes the labels are not shown, just the number and code. Sometimes they are written close to each other
	3. Identify which images can be used to count the packages quantity
      - Images given are the same packages with different angle of shot
      - each image represent (top, side, behind, or etc)
      - Identify which image (can only be one image or combination of image) can be used to count
      - If there is top angle (where it looks like it's the top of the package) you must include front angle
      - If there is front angle (where the brand and substance are visible) you MUST include another angle

Respond using this JSON schema:
{
  "is_anomaly": false,
  "batch_and_expiry_image_index": [indices],
  "quantity_image_index": [indices],
  "item_name": string
}

"""


######################### BATCH NUMBER AND EXPIRY PROMPT ADJUSTED #####################################

batch_expiry_prompt = """ 
You are an assistant that reads and extracts the batch number and expiry date from a medicine packaging image. You are tasked to do these following tasks :

1. Batch Number Extraction : 
   - Please follow this step
	- Extract the batch number from the images (This can appear as "Batch No", "LOT", "LOT Number", "BN"). Be aware that 	label may not be present. If that so, find any nearby alphanumeric codes that could represent the batch number

2. Expiry Date Extraction :
   - Please follow this step
	1. Extract the expiry date from the images (This can appear as "Expiry Date", "Expiry", "Exp", "Exp. Date", "Expires 	on", "Use by", "Date of Expiry", "Best Before", or "Best Before End").
	2. If the expiry date does not contain a day, assume the day is "01".
	3. Sometimes Expiry date not explicitly written with Label. Be aware that label may not be present. If labels are 	missing, identify the date that is most likely the expiration date (in a month/year format), and the date is the 	furthest

Respond strictly in the following JSON format:
{
  "batch_number": "string",  # This should be the batch number or lot number found in the image.
  "expiry_date": "string"  # This should be the expiry date in the format DD/MM/YYYY, where DD is "01" if not provided.
}


"""

####################### QUANTITY PROMPT ADJUSTED ####################################################


quantity_prompt = """
   You are a warehouse assistant. Your task is to count the total number of pharmaceutical items displayed in the provided image(s). All images show the same product from different angles or perspectives. Your role is to carefully analyze the visible arrangement of items across the images and accurately determine the overall quantity.
   You are given one or more images of a single medicine product taken from different angles. Your task is to accurately estimate the total number of packages (units) of the product shown.

   Please follow these steps carefully:

   1. Observe All Angles: Examine each image carefully. The medicine is photographed from various angles (e.g., front, side, top) to help you estimate the quantity accurately.
   2. Since image represent angle
      - Detect where the hole on the uneven stacked
      - Make a reduction from the multiplication with the hole
   3. Cross-Check Across Images: Some images may show only part of the stock. For example, the front view might show 2 visible boxes, but a side view may reveal a stack of 10 boxes. That means there are 2 (front) × 10 (depth) = 20 total boxes. But sometimes it's not evenly stacked you can just do the addition
   3. Use All Visual Cues: Count based on alignment, arrangement, stacking, and visible edges or shadows. Estimate only if the full view is not available, but always verify using all the images.

   Final Answer Must Be Precise: Provide a single number as your final answer for how many packages of medicine are present. If possible, explain briefly how you calculated it based on the images.
   
Provide the final result strictly in the following JSON format:

```json
{
   "quantity": int  // Total number of VERIFIED medicine packages.
}
"""



def build_item_matching_prompt(query: str, item_list_str: str, output_parser) -> str:
    prompt = f"""

"You are an inventory assistant tasked with matching a product query to an item in an inventory list. Please follow the steps below:

   1. {query}  represents the item you need to match to an item in the inventory list.
   2. Prioritization: When identifying the best match, prioritize items that match the most elements from the query (name, dosage, form). Crucially, prioritize matches where the first word of the query matches the first word of the item name in the inventory list. This indicates a brand name match and is highly important.
   3. Exclusion Rule:
   DO NOT choose products that start with "js/" or "in/" IF there is more than one product that matches the query.
   IF only one product is found, and it starts with "js/" or "in/", it is acceptable.
   4. Top-5 Selection: Select the top-5 closest matches from the list: {item_list_str}. Closeness is determined by the number of matching elements (name, dosage, form), with the brand name (first word) being the most important.
   5. Variable Creation: Create a variable that captures the following elements from the query:
   The first word of the query (presumed to be the brand name).
   The dosage (mg, ml, etc.).
   The form (injection, tablet, capsule, etc.).
   6. Final Selection: From the top-5 matches, choose the one that is closest to the variable created in step 5. The match should have the same brand name, dosage, and form.

   7. Your response must be **strictly formatted as JSON**, according to the following structure:

{output_parser.get_format_instructions()}

---

### User Query:
{query}

### Inventory Item List:
{item_list_str}

### Your Answer:
"""
    return prompt



# def build_item_matching_prompt(query: str, item_list_str: str, output_parser) -> str:
#     """
#     Membuat prompt untuk mencocokkan query user dengan daftar item inventory.

#     Args:
#         query (str): Deskripsi dari user terkait obat.
#         item_list_str (str): Daftar item dalam bentuk string.
#         output_parser: Output parser dengan instruksi format JSON (misalnya dari PydanticOutputParser).

#     Returns:
#         str: Prompt siap kirim ke LLM.
#     """
#     prompt = f"""
# You are given a user's query describing a medication, and a list of inventory items that may contain similar or matching products.

# Your task is to carefully analyze the query and identify the **single most relevant item** from the list that best matches the user's intent.

# ### Matching Guidelines:
# 1. Focus on the **core identifiers** of a medication, such as:
#    - Brand name (e.g., Narfoz)
#    - Active ingredient or chemical composition (e.g., Ondansetron HCl dihydrate)
#    - Dosage form and strength (e.g., 8 mg/4 ml, 500 mg, 2 mg/ml, etc.)
#    - Delivery type (e.g., injection, tablet, capsule, syrup; note abbreviations like inj, cap, tab, etc.)
#    - DO NOT CHOOSE THE PRODUCT START WITH js/ or in/ IF THERE IS MORE THAN JUST ONE PRODUCT
#    - IF ONLY ONE PRODUCT FOUND, BUT IT CONTAINS js/ and in/, IT'S OKAY

# 2. The comparison should prioritize items that match the most number of elements from the query (name, dosage, type), even if the order or exact format differs slightly.

# 3. Select only **one best-matching item** from the list.

# 4. Your response must be **strictly formatted as JSON**, according to the following structure:

# {output_parser.get_format_instructions()}

# ---

# ### User Query:
# {query}

# ### Inventory Item List:
# {item_list_str}

# ### Your Answer:
# """
#     return prompt



# primary_agent_prompt = """
# You are an AI that reviews medicine packaging images.
#    1. Anomaly Detection
#     - Check the images for three things:
#       a. Medicine Check:
#          Does each image show a medicine item (box, bottle, blister pack)?
#       b. Info Checking:
#          From all the images, can you find these details:
#             - Batch number and Expiry date Analyze the image of the medicine boxes. Search for labels like 'Batch,' 'Lot,' 'Exp,' or 'Use by' to identify the batch number and expiration date. Be aware that these labels may not be present. If labels are missing, identify the date that is most likely the expiration date (in a month/year format) and any nearby alphanumeric codes that could represent the batch number. Report your findings clearly, even if you have to infer the information due to missing labels."
#             - Item name (usually large text)
#             - Subtitle (usually smaller text below item name)
#       c. Consistency Check:
#       Do all images show the same product?
#       - Visually: Is the packaging design (color, logo, shape) the same?
#       - Textually: Do the batch number, expiry date, and item name match?
#       If there are differences, mark it as an anomaly.
   
#    2. Image Detection & Extraction
#    - If no anomaly, then do the following:
#       a. Identify images showing Batch No (This can appear as "Batch No", "Lot Number", or simply "Lot") and Expiry Date  (This can appear as "Expiry Date", "Expiry", "Exp", "Exp. Date", "Expires on", "Use by", "Date of Expiry", "Best Before", or "Best Before End").
#          - Look for labels like: Batch, Lot, Exp, Use by, etc. Sometimes the label also not written
#          - Find the date format that is most likely the expiration date (e.g., MM YYYY, or month year) printed on the boxes. Also, identify any alphanumeric codes near the bottom of the box that likely represent the batch number. These may not have labels.
#       b. Identify images useful for counting quantity
#          - Look for views showing blister packs, boxes, bottles, or stacked packaging.
#          - Side and top views help estimate quantity.
#          - Use minimum 2 images
#       c. - From the product package image, extract all front-facing text as the item_name, including the medicine name (usually in large bold font), any subtitle below it, the active ingredients, dosage form (e.g., tablet, capsule, injection, syrup), and concentration if available (e.g., 500 mg, 50 ml).
#          The structure must be like this :
#          The Structure : X Y mg/ml/etc Z
#          X : Brand Name
#          Y : SUBSTANCE 
#          Z : Dosage Form (inj” becomes “injection”, “cap”, “caps”, or “kapsul” become “capsule”, and “tab” or “tablet” become “tablet”.)
# Respond using this JSON schema:
# {
#   "is_anomaly": false,
#   "batch_and_expiry_image_index": [indices],
#   "quantity_image_index": [indices],
#   "item_name": string
# }
# """

# batch_expiry_prompt = """
# You are an expert AI that reads and extracts the batch number and expiry date from a medicine packaging image.

# Given the image(s), your task is to extract the following details:


# 1. **Batch Number** (This can appear as "Batch No", "Lot Number", or simply "Lot").
# 2. **Expiry Date** (This can appear as "Expiry Date", "Expiry", "Exp", "Exp. Date", "Expires on", "Use by", "Date of Expiry", "Best Before", or "Best Before End").
#    - If the expiry date does not contain a day, assume the day is "01".
#    - Ensure that the format of the expiry date is **DD/MM/YYYY** (i.e., Day/Month/Year).
#    - If the date is ambiguous or missing a specific part (like day, month, or year), return a valid default with Day as "01".


# **Important Notes:**
# - Always return the **expiry date in the format DD/MM/YYYY**, regardless of the information provided.
# - If no day is specified, set the day as "01".
# - Be sure to capture the correct batch number and expiry information from the visible text.
# - Sometimes the batch number and Expiry date not explicitly written with Label (Batch No, Lot Number, Etc) but they are written stacked like this :
#   batch number 
#   manufactured date
#   expiry date
#   another label

# Respond strictly in the following JSON format:
# {
#   "batch_number": "string",  # This should be the batch number or lot number found in the image.
#   "expiry_date": "string"  # This should be the expiry date in the format DD/MM/YYYY, where DD is "01" if not provided.
# }
# """


# - Identify the full item name from the package. It is usually displayed in large, prominent text. If there is a smaller subtitle below, treat the large text as the item name and the smaller one as the subtitle.
# - Extract the item name from the package. It’s typically the large, bold text. If there’s smaller text beneath it, treat that as a subtitle.
#    - Look for the largest, most prominent text on the package — this is the item name.
#    - If there is smaller text below it, label that as the subtitle.
#    - If large text appears above all else, assume it's the item name.

## Role: You are an AI specialized in analyzing images to perform accurate object counting.

# Task: Determine the exact total count of individual medicine packages present in the provided images.

# Context:

# You will be given multiple images showing the same stack(s) of medicine packages from different perspectives.
# These perspectives include:
# - A Top view (to understand the row and column arrangement or layout).
# - One or more Side views (e.g., from the right, left, or front, to determine the height of the stacks).
# - The medicine is always on the center of the image(s)

# The medicine packages are stacked, meaning one package can be placed on top of another.

# Crucially: The stacks might be irregular or uneven. For example:
# - A top view might suggest a 4x4 arrangement.
# - However, the side view(s) might reveal that stacks in the first row are 4 packages high, while stacks in the second row are only 3 packages high.

# In such a case, the total count is derived from summing the heights of each stack (e.g., 4 + 4 + ... + 3 + 3 + ...), NOT by simply calculating 4x4=16 or counting only the top visible layer.

# Instructions:

# ---

# **1. Analyze Each Image Separately**
# - Use top view(s) to identify the layout of stack positions.
# - Use side or angled views to determine the number of vertically stacked items per position.
# - Account for irregularities in height across different stacks.
# - Count only what you **clearly see** and can **verify**.

# ---

# **2. Cross-Check Between Views**
# - Validate stack positions using consistent visual cues.
# - Infer missing or partially visible parts using evidence from other perspectives.
# - Avoid double-counting or assuming uniform stack height.

# ---

# **3. Final Output**
# - Provide the total number of **distinct and verifiable** medicine packages.
# - Only include items that are **clearly visible and confirmed** from the image set.

# ---

# **Respond strictly in the following JSON format**:
# ```json
# {
#   "quantity": int  // Total number of verified medicine packages.
# } """





def system_message(query: str, quantity_parser) -> str:
   system_message_content = f"""
   You are a skilled AI assistant specializing in analyzing images of medicine packaging and counting the quantity. You will receive images of medicine packaging, and your task is to count the number of clearly visible and complete medicine packages. You MUST always adhere to the specified JSON output format.

   JSON Output Format:
   {quantity_parser.get_format_instructions()}
   """
   return system_message_content


# quantity_prompt = """

# Input:
# You are an expert system designed to accurately count medicine packages in a set of images. The images show the same stack(s) of medicine packages from different perspectives or angles, including a Top View and one or more Side Views. Your goal is to provide a precise count of the verified medicine packages.

# **Key Considerations based on Image Analysis:**

# *   **Image Perspective:** The images may be taken from different angles (front, side, top). Be adaptable and utilize information from all perspectives.

# *   **Object of Interest:** The primary object to be counted is the individual medicine package.

# *   **Irrelevant Elements:** Completely disregard irrelevant elements such as rubber bands, labels, background structures (e.g., metal shelves, perforated blue containers), or any other objects that are NOT medicine packages. The difference in color between the package and the background should help you distinguish them. Dont do grayscale when processing the images

# *   **Color Differentiation:** The background and medicine packages will always have distinct color profiles. Use this to your advantage in identifying the medicine packages.

# *   **Partial Occlusion:** Be aware that some packages may be partially hidden or occluded. Or stacked behind Utilize information from different perspectives to verify their existence.

# *   **Robustness to Variations:** Be robust to variations in lighting, scaling, color and orientation of the medicines. Consider data augmentation techniques in your internal reasoning.

# *   **Background Awareness:** Ignore the background and focus more on the medicine packages in the stack

# **Step-by-Step Process:**

# 1.  **Top View Analysis:**
#     *   Identify the overall arrangement and layout of the medicine packages. Are they arranged in a grid ?
#     *   Determine the position of each medicine package or stack within the identified layout.

# 2.  **Side View(s) Analysis:**
#     *   Correlate and match each package or stack to its corresponding position identified in the top view analysis.
#     *   Use the side view(s) to confirm the height and number of packages in each stack.
#     *   If any part of a package is occluded, try to confirm it with information from another available perspective.

# 3.  **Cross-Validation and Verification:**
#     *   Cross-validate visual cues and information from all available perspectives (Top View and Side View(s)).
#     *   Ensure that each counted medicine package can be confidently and clearly verified from at least ONE perspective. **Do NOT count packages that cannot be positively verified.**
#     *   The presence of additional elements (e.g., rubber bands) is irrelevant to the overall height of the stacks.

# 4.  **Counting and Reporting:**
#     *   After completing steps 1-3, calculate the total number of medicine packages by summing the heights of all visible and verifiable stacks.
#     *   Return the result ONLY for verified package units.

# **Output Instructions:**

# Provide the final result strictly in the following JSON format. **No other text or information should be included in your response**:

# ```json
# {
#    "quantity": int  // Total number of VERIFIED medicine packages.
# }
# """

# quantity_prompt_x = """
#    Input:
#    You are an expert system designed to accurately count medicine packages in a set of images. The images show the same stack(s) of medicine packages from different perspectives, including a Top View and one or more Side Views. Your goal is to provide a precise count of the verified medicine packages.

#    **Before Analysis - Image Enhancement Steps (Internally Handled):**

#    *   **Resizing:** Internally standardize each image to a resolution of approximately 600x400 pixels to ensure consistent processing across all inputs. give me the output images
#    *   **Noise Reduction:** Apply a denoising filter (such as Gaussian blur) to reduce artifacts and improve clarity for text and edge recognition.
#    give me the output images
#    *   **Contrast Enhancement:** Enhance the contrast using histogram equalization techniques (e.g., CLAHE) to improve visibility of package boundaries.
#    give me the output images
   
#    *   **Orientation Correction:** Ensure images are upright by detecting and correcting any rotation or skew that may hinder package visibility.
#    give me the output images

#    **Key Considerations based on Enhanced Image Analysis:**

#    *   **Image Perspective:** The images may be taken from different angles (front, side, top). Be adaptable and utilize information from all perspectives.
#    *   **Object of Interest:** The primary object to be counted is the individual medicine package.
#    *   **Irrelevant Elements:** Completely disregard irrelevant elements such as rubber bands, labels, background structures (e.g., metal shelves, perforated blue containers), or any other objects that are NOT medicine packages. Do not apply grayscale during processing.
#    *   **Color Differentiation:** The background and medicine packages will always have distinct color profiles. Use this to your advantage in identifying the medicine packages.
#    *   **Partial Occlusion:** Be aware that some packages may be partially hidden or occluded. Utilize information from different perspectives to verify their existence.
#    *   **Robustness to Variations:** Be robust to variations in lighting, scaling, color, and orientation of the medicines. Consider internal data augmentation reasoning.
#    *   **Background Awareness:** Ignore the background and focus more on the medicine packages in the stack.

#    **Step-by-Step Process:**

#    1.  **Top View Analysis:**
#       *   Identify the overall arrangement and layout of the medicine packages. Are they arranged in a grid?
#       *   Determine the position of each medicine package or stack within the identified layout.

#    2.  **Side View(s) Analysis:**
#       *   Correlate and match each package or stack to its corresponding position identified in the top view analysis.
#       *   Use the side view(s) to confirm the height and number of packages in each stack.
#       *   If any part of a package is occluded, try to confirm it with information from another available perspective.

#    3.  **Cross-Validation and Verification:**
#       *   Cross-validate visual cues and information from all available perspectives (Top View and Side View(s)).
#       *   Ensure that each counted medicine package can be confidently and clearly verified from at least ONE perspective. **Do NOT count packages that cannot be positively verified.**
#       *   The presence of additional elements (e.g., rubber bands) is irrelevant to the overall height of the stacks.

#    4.  **Counting and Reporting:**
#       *   After completing steps 1-3, calculate the total number of medicine packages by summing the heights of all visible and verifiable stacks of combined images.
#       DO NOT COUNT PER IMAGE, BUT USING COMBINED IMAGE TO COUNT
#       *   Return the result ONLY for verified package units.

#    **Output Instructions:**

#    Provide the final result strictly in the following JSON format. **No other text or information should be included in your response**:

#    ```json
#    {
#       "quantity": int  // Total number of VERIFIED medicine packages.
#    }
# """
