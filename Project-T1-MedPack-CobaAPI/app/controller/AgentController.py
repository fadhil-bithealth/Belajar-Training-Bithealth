from langchain_core.messages import HumanMessage
from app.utils.prompts import anomaly_check_prompt, image_detection_prompt, final_output_prompt
from app.utils.parser import anomaly_parser, detection_parser, final_parser
from app.schemas.response_schema import AnomalyResult, DetectionResult, FinalOutput
from config.setting import env
from langchain_google_genai import ChatGoogleGenerativeAI

class AgentController:
    def __init__(self, llm):
        self.llm = llm  # Inject LLM dari AppController

    def run_anomaly_check(self, images) -> AnomalyResult:
        messages = [HumanMessage(content=[
            {"type": "text", "text": anomaly_check_prompt}
        ] + images)]

        response = self.llm.invoke(messages)
        parsed = anomaly_parser.parse(response.content)
        result = AnomalyResult(**parsed)

        detection_result: DetectionResult = self.run_image_detection(images)
        if not detection_result.batch_and_expiry_image:
            result.is_anomaly = True

        return result

    def run_image_detection(self, images) -> DetectionResult:
        messages = [HumanMessage(content=[
            {"type": "text", "text": image_detection_prompt}
        ] + images)]

        response = self.llm.invoke(messages)
        parsed = detection_parser.parse(response.content)
        return DetectionResult(**parsed)

    def run_output_formatting(self, anomaly_result: AnomalyResult, detection_result: DetectionResult = None) -> FinalOutput:
        messages = [HumanMessage(content=[
            {"type": "text", "text": final_output_prompt},
            {"type": "text", "text": f"Anomaly Result: {anomaly_result.model_dump_json()}"},
            {"type": "text", "text": f"Detection Result: {detection_result.model_dump_json() if detection_result else '{}'}"},
        ])]

        response = self.llm.invoke(messages)
        parsed = final_parser.parse(response.content)
        return FinalOutput(**parsed)
    
    def run_combined_detection_agent(images: List[dict]):
    anomaly_result = run_anomaly_check(images)
    detection_result = run_image_detection(images)

    is_anomaly = anomaly_result.is_anomaly
    if (
        not detection_result.item_name or
        not detection_result.batch_and_expiry_image or
        not detection_result.quantity_detection_images
    ):
        is_anomaly = True

    return {
        "anomaly_result": is_anomaly,
        "detection_result": detection_result.model_dump() if not is_anomaly else {}
    }


# Build LLM untuk agentController
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=env.google_api_key,
)

agentController = AgentController(llm)
