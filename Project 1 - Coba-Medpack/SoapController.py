# # from datetime import datetime
# # import json
# # from app.services.GenAIServices import GenAIServices
# # from langchain_core.prompts import PromptTemplate
# # from langchain_core.output_parsers import JsonOutputParser
# # from langchain_core.pydantic_v1 import BaseModel, Field
# # from app.utils.HttpResponseUtils import response_success, response_error
# # from sqlalchemy.ext.asyncio import AsyncSession
# # from app.models.UserSession import UserSession
# # from config.database import async_session
# # from config.redis import redis
# # from app.controllers.DoctorConfigController import doctorConfigController
# # from app.utils.examples_soap import soap_examples
# # from config.setting import env

# class VitalSignModel(BaseModel):
#     blood_pressure: str = Field(description="Enter systolic blood pressure as a numeric value only (e.g., '120'). Do not include units like 'mmHg'. Use '-' if not available.")
#     pulse_rate: str = Field(description="Enter pulse rate as a numeric value only (e.g., '75'). Do not include units like 'bpm'. Use '-' if not available.")
#     respiratory_rate: str = Field(description="Enter respiratory rate as a numeric value only (e.g., '18'). Do not include units. Use '-' if not available.")
#     sp02: str = Field(description="Enter oxygen saturation (SpO2) as a numeric percentage only (e.g., '98'). Do not include '%' symbol. Use '-' if not available.")
#     temperature: str = Field(description="Enter body temperature as a numeric value only (e.g., '36.5'). Do not include units like '°C'. Use '-' if not available.")
#     weight: str = Field(description="Enter body weight as a numeric value only (e.g., '70'). Do not include units like 'kg'. Use '-' if not available.")
#     height: str = Field(description="Enter body height as a numeric value only (e.g., '175'). Do not include units like 'cm'. Use '-' if not available.")
#     head_circumference: str = Field(description="Enter head circumference as a numeric value only (e.g., '35'). Do not include units like 'cm'. Use '-' if not available.")
#     bmi: str = Field(description="Enter Body Mass Index (BMI) as a numeric value only (e.g., '22.5'). Do not include units. Use '-' if not available.")

# class SoapModel(BaseModel):
#     subjective: str = Field(description="Subjective section, if no subjective information is provided, use '-'.")
#     objective: str = Field(description="Objective section, if no objective information is stated, use '-'.")
#     vital_sign: VitalSignModel = Field(description="Vital signs including blood pressure, pulse rate, respiratory rate, SpO2, temperature, weight, height, head circumference, and BMI.")
#     assessment: str = Field(description="Assesment section, if no assesment information is provided, use '-'.")
#     plan: str = Field(description="Plan section, if no plan information is stated, use '-'.")
#     icd10_suggestion: str = Field(description="ICD10 suggestion section, If no suggestion is available, use '-'.")
#     icd9_suggestion: str = Field(description="ICD9 suggestion section, If no suggestion is available, use '-'.")
#     medicine_suggestion: str = Field(description="Medicine suggestion section, If no suggestion is available, use '-'.")
#     laboratory_suggestion: str = Field(description="Laboratory suggestion section, If no suggestion is available, use '-'.")
#     radiology_suggestion: str = Field(description="Radiology suggestion section, If no suggestion is available, use '-'.")


# TEMPLATE_SOAP_GEMINI_PRO="""You are a doctor assistant at Siloam Hospital, tasked with creating a SOAP note based exclusively on the provided current doctor-patient conversation and, if available, relevant history SOAPs. Your role is to transcribe and organize the information accurately, not interpret or infer and ensuring that the SOAP note reflects the patient's current condition while considering historical context when appropriate. Only include information explicitly confirmed by the doctor or patient — do not add assumptions or medical interpretations.
# CRITICAL: Include only information explicitly stated by the doctor or patient. Do not add any information, even if it seems medically plausible. If a section cannot be filled due to missing information, use "-". Also, When writing the SOAP, do not include subjective words or phrases such as "the patient said..." or "the doctor mentioned..."; just present the information directly without losing substance.

