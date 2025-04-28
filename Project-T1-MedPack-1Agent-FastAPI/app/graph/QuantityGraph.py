from langgraph.graph import StateGraph
from langchain_core.messages import HumanMessage
from app.utils.prompts import quantity_prompt
from app.utils.parser import quantity_parser
from config.setting import env
from langchain_google_genai import ChatGoogleGenerativeAI
from app.schemas.quantity_schema import QuantityResult

class QuantityGraph:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=env.google_api_key,
        )

    async def detect_quantity(self, image_inputs) -> QuantityResult:
        messages = [HumanMessage(content=[{"type": "text", "text": quantity_prompt}] + image_inputs)]
        response = self.llm.invoke(messages)
        parsed = quantity_parser.parse(response.content)
        return QuantityResult(**parsed)

quantityGraph = QuantityGraph()
