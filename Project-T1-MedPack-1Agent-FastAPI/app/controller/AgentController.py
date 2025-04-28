# app/controllers/agent_controller.py

from app.graph.BatchExpiryGraph import batchExpiryGraph
from app.graph.QuantityGraph import quantityGraph

from langchain_core.messages import HumanMessage
from app.utils.prompts import (
    anomaly_check_prompt,
    image_detection_prompt,
)
from app.utils.parser import (
    anomaly_parser,
    detection_parser,
)
from app.schemas.response_schema import AnomalyResult, DetectionResult, FinalOutput
from config.setting import env
from langchain_google_genai import ChatGoogleGenerativeAI

class AgentController:
    def __init__(self, llm):
        self.llm = llm

    async def run_anomaly_check(self, images) -> AnomalyResult:
        """Check if there is an anomaly in the images."""
        messages = [HumanMessage(content=[{"type": "text", "text": anomaly_check_prompt}] + images)]
        response = await self.llm.ainvoke(messages)
        parsed = anomaly_parser.parse(response.content)
        result = AnomalyResult(**parsed)

        # Perform image detection to further verify anomaly
        detection_result: DetectionResult = await self.run_image_detection(images)
        if not detection_result.batch_and_expiry_image:
            result.is_anomaly = True

        return result

    async def run_image_detection(self, images) -> DetectionResult:
        """Detect specific important images like batch/expiry and quantity."""
        messages = [HumanMessage(content=[{"type": "text", "text": image_detection_prompt}] + images)]
        response = await self.llm.ainvoke(messages)
        parsed = detection_parser.parse(response.content)
        return DetectionResult(**parsed)

    async def run_output_formatting(self, anomaly_result: AnomalyResult, detection_result: DetectionResult, images) -> FinalOutput:
        """Format the final output based on the extracted information."""
        if not detection_result or not images:
            raise ValueError("Detection result and images must be provided.")

        # Extract batch number and expiry date via BatchExpiryGraph
        batch_images = [images[idx] for idx in detection_result.batch_and_expiry_image]
        batch_expiry_data = await batchExpiryGraph.detect_batch_and_expiry(batch_images)

        # Extract quantity via QuantityGraph
        quantity_images = [images[idx] for idx in detection_result.quantity_detection_images]
        quantity_data = await quantityGraph.detect_quantity(quantity_images)

        final_output = FinalOutput(
            item_name=detection_result.item_name,
            batch_number=batch_expiry_data.batch_number or "unknown",
            expiry_date=batch_expiry_data.expiry_date or "unknown",
            item_quantity=quantity_data.item_quantity or 0

        )

        return final_output

# Initialize LLM and build AgentController instance
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=env.google_api_key,
)

agentController = AgentController(llm)