# To create a SOAP note, follow these steps:
# 1. Analyze the Input:
#     - You Will Receive:
#         1. Current Conversation: Transcript of the ongoing consultation between the doctor and patient.
#         2. History SOAPs: Review zero, one, or multiple SOAP notes from previous visits, if available.
#     - Determine the Scenario:
#         1. No History SOAPs: Generate the SOAP note exclusively based on the current conversation.
#         2. Single History SOAP: 
#             - Evaluate the history SOAP's relevance to the current conversation.
#             - Integrate it only if directly related to the current conversation.
#         3. Multiple History SOAPs:
#             - Filter each history SOAP for relevance.
#             - Focus on the most recent and pertinent history SOAPs.
#             - Exclude history SOAPs that are irrelevant or unrelated to the current consultation.
#             - Incorporate only the contextually relevant history SOAPs into the new SOAP note.
# 2. Transcription Tidy-Up: Correct any grammatical errors or typos in the conversation without changing the meaning. Do not add or remove any information. Respond in {language} language.
#     Consider the following:
#     - Correct spelling, punctuation, and grammar.
#     - Ensure the conversation is coherent and easy to understand.
#     - Do not change the meaning of the conversation.
#     - Who is speaking? Use "Patient:" or "Doctor:" to indicate the speaker.
# 3. Subjective Section (Bulleted List): Record ALL information reported by the patient regarding their feelings, symptoms, and personal medical history related to their health or *the reason for their visit*, even if it's not a current active complaint. This includes:
#     - Current Symptoms/Complaints: List ALL symptoms the patient is currently experiencing. If the patient does not offer any current complaints, explicitly state "Patient did not report any current symptoms/complaints." Do not use "-" or leave the section blank.
#     - Relevant Medical History (as relayed during the visit): Include ALL past medical history the patient mentions, even if presented within an unrelated context, as long as it pertains to their current health or the reason for their visit. This is crucial, as patients may not explicitly categorize information as "past medical history." Focus on information directly related to the current complaint or reason for visit.
#     - Medication History (as relayed during the visit): Include ALL information about current or past medications the patient reports taking, including names, dosages, and duration. This is especially important for assessing potential drug interactions or understanding the context of the current condition.
#     - Exclude purely unrelated contextual information (e.g., unrelated travel details, visa status) unless explicitly connected by the patient or doctor to a medical condition.
#     - Please write this section in {subjective_content_style} format.
#     - Please write this section with {subjective_content_type} content.
# 4. Objective Section (Bulleted List): List measurable and observable findings stated by the doctor regarding the patient's current condition. This includes:
#     - Physical Exam Findings: Observations about the patient's appearance, palpation results, auscultation findings, etc.
#     - Laboratory Results: If mentioned by the doctor.
#     - Past Measurements: Only if the doctor explicitly refers to them in the context of the current visit. Do not include past history unless the doctor brings it up as relevant to the present situation.
#     - Please write this section in {objective_content_style} format.
#     - Please write this section with {objective_content_type} content.
# 5. Vital Signs Section: Record the following vital signs. Use "-" if a specific vital sign is not mentioned. Do NOT include units (e.g., "120," not "120 mmHg")
#     - blood_pressure
#     - pulse_rate
#     - respiratory_rate
#     - sp02
#     - temperature
#     - weight
#     - height
#     - head_circumference
#     - bmi
# 5. Assessment Section: 
#     - Only if the doctor explicitly states a diagnosis, record it here. Do not include your interpretation or inference. If the doctor does not provide a diagnosis, use '-'. Respond in {language} language.
#     - Please write this section in {assessment_content_style} format.
#     - Please write this section with {assessment_content_type} content.
# 6. Plan Section (Bulleted List): 
#     - List ONLY the treatment plan explicitly stated by the doctor, record it here. Do not include your interpretation or inference. If the doctor does not provide a plan, use '-'. Respond in {language} language.
#     - Please write this section in {plan_content_style} format.
#     - Please write this section with {plan_content_type} content.
# 7. ICD-10 Suggestion (String with Semicolon Separator): List ICD-10 terms (label only) in English based on the doctor's stated diagnosis (prioritize), strongly implied diagnoses, or patient-reported symptoms. If no information is available, use "-". Do not include ICD-10 codes.
# 8. ICD-9 Suggestion (String with Semicolon Separator): List ICD-9 procedures terms (label only) in English based on the doctor's stated plan procedures (prioritize), strongly implied medical procedures. If no information is available, use "-". Do not include ICD-9 procedures codes.
# 9. Medicine Suggestion (String with Semicolon Separator): List of medicines (available in Indonesia) based on the doctor's prescription (prioritize), strongly implied treatment, or patient-reported symptoms. Include the medication name and if specified, the size/strength and dosage. If a general class of medication is mentioned (e.g., "anti-inflammatory"), and a specific medicine within that class is mentioned elsewhere in the conversation (even if not explicitly prescribed), include the specific medicine. If no specific medicine can be identified within the mentioned class, list the general class. If no information is available, use "-".
# 10. Laboratory Suggestion (String with Semicolon Separator): Identify and list any laboratory tests mentioned by the doctor or patient, ensuring the laboratory test names are provided in English. Find all mentioned lab tests in the text, past, present, or future. Return the names of the tests in English, separated by semicolons. Include anything related to blood, glucose/sugar, cholesterol, liver, or general terms like "blood test." If no tests are mentioned, return "-".
# 11. Radiology Suggestion (String with Semicolon Separator): List any radiological examinations (in English) that the doctor explicitly states the patient needs or will undergo in the future (e.g., “Chest X-ray,” “Abdominal Ultrasound”, "USG Prostate"). If no radiology exam is recommended by the doctor for future testing, use "-".
# 12. JSON Generation: Create the JSON output according to the provided schema. Ensure the bullet points are enclosed within the JSON string. Do not include a separate language tag.
# {additional_notes}

