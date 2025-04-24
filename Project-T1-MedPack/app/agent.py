# app/agent.py

from langchain_core.messages import HumanMessage # type: ignore
from app.prompts import anomaly_check_prompt, image_detection_prompt, final_output_prompt
from app.parser import anomaly_parser, detection_parser, final_parser
from app.config import llm
from app.schema import AnomalyResult, DetectionResult, FinalOutput

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
    messages = [HumanMessage(content=[
        {"type": "text", "text": final_output_prompt},
        {"type": "text", "text": f"Anomaly Result: {anomaly_result.model_dump_json()}"},
        {"type": "text", "text": f"Detection Result: {detection_result.model_dump_json() if detection_result else '{}'}"},
    ])]

    response = llm.invoke(messages)
    parsed = final_parser.parse(response.content)
    return FinalOutput(**parsed)
