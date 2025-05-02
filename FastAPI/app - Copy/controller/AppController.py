from config.setting import env
from app.utils.HttpResponseUtils import response_success, response_error
from langchain_google_genai import ChatGoogleGenerativeAI
from app.utils.AgentTools import get_weather
from langgraph.prebuilt import create_react_agent

class AppController:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="models/gemini-2.0-flash", google_api_key=env.google_api_key)
        pass
    def get_app_info(self):
        return {
            "app_name": env.app_name,
            "app_version": env.app_version,
        }
    
    def echo_data(self, user):
        try:
            return response_success(user)
        except Exception as e:
            return response_error(e)
    
    def chat_with_gemini(self, message):
        try:
            # Assuming you have a function to handle the chat with Gemini
            result = self.llm.invoke(message)
            return response_success(result)
        except Exception as e:
            return response_error(e)
        
    def react_agent(self, message):
        try:
            tools = [get_weather]
            result = self.llm.invoke(message)
            graph = create_react_agent(self.llm, tools=tools)

            inputs = {"messages": 
                [("user", message)]
            }
            result = graph.invoke(inputs)
            return response_success(result)
        except Exception as e:
            print(e)
            return response_error(e)

appController = AppController()