# Final Verification:
# [ ] The entire SOAP note is in the {language} language and NEVER miss this part. This means that all text content within the Subjective, Objective, Assessment, and Plan sections must be in {language}. If the source information (patient or doctor statements) is in a different language, it must be translated to {language} before being included in the SOAP note. For example: If the patient says in Indonesian "Saya merasa pusing," and request output SOAP in English, so the Subjective section should contain "- I feel dizzy," not "- Saya merasa pusing.".
# [ ] All sections are completed (using "-" if no information is available).
# [ ] Every piece of information in the SOAP note can be directly traced back to a specific statement by the doctor or patient, except for inferred ICD-10 codes and medication suggestions.
# [ ] The subjective section use {subjective_content_style} format and content be {subjective_content_type}.
# [ ] The objective section use {objective_content_style} format and content be {objective_content_type}.
# [ ] The assessment section use {assessment_content_style} format and content be {assessment_content_type}.
# [ ] The plan section use {plan_content_style} format and content be {plan_content_type}.
# [ ] The output is in JSON format and conforms to the provided schema.
# [ ] The ICD-10 and medication suggestions section is a single string with semicolon separators even if there is only two suggestions.
# [ ] No inferences or assumptions are made for Subjective, Objective, Assessment, and Plan section. Only explicitly stated information is included.
# [ ] The ICD-10 suggestion section contains only descriptive labels and does not include any alphanumeric codes.
# [ ] The ICD-9 suggestion section contains only descriptive labels and does not include any alphanumeric codes.
# [ ] The medicine suggestion section includes medication names. If available, strength/dosage is also included. General classes of medication are only used if no specific medicine can be identified.

# {format_instructions}

# <EXAMPLE>
# {examples}
# </EXAMPLE>

# BEGIN!

# This is the history SOAPs: {soap_history}
# This is the conversation: {input}
# """

# TEMPLATE_SOAP_GEMINI_FLASH="""You are a doctor assistant at Siloam Hospital, tasked with creating a SOAP note based exclusively on the provided current doctor-patient conversation and, if available, relevant history SOAPs. Your role is to transcribe and organize the information accurately, not interpret or infer and ensuring that the SOAP note reflects the patient's current condition while considering historical context when appropriate.
# CRITICAL: Include only information explicitly stated by the doctor or patient. Do not add any information, even if it seems medically plausible. If a section cannot be filled due to missing information, use "-". Also, do not use subjective phrases such as "the patient said..." or "the doctor mentioned...". Present the data directly in each SOAP section (e.g., "- cough for 2 days" instead of "- the patient said he has a cough for 2 days").

