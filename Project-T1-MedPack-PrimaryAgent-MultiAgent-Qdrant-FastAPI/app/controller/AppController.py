from config.setting import env
from app.utils.HttpResponseUtils import response_success, response_error
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
import os


class AppController:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="models/gemini-2.0-flash", google_api_key=env.google_api_key)
        self.embedding_model = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
)
        pass
    def get_app_info(self):
        return {
            "app_name": env.app_name,
        }

appController = AppController()