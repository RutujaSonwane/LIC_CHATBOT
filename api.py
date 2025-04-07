from fastapi import FastAPI
from pydantic import BaseModel
from chatbot import ask_chatbot  # Import insurance chatbot logic

app = FastAPI(title="Insurance Advisor AI API", description="API for AI-powered insurance assistant", version="1.0.0")

# Request Body Model
class QueryRequest(BaseModel):
    question: str

# 🟢 Home Route
@app.get("/")
def home():
    return {"message": "Insurance Advisor AI API is running!"}

# 🟢 Chatbot API
@app.post("/ask")
def ask_question(request: QueryRequest):
    response = ask_chatbot(request.question)
    return {"question": request.question, "answer": response}
