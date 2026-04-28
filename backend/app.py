from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from emotion_classifier import EmotionClassifier
from rag import retrieve_context

from database import Base, engine
from models import User

from database import SessionLocal
from models import ChatHistory
from fastapi import Depends
from sqlalchemy.orm import Session

from langgraph_main import app as langgraph_app
from langchain_core.messages import HumanMessage

Base.metadata.create_all(bind=engine)

# 🚀 Create FastAPI app
app = FastAPI()

from auth import router as auth_router

app.include_router(auth_router)

# 🌍 Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🧠 Load ML model once
classifier = EmotionClassifier()

# 📩 Request format from frontend
class ChatRequest(BaseModel):
    message: str
    user_id:int


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 💬 API endpoint
@app.post("/chat")
def chat(req: ChatRequest, db: Session = Depends(get_db)):

    text = req.message
    user_id=req.user_id

    #  Call LangGraph instead of manual logic
    result = langgraph_app.invoke(
    {
        "messages": [HumanMessage(content=text)],
        
    },
    config={
        "configurable": {
            "thread_id": str(user_id)
        }
    }
)

    reply = result.get("messages", [])[-1].content if result.get("messages") else "Sorry, something went wrong."
    # ✅ Save chat
    chat_entry = ChatHistory(
        user_id=user_id,   # (we'll fix this later with token)
        message=text,
        response=reply
    )

    db.add(chat_entry)
    db.commit()

    return {
        "reply": reply
    }

@app.get("/history/{user_id}")
def get_history(user_id: int, db: Session = Depends(get_db)):

    chats = db.query(ChatHistory).filter(ChatHistory.user_id == user_id).all()

    sessions = []

    for chat in chats:
        sessions.append({
            "date": "Today",
            "exercise": chat.message[:30],
            "duration": len(chat.response) // 50
        })

    return {
        "totalSessions": len(sessions),
        "totalMinutes": sum([s["duration"] for s in sessions]),
        "streak": len(sessions),
        "sessions": sessions
    }


# 🟢 Test route
@app.get("/")
def home():
    return {"status": "Backend is running 🚀"}