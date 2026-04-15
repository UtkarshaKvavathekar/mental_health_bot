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

    emotion = classifier.predict(text)
    context = retrieve_context(text)

    if "No relevant context found" in context:
        reply = f"""
I hear you. You're feeling {emotion['label']} right now. 💙
It's okay to feel this way. I'm here with you.
Would you like to talk more about what's troubling you?
"""
    else:
        reply = f"""
I understand you're feeling {emotion['label']}. 💙
Here is something that might help you:
{context[:500]}
Take a deep breath. You're not alone.
"""

    # ✅ SAVE CHAT (IMPORTANT)
    chat_entry = ChatHistory(
        user_id=1,  # ⚠️ TEMP (we improve later)
        message=text,
        response=reply
    )

    db.add(chat_entry)
    db.commit()

    return {
    "emotion": emotion,
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