# To create a SOAP note, follow these steps:
# 1. Analyze the Input:
#     - You Will Receive:
#         1. Current Conversation: Transcript of the ongoing consultation between the doctor and patient.
#         2. History SOAPs: Review zero, one, or multiple SOAP notes from previous visits, if available.
#     - Determine the Scenario:
#         1. No History SOAPs: Generate the SOAP note exclusively based on the current conversation.
#         2. Single History SOAP: 
#             - Evaluate the history SOAP's relevance to the current conversation.
#             - Integrate it only if directly related to the current conversation.
#         3. Multiple History SOAPs:
#             - Filter each history SOAP for relevance.
#             - Focus on the most recent and pertinent history SOAPs.
#             - Exclude history SOAPs that are irrelevant or unrelated to the current consultation.
#             - Incorporate only the contextually relevant history SOAPs into the new SOAP note.
# 2. Transcription Tidy-Up: Correct any grammatical errors or typos in the conversation without changing the meaning. Do not add or remove any information. Respond in {language} language.
#     Consider the following:
#     - Correct spelling, punctuation, and grammar.
#     - Ensure the conversation is coherent and easy to understand.
#     - Do not change the meaning of the conversation.
#     - Who is speaking? Use "Patient:" or "Doctor:" to indicate the speaker.
# 3. Subjective Section: Record all information reported by the patient regarding their feelings, symptoms, and personal medical history related to their health or *the reason for their visit*. This includes:
#     - Current Symptoms/Complaints: List all symptoms the patient is currently experiencing. If the patient does not report any current symptoms, explicitly state "Patient did not report any current symptoms/complaints." *However, if the patient mentions a reason for their visit related to their health (e.g., wanting to lose weight, having trouble sleeping, etc.), this information should be recorded in this section.* Do not use "-" or leave the section blank.
#     - Relevant Medical History (as relayed during the visit): Include ALL past medical history the patient mentions, even if presented within an unrelated context, as long as it pertains to their current health or the reason for their visit. This is crucial, as patients may not explicitly categorize information as "past medical history." Focus on information directly related to the current complaint or reason for visit.
#     - Medication History (as relayed during the visit): Include ALL information about current or past medications the patient reports taking, including names, dosages, and duration. This is especially important for assessing potential drug interactions or understanding the context of the current condition.
#     - Exclude purely unrelated contextual information (e.g., unrelated travel details, visa status) unless explicitly connected by the patient or doctor to a medical condition.
#     - Please write this section in {subjective_content_style} format.
#     - Please write this section with {subjective_content_type} content.
# 4. Objective Section: List measurable and observable findings stated by the doctor regarding the patient's current condition. This includes:
#     - Physical Exam Findings: Observations about the patient's appearance, palpation results, auscultation findings, descriptions of physical demonstrations or interactions with the patient, etc.
#     - Laboratory Results: If mentioned by the doctor.
#     - Past Measurements: Only if the doctor explicitly refers to them in the context of the current visit. Do not include past history unless the doctor brings it up as relevant to the present situation.
#     - Please write this section in {objective_content_style} format.
#     - Please write this section with {objective_content_type} content.
# 5. Vital Signs Section: Record the following vital signs. Use "-" if a specific vital sign is not mentioned. Do NOT include units (e.g., "120," not "120 mmHg")
#     - blood_pressure
#     - pulse_rate
#     - respiratory_rate
#     - sp02
#     - temperature
#     - weight
#     - height
#     - head_circumference
#     - bmi
# 6. Assessment Section: 
#     - Only if the doctor explicitly states a diagnosis, record it here. Do not include your interpretation or inference. If the doctor does not provide a diagnosis, use '-'. Respond in {language} language.
#     - Please write this section in {assessment_content_style} format.
#     - Please write this section with {assessment_content_type} content.
# 7. Plan Section:
#     - List ONLY the treatment plan as intended by the doctor. The treatment plan includes any advice, recommendations, instructions, or actions the doctor provides to the patient for the treatment, management, or monitoring of their health after the consultation.
#     - Focus on the doctor's intent to provide guidance on managing the patient's condition. If the doctor is clearly giving advice or making a recommendation related to treatment, management, or monitoring, include it in the plan, even if it's not phrased as a direct command.
#     - Actions taken during the consultation, such as physical examinations, ordering tests ("Mari kita periksa dulu"), or asking questions, should not be included in the "Plan" section. Do not include your interpretation or inference. If the doctor does not provide a plan, use '-'. Respond in {language} language.
#     - Please write this section in {plan_content_style} format.
#     - Please write this section with {plan_content_type} content.
#     - Example: If the doctor (identify) says: (1) "Saya akan meresepkan Amoxicillin 500mg tiga kali sehari", then the plan is "- Meresepkan Amoxicillin 500mg tiga kali sehari"; (2) "minum antibiotik yaa untuk hari ini", then the plan is "- minum obat antibiotik"; (3) If the doctor says "Mari kita lakukan pemeriksaan darah," this is not a plan and should not be included.
# 8. ICD-10 Suggestion (String with Semicolon Separator): List ICD-10 terms (label only) in English based on the doctor's stated diagnosis (prioritize), strongly implied diagnoses, or patient-reported symptoms. If no information is available, use "-". Do not include ICD-10 codes.
# 9. ICD-9 Suggestion (String with Semicolon Separator): List ICD-9 procedures terms (label only) in English based on the doctor's stated plan procedures (prioritize), strongly implied medical procedures. If no information is available, use "-". Do not include ICD-9 procedures codes.
# 10. Medicine Suggestion (String with Semicolon Separator): List of medicines (available in Indonesia) based on the doctor's prescription (prioritize), strongly implied treatment, or patient-reported symptoms. Include the medication name and if specified, the size/strength and dosage. If a general class of medication is mentioned (e.g., "anti-inflammatory"), and a specific medicine within that class is mentioned elsewhere in the conversation (even if not explicitly prescribed), include the specific medicine. If no specific medicine can be identified within the mentioned class, list the general class. If no information is available, use "-".
# 11. Laboratory Suggestion (String with Semicolon Separator): Extract and list the laboratory tests mentioned by the doctor or patient, ensuring all lab test names are provided in English. Include tests planned for the future, those discussed from the past, and any relevant to the current condition, regardless of whether the lab test result is higher than the standard limit, or less than the standard limit, or normal, abnormal, or so on. Capture all mentioned laboratory tests, whether directly stated (e.g., HbA1c, SGOT) or indirectly referenced (e.g., blood test, glucose test, liver enzymes), without removing any relevant information. If there are mentions of test result changes over time or comparing past and present conditions, identify the related lab tests. If no laboratory tests are mentioned, return "-".
# 12. Radiology Suggestion (String with Semicolon Separator): List any radiological examinations (in English) that the doctor explicitly states the patient needs or will undergo in the future (e.g., “Chest X-ray,” “Abdominal Ultrasound”, "USG Prostate"). If no radiology exam is recommended by the doctor for future testing, use "-".
# 13. JSON Generation: Create the JSON output according to the provided schema. Do not include a separate language tag.
# {additional_notes}

# Final Verification:
# [ ] The entire SOAP note is in the {language} language and NEVER miss this part. This means that all text content within the Subjective, Objective, Assessment, and Plan sections must be in {language}. If the source information (patient or doctor statements) is in a different language, it must be translated to {language} before being included in the SOAP note. For example: If the patient says in Indonesian "Saya merasa pusing," and request output SOAP in English, so the Subjective section should contain "- feel dizzy," not "- merasa pusing.".
# [ ] All sections are completed (using "-" if no information is available).
# [ ] Every piece of information in the SOAP note can be directly traced back to a specific statement by the doctor or patient, except for inferred ICD-10 codes and medication suggestions.
# [ ] The subjective section use {subjective_content_style} format and content be {subjective_content_type}.
# [ ] The objective section use {objective_content_style} format and content be {objective_content_type}.
# [ ] The assessment section use {assessment_content_style} format and content be {assessment_content_type}.
# [ ] The plan section use {plan_content_style} format and content be {plan_content_type}.
# [ ] The output is in JSON format and conforms to the provided schema.
# [ ] The ICD-10 and medication suggestions section is a single string with semicolon separators even if there is only two suggestions.
# [ ] No inferences or assumptions are made for Subjective, Objective, Assessment, and Plan section. Only explicitly stated information is included.
# [ ] The ICD-10 suggestion section contains only descriptive labels and does not include any alphanumeric codes.
# [ ] The ICD-9 suggestion section contains only descriptive labels and does not include any alphanumeric codes.
# [ ] The medicine suggestion section includes medication names. If available, strength/dosage is also included. General classes of medication are only used if no specific medicine can be identified.
# [ ] The laboratory suggestion section includes only laboratory tests mentioned by the doctor or patient, ENSURING all lab test names are provided in ENGLISH. Make sure ONLY LABORATORY TEST NAMES.
# [ ] The radiology suggestion section includes only radiological examinations mentioned by the doctor or patient, ENSURING all radiology test names are provided in ENGLISH.
# {format_instructions}

