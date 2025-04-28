# app/agent.py

from langchain_core.messages import HumanMessage # type: ignore
from app.prompts import (
    anomaly_check_prompt, 
    image_detection_prompt, 
    final_output_prompt,
    batch_expiry_prompt,  # tambahkan
    quantity_prompt           # tambahkan
)
from app.parser import (
    anomaly_parser, 
    detection_parser, 
    final_parser,
    batch_and_expiry_parser,  # tambahkan
    quantity_parser           # tambahkan
)
from app.config import llm
from app.schema import (
    AnomalyResult, 
    DetectionResult, 
    FinalOutput,
    BatchAndExpiryResult,     # tambahkan
    QuantityResult            # tambahkan
)

def run_anomaly_check(images) -> AnomalyResult:
    messages = [HumanMessage(content=[
        {"type": "text", "text": anomaly_check_prompt}] + images)]
    
    response = llm.invoke(messages)
    parsed = anomaly_parser.parse(response.content)
    return AnomalyResult(**parsed)

def run_image_detection(images) -> DetectionResult:
    messages = [HumanMessage(content=[
        {"type": "text", "text": image_detection_prompt}] + images)]
    
    response = llm.invoke(messages)
    parsed = detection_parser.parse(response.content)
    return DetectionResult(**parsed)

def run_output_formatting(anomaly_result: AnomalyResult, detection_result: DetectionResult = None) -> FinalOutput:
    messages = [HumanMessage(content=[{
        "type": "text", 
        "text": final_output_prompt},
        {
            "type": "text", 
            "text": f"Anomaly Result: {anomaly_result.model_dump_json()}"},
        {
            "type": "text", 
            "text": f"Detection Result: {detection_result.model_dump_json() if detection_result else '{}'}"},
    ])]

    response = llm.invoke(messages)
    parsed = final_parser.parse(response.content)
    return FinalOutput(
        batch_number=parsed["batch_number"],
        expiry_date=parsed["expiry_date"],
        item_name=parsed["item_name"],
        quantity=parsed["quantity"]
    )

# NEW: Tambahan dua fungsi baru

def run_batch_and_expiry_agent(images) -> BatchAndExpiryResult:
    messages = [HumanMessage(content=[
        {"type": "text", "text": batch_expiry_prompt}] + images)]
    
    response = llm.invoke(messages)
    parsed = batch_and_expiry_parser.parse(response.content)
    return BatchAndExpiryResult(**parsed)

def run_quantity_agent(images) -> QuantityResult:
    messages = [HumanMessage(content=[
        {"type": "text", "text": quantity_prompt}] + images)]
    
    response = llm.invoke(messages)
    parsed = quantity_parser.parse(response.content)
    return QuantityResult(**parsed)
