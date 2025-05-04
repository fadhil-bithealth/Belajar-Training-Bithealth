# app/core/resources.py
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from qdrant_client import QdrantClient
from dotenv import load_dotenv
load_dotenv()
import os

google_api_key = os.getenv("GOOGLE_API_KEY")


llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.0-flash",
    google_api_key=google_api_key,
    temperature=0.9,
)

llm_rag = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=google_api_key,
    temperature=0.3,
)

embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=google_api_key,
)

client = QdrantClient(
    host='localhost',
    port=6333
)