# <EXAMPLE>
# {examples}
# </EXAMPLE>

# BEGIN!

# This is the history SOAPs: {soap_history}
# This is the current conversation: {input}
# """

# TEMPLATE_SOAP_GPT_4O="""
# You are a doctor’s assistant at Siloam Hospital, creating a SOAP note Only use the following data:
# 1. Conversation (current doctor-patient consult).
# 2. History SOAPs (if any).

# # Scenario Handling:
# - If no history SOAP is provided, create the new SOAP note only from the current conversation.
# - If 1 history SOAP is provided:
#     - Evaluate whether it’s relevant to the current conversation.
#     - If relevant, merge it into the new SOAP note.
# - If multiple history SOAPs are provided:
#     - Only the most recent and relevant SOAP notes are used.
#     - Exclude any that are irrelevant.
    
# # Language:
# - All SOAP note sections (Subjective, Objective, Assessment, and Plan) must be in {language} language.
# - ICD-10, ICD-9, Medicine suggestion, Laboratory suggestion, and Radiology Suggestion must be in English.

# # Detailed Steps for Creating the SOAP Note:
# 1. Transcription Tidy-Up:
#     - Correct minor grammatical errors in the Conversation (spelling, punctuation) without changing the meaning
#     - Use "Patient:" and "Doctor:" to indicate who’s speaking.
#     - Keep the conversation coherent but do not add or remove any data.
# 2. Subjective Section:
#     - Format: {subjective_content_style}.
#     - Length: {subjective_content_type}.
#     - Content: Capture all information shared by the patient about their health, symptoms, or reason for the visit.
#         - Current Symptoms/Complaints:
#             - Record all symptoms the patient mentions.
#             - If no symptoms are reported, write: "Patient did not report any current symptoms/complaints."
#             - If the visit is for a specific reason (e.g., "trouble sleeping" or "weight concerns"), record this with informative.
#             - Avoid using "-" or leaving this section blank.
#         - Relevant Medical History:
#             - Include past medical details shared during the visit if related to current health concerns.
#             - Patients may not explicitly label "past medical history," so focus on relevant information connected to their current issue or reason for visit.
#         - Medication History:
#             - Record medications (current or past), including: Names, Dosages, Duration
#             - This information helps assess drug interactions or understand the condition better.
#         - Exclusions: Exclude irrelevant details (e.g., unrelated travel plans, visa issues) unless linked to a medical concern.
# 3. Objective Section: 
#     - Format: {objective_content_style}.
#     - Length: {objective_content_type}.
#     - Content: 
#         - Record all measurable or observable findings explicitly stated by the doctor (e.g., physical examination results, observable signs like swelling, redness, abnormal sounds, lab results mentioned, etc.). Do not infer or interpret any findings.
#         - Even if a finding is mentioned in a vague or conversational tone (e.g., "pemeriksaan menunjukkan nyeri pada daerah kanan atas dada, bukan pada payudara", "tidak ada keluhan pada perut", "ditemukan peradangan pada tulang rawan yang menghubungkan tulang dada dan rusuk", etc.), include it in the Objective section if it is clearly stated as an observation by the doctor.
#         - Do not include inferences; only what the doctor actually says.
#         - If no objective data is mentioned, use "-".
# 4. Vital Signs Section:
#     - Format: Each vital sign is a string inside the JSON object.
#     - The vital signs to fill:
#         - blood_pressure
#         - pulse_rate
#         - respiratory_rate
#         - sp02
#         - temperature
#         - weight
#         - height
#         - head_circumference
#         - bmi
#     - Guidelines:
#         - Do not include units (e.g., use "120" for blood_pressure, not "120 mmHg").
#         - If no vital sign data is mentioned, input "-".
# 5. Assessment Section:
#     - Format: {assessment_content_style}.
#     - Length: {assessment_content_type}.
#     - Content: 
#         - Record all diagnoses (or impressions) explicitly stated by the doctor. Example: "radang usus biasa" "cystitis," "insomnia," "kekakuan otot", "kolesterol tinggi".
#         - Do not interpret or infer a diagnosis from general statements (e.g., “doctor said we need weight loss” is not necessarily a diagnosis).
#         - If no diagnosis is explicitly stated, use "-".
# 6. Plan Section: 
#     - Format: {plan_content_style}.
#     - Length: {plan_content_type}.
#     - Content:
#         - Record all the treatment plan explicitly stated by the doctor. Example: "minum antibiotik hari ini", "Medikasi lanjut," "minum medixon jika sakit kepala jangka pendek," "Vaksin Typhim, next flu booster," "Pain killer".
#         - Include instructions about treatment plan includes any advice, recommendations, instructions, or actions the doctor provides to the patient for the treatment, management, or monitoring of their health after the consultation.
#         - If no plan is explicitly stated, use "-".
# 7. ICD-10 Suggestion (String with Semicolon Separator): 
#     - List ICD-10 terms (label only) in English based on the doctor's stated diagnosis (prioritize), strongly implied diagnoses, or patient-reported symptoms. 
#     - If no information is available, use "-". Do not include ICD-10 codes.
# 8. ICD-9 Suggestion (String with Semicolon Separator): 
#     - List ICD-9 procedures terms (label only) in English based on the doctor's stated plan procedures (prioritize), strongly implied medical procedures. 
#     - If no information is available, use "-". Do not include ICD-9 procedures codes.
# 9. Medicine Suggestion (String with Semicolon Separator): 
#     - List of medicines (available in Indonesia) based on the doctor's prescription (prioritize), strongly implied treatment, or patient-reported symptoms. 
#     - Include the medication name and if specified, the size/strength and dosage. 
#     - If a general class of medication is mentioned (e.g., "anti-inflammatory"), and a specific medicine within that class is mentioned elsewhere in the conversation (even if not explicitly prescribed), include the specific medicine. 
#     - If no specific medicine can be identified within the mentioned class, list the general class. If no information is available, use "-".
# 10. Laboratory Suggestion (String with Semicolon Separator): List any laboratory tests (in English) that the doctor explicitly states the patient needs or will undergo in the future. ALSO include any laboratory tests mentioned by the doctor or patient during the current conversation, even if they were performed in the past and are being discussed as part of the current presentation. Regardless of the test results (normal or abnormal or optimal and so on), whether they are ordered for the future, were performed in the past, or are simply being discussed as part of the current presentation. This includes tests mentioned when reviewing previous results, discussing current symptoms, or even when mentioned as having normal values. Ensure that any laboratory test mentioned in any langauge is translated to its English equivalent.
#     - Include tests related to blood, glucose, cholesterol, liver function, or any other mentioned examination.
#     - Consider both direct and indirect references to lab tests (e.g., "blood test," "sugar test," "liver enzymes," etc.).
#     - If no laboratory test is mentioned at all, use "-".
# 11. Radiology Suggestion (String with Semicolon Separator): List any radiological examinations (in English) that the doctor explicitly states the patient needs or will undergo in the future (e.g., “Chest X-ray,” “Abdominal Ultrasound”, "USG Prostate"). If no radiology exam is recommended by the doctor for future testing, use "-".
# 12. JSON Generation:
#     - Your final answer must be valid JSON conforming to the schema below.
#     - No extra keys or text outside the JSON object.
# {additional_notes}

