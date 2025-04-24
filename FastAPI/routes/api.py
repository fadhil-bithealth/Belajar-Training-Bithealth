from fastapi import APIRouter, Header, Depends
from typing import Annotated
import app.schemas as schemas
from app.controller.AppController import appController

router = APIRouter()

@router.get("/")
def get_action():
    return appController.get_app_info()

@router.post("/echo")
def post_echo_action(user: schemas.UserSchema):
    return appController.echo_data(user)

@router.post("/chat")
def chat(payload: schemas.ChatSchema):
    return appController.chat_with_gemini(payload.message)

@router.post("/react-agent")
def chat(payload: schemas.ChatSchema):
    return appController.react_agent(payload.message)