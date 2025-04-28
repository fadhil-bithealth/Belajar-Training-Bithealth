from langgraph.graph import StateGraph
from langchain_core.messages import HumanMessage
from app.utils.prompts import batch_expiry_prompt
from app.utils.parser import batch_expiry_parser
from config.setting import env
from langchain_google_genai import ChatGoogleGenerativeAI
from app.schemas.batch_expiry_schema import BatchExpiryResult

class BatchExpiryGraph:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=env.google_api_key,
        )

    async def detect_batch_and_expiry(self, image_inputs) -> BatchExpiryResult:
        messages = [HumanMessage(content=[{"type": "text", "text": batch_expiry_prompt}] + image_inputs)]
        response = await self.llm.ainvoke(messages)  # <-- harus await ainvoke
        parsed = batch_expiry_parser.parse(response.content)  # parse langsung
        return BatchExpiryResult(**parsed)


batchExpiryGraph = BatchExpiryGraph()