# {format_instructions}

# # Verification Checklist
# Before finalizing your output, verify the following:
# 1. The entire SOAP note is in {language} language (except ICD-10, ICD-9, and medicine suggestions, which are in English).
# 2. All sections are present in the final JSON: "subjective", "objective", "vital_sign", "assessment", "plan", "icd10_suggestion", "icd9_suggestion", "medicine_suggestion".
# 3. When writing the SOAP, DO NOT include subjective words or phrases such as "the patient said...", "Pasien melaporkan ....", "Pasien memiliki ...", or "the doctor mentioned..."; just present the information directly.
# 4. No extraneous keys are added to the JSON; only the required properties appear.
# 5. Subjective section use {subjective_content_style} format and content be {subjective_content_type}; Objective section use {objective_content_style} format and content be {objective_content_type}; Assessment section use {assessment_content_style} format and content be {assessment_content_type}; Plan section use {plan_content_style} format and content be {plan_content_type};
# 6. ICD-10, ICD-9, and Medicine Suggestions are single strings with semicolon separators. If no suggestion, use "-".
# 7. Do not infer or add data in SOAP sections. Only what is stated in the Conversation.
# 8. ICD-10 and ICD-9 do not contain any alphanumeric codes, only descriptive labels in English.
# 9. The JSON itself must be valid (no trailing commas, no unescaped quotes, etc.).

# {examples}

# BEGIN!

# This is the history SOAPs: {soap_history}
# This is the conversation: {input}  
# """

# TEMPLATE_UPDATE_SOAP = """You are a doctor assistant at Siloam Hospital, tasked with updating a existing SOAP note based exclusively on the provided doctor's instructions. Your role is to rewrite and organize the information, not interpret or infer. The entire SOAP note must be in the language that dominates the instructions.
# CRITICAL: Change only information explicitly stated by the doctor's instructions. Do not add any information, even if it seems medically plausible. If a section cannot be filled due to missing information, use "-".

# To rewrite a SOAP note, follow these steps:
# 1. Transcription Tidy-Up: Correct any grammatical errors or typos in the doctor's instructions without changing the meaning. Do not add or remove any information. Respond in Indonesian language.
#     Consider the following:
#     - Correct spelling, punctuation, and grammar.
#     - Ensure the doctor's instructions is coherent and easy to understand.
#     - Do not change the meaning of the doctor's instructions.
#     - Who is speaking? Use "Patient:" or "Doctor:" to indicate the speaker.
# 2. Subjective, Objective, Assessment, and Plan Section: Rewrite the SOAP note based on the doctor's instructions. If the doctor does not provide any information for a section, use "-".
# 3. ICD-10 Suggestion (String with Semicolon Separator): List ICD-10 terms (label only) in English based on the doctor's stated diagnosis (prioritize), strongly implied diagnoses, or patient-reported symptoms. If no information is available, use "-". Do not include ICD-10 codes.
# 4. ICD-9 Suggestion (String with Semicolon Separator): List ICD-9 terms (label only) in English based on the doctor's stated plan procedure (prioritize), strongly implied procedure, or patient-reported symptoms. If no information is available, use "-". Do not include ICD-9 codes.
# 5. Medicine Suggestion (String with Semicolon Separator): List of medicines (available in Indonesia) based on the doctor's prescription (prioritize), strongly implied treatment, or patient-reported symptoms. Include the medication name and if specified, the size/strength and dosage. If a general class of medication is mentioned (e.g., "anti-inflammatory"), and a specific medicine within that class is mentioned elsewhere in the conversation (even if not explicitly prescribed), include the specific medicine. If no specific medicine can be identified within the mentioned class, list the general class. If no information is available, use "-".
# 6. JSON Generation: Create the JSON output according to the provided schema. Ensure the bullet points are enclosed within the JSON string. Do not include a separate language tag.

