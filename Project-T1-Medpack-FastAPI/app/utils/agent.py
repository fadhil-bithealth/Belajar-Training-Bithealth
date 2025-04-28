
from langchain_core.messages import HumanMessage
from app.utils.prompts import anomaly_check_prompt, image_detection_prompt, final_output_prompt
from app.utils.parser import anomaly_parser, detection_parser, final_parser
from config.llm_config import llm
from app.schemas.response_schema import AnomalyResult, DetectionResult, FinalOutput

def run_anomaly_check(images) -> AnomalyResult:
    messages = [HumanMessage(content=[
        {"type": "text", "text": anomaly_check_prompt}
    ] + images)]
    
    response = llm.invoke(messages)
    parsed = anomaly_parser.parse(response.content)
    result = AnomalyResult(**parsed)

    detection_result: DetectionResult = run_image_detection(images)
    if not detection_result.batch_and_expiry_image:
        result.is_anomaly = True

    return result

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
