# app/agent.py
from fastapi import FastAPI, HTTPException

from langchain_core.messages import HumanMessage # type: ignore
from app.prompts import (
    anomaly_check_prompt, 
    image_detection_prompt, 
    final_output_prompt,
    batch_expiry_prompt,  # tambahkan
    quantity_prompt  ,
    primary_agent_prompt       # tambahkan
)
from app.parser import (
    anomaly_parser, 
    detection_parser, 
    final_parser,
    batch_and_expiry_parser,  # tambahkan
    quantity_parser,
    output_parser           # tambahkan
)
from app.config import llm
from app.schema import (
    AnomalyResult, 
    DetectionResult, 
    FinalOutput,
    BatchAndExpiryResult,     # tambahkan
    QuantityResult ,
    ItemMatch, 
    PrimaryAgentResult          # tambahkan
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

def run_primary_agent(images) -> PrimaryAgentResult:
    messages = [HumanMessage(content=[
        {"type": "text", "text": primary_agent_prompt}] + images)]
    
    response = llm.invoke(messages)
    try:
        print("RESPONSE:", response)
        parsed = output_parser.parse(response.content)
        return PrimaryAgentResult(**parsed)
    except Exception as e:
        print("PARSING ERROR:", e)
        print("RESPONSE:", response)
        print("RESPONSE CONTENT:", response.content)
    raise HTTPException(status_code=500, detail=f"Internal server error: {e}")



def run_batch_and_expiry_agent(images) -> BatchAndExpiryResult:
    messages = [HumanMessage(content=[
        {"type": "text", "text": batch_expiry_prompt}] + images)]

    response = llm.invoke(messages)
    
    try:
        parsed = batch_and_expiry_parser.parse(response.content)
        return BatchAndExpiryResult(**parsed)
    except Exception as e:
        print("ERROR PARSING:", e)
        print("RESPONSE CONTENT:", response.content)
        raise e


def run_quantity_agent(images) -> QuantityResult:
    messages = [HumanMessage(content=[
        {"type": "text", "text": quantity_prompt}] + images)]
    
    response = llm.invoke(messages)
    parsed = quantity_parser.parse(response.content)
    return QuantityResult(**parsed)