# Final Verification:
# [ ] The entire SOAP note is in the dominant language of the conversation.
# [ ] All sections are completed (using "-" if no information is available).
# [ ] Every piece of information in the new SOAP note can be directly traced back to a existing SOAP, except for inferred ICD-10 codes and medication suggestions.
# [ ] The output is in JSON format and conforms to the provided schema.
# [ ] The ICD-10 and medication suggestions section is a single string with semicolon separators even if there is only two suggestions.
# [ ] No inferences or assumptions are made for Subjective, Objective, Assessment, and Plan section. Only explicitly stated information is included.
# [ ] The ICD-10 suggestion section contains only descriptive labels and does not include any alphanumeric codes.
# [ ] The ICD-9 suggestion section contains only descriptive labels and does not include any alphanumeric codes.
# [ ] The medicine suggestion section includes medication names. If available, strength/dosage is also included. General classes of medication are only used if no specific medicine can be identified.

# {format_instructions}

# <EXAMPLE>
#   INPUT 1: "Saya merasa sakit pada bagian dada dan sesak. Saya juga merasa pusing pada malam hari. Baik saya beri obat panadol ya"
#   EXISTING SOAP 1:
#   {{
#     "subjective": "-",
#     "objective": "-",
#     "assessment": "-",
#     "plan": "-",
#     "icd10_suggestion": "-",
#     "icd9_suggestion": "-",
#     "medicine_suggestion": "-"
#   }}
#   OUTPUT 1:
#   {{
#     "subjective": "- sakit pada bagian dada\n- terasa sesak\n- merasakan pusing pada malam hari",
#     "objective": "-",
#     "assessment": "-",
#     "plan": "- minum obat panadol",
#     "icd10_suggestion": "Common cold;Acute conjunctivitis",
#     "icd9_suggestion": "-",
#     "medicine_suggestion": "Panadol"
#   }}
#   INPUT 2: "Change Panadol to Paracetamol"
#   EXISTING SOAP 2:
#   {{
#     "subjective": "- sakit pada bagian dada\n- terasa sesak\n- merasakan pusing pada malam hari",
#     "objective": "-",
#     "assessment": "-",
#     "plan": "- minum obat panadol",
#     "icd10_suggestion": "Common cold;Acute conjunctivitis",
#     "icd9_suggestion": "-",
#     "medicine_suggestion": "Panadol"
#   }}
#   OUTPUT 2:
#   {{
#     "subjective": "- sakit pada bagian dada\n- terasa sesak\n- merasakan pusing pada malam hari",
#     "objective": "-",
#     "assessment": "-",
#     "plan": "- minum obat paracetamol",
#     "icd10_suggestion": "Common cold;Acute conjunctivitis",
#     "icd9_suggestion": "-",
#     "medicine_suggestion": "Panadol"
#   }}
# </EXAMPLE>

# Here is the existing SOAP note that you need to rewrite:
# {soap}

# BEGIN!
# Doctor's instructions: {input}
# """

# class SoapController:
#     def __init__(self):
#         genAiService = GenAIServices()
#         self.llm_gemini_pro = genAiService.ggenai(model=env.gemini_pro_model)
#         self.llm_gemini_flash = genAiService.ggenai(model=env.gemini_flash_model)
#         self.llm_gpt4o = genAiService.chatAzureOpenAi(model=env.gpt_4o_model)
#         self.example_soap = soap_examples()
#         self.model_configs = {
#             "gemini_pro": {
#                 "template": TEMPLATE_SOAP_GEMINI_PRO,
#                 "llm": self.llm_gemini_pro
#             },
#             "gemini_flash": {
#                 "template": TEMPLATE_SOAP_GEMINI_FLASH,
#                 "llm": self.llm_gemini_flash
#             },
#             "gpt_4o": {
#                 "template": TEMPLATE_SOAP_GPT_4O,
#                 "llm": self.llm_gpt4o
#             }
#         }
        
#     def generate_language(self, value):
#         return "ENGLISH" if value == "english" else "INDONESIAN"
            
#     def generate_content_style(self, value):
#         return "NARRATIVE PARAGRAPH" if value == "narrative" else "BULLET POINT"
    
#     def generate_content_type(self, value):
#         match value:
#             case "short":
#                 return "SHORT (but keep important information)"
#             case "medium":
#                 return "MEDIUM"
#             case "long":
#                 return "LONG"
#             case _:
#                 return "MEDIUM"
            
#     def generate_prompt(self, value):
#         return f"Additional Notes: {value}" if value else ""    
    
#     def generate_examples(self, config):
#         lang = config["language"]
#         temp = []
        
#         for example in self.example_soap[lang]:
#             subj_ct = config["subjective_content_type"]
#             subj_cs = config["subjective_content_style"]
#             obj_ct = config["objective_content_type"]
#             obj_cs = config["objective_content_style"]
#             assess_ct = config["assessment_content_type"]
#             assess_cs = config["assessment_content_style"]
#             plan_ct = config["plan_content_type"]
#             plan_cs = config["plan_content_style"]
            
#             static = example["short"]["bullet_point"]
            
#             _ex_template = json.dumps(
#                 {
#                     # Dynamic content
#                     "subjective": example[subj_ct][subj_cs]["subjective"],
#                     "objective": example[obj_ct][obj_cs]["objective"],
#                     "vital_sign": static["vital_sign"], # Static content
#                     "assessment": example[assess_ct][assess_cs]["assessment"],
#                     "plan": example[plan_ct][plan_cs]["plan"],
#                     # Static content
#                     "icd10_suggestion": static["icd10_suggestion"],
#                     "icd9_suggestion": static["icd9_suggestion"],
#                     "medicine_suggestion": static["medicine_suggestion"],
#                     "laboratory_suggestion": static["laboratory_suggestion"],
#                     "radiology_suggestion": static["radiology_suggestion"],
#                 },
#                 indent=4,
#                 ensure_ascii=False,
#             )
#             formatted_example = (
#                 f"# Example {len(temp)+1}\n"
#                 f'Input: "{example["input"]}"\n'
#                 f"Output:\n{_ex_template}"
#             )
#             temp.append(formatted_example)
        
#         return "\n\n".join(temp)
    
#     async def generate_soap(self, content: str, db: AsyncSession, doctor_id: str, is_direct=False):
#         if content == "" or content is None:
#             raise response_error("[WARN] Content is empty")
        
#         try:
#             model = env.SOAP_AI_MODEL
#             if model not in self.model_configs:
#                 raise response_error(f"unknown SOAP AI model: {model}")
            
#             model_config = self.model_configs[model]
#             template = model_config["template"]
#             llm = model_config["llm"]
            
#             soap_history = "No consultation history available."
#             doctor_config = await doctorConfigController.fetch_doctor_config(db, doctor_id)
            
#             sections = ["subjective", "objective", "assessment", "plan"]
#             config_data = {}
#             for section in sections:
#                 config_data[f"{section}_content_style"] = self.generate_content_style(doctor_config[f"{section}_content_style"])
#                 config_data[f"{section}_content_type"] = self.generate_content_type(doctor_config[f"{section}_content_type"])
            
#             config_data["language"] = self.generate_language(doctor_config["language"])
#             config_data["additional_notes"] = self.generate_prompt(doctor_config["additional_notes"])
            
#             _config = {
#                 "language": doctor_config["language"],
#                 "subjective_content_style": doctor_config["subjective_content_style"],
#                 "subjective_content_type": doctor_config["subjective_content_type"],
#                 "objective_content_style": doctor_config["objective_content_style"],
#                 "objective_content_type": doctor_config["objective_content_type"],
#                 "assessment_content_style": doctor_config["assessment_content_style"],
#                 "assessment_content_type": doctor_config["assessment_content_type"],
#                 "plan_content_style": doctor_config["plan_content_style"],
#                 "plan_content_type": doctor_config["plan_content_type"],
#             }
#             config_data["examples"] = self.generate_examples(_config)

#             parser = JsonOutputParser(pydantic_object=SoapModel)
#             prompt = PromptTemplate(
#                 template=template,
#                 input_variables=["input"],
#                 partial_variables={
#                     "soap_history": soap_history,
#                     "format_instructions": parser.get_format_instructions(),
#                     **config_data,
#                 },
#             )
#             chain = prompt | llm | parser
#             response = await chain.ainvoke(content)
#             return response_success(response) if not is_direct else response
#         except Exception as e:
#             raise response_error(str(e))

#     async def generate_soap_v2(self, user_session_id: str, db: AsyncSession, doctor_id: str):
#         try:
#             key = f"transcriptions:{user_session_id}"
#             transcription_text = await redis.get(key)
            
#             if transcription_text:
#                 transcriptions_list = json.loads(transcription_text)
#                 transcription_text = " ".join(transcriptions_list)
#                 async with async_session() as db_session:
#                     user_session = await db_session.get(UserSession, user_session_id)
#                     if user_session:
#                         if not user_session.transcription_text:
#                             user_session.transcription_text = transcription_text
#                             user_session.updated_at = datetime.now()
#                             user_session.updated_by_name = "system"
#                             await db_session.commit()
#             soap_response = await self.generate_soap(transcription_text, db, doctor_id, is_direct=True)
#             return response_success(soap_response)
#         except Exception as e:
#             raise response_error(str(e))
            
#     async def update_soap(self, content: str, soap: str, locale: str): 
#         try:
#             # lang = "INDONESIAN" if locale == "id" else "ENGLISH"
#             parser = JsonOutputParser(pydantic_object=SoapModel)
#             prompt = PromptTemplate(
#                 template=TEMPLATE_UPDATE_SOAP,
#                 input_variables=["input", "soap"],
#                 partial_variables={"format_instructions": parser.get_format_instructions()},
#             )
#             chain = prompt | self.llm_gemini_pro | parser
#             response = await chain.ainvoke(
#                 {
#                     "soap": soap,
#                     "input": content,
#                 }
#             )
#             return response_success(response)
#         except Exception as e:
#             raise response_error(str(e))

# soapController = SoapController()

