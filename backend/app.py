from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# from emotion_classifier import EmotionClassifier
# from rag import retrieve_context

from database import Base, engine, SessionLocal
from models import ChatSession, ChatMessage
from fastapi import Depends
from sqlalchemy.orm import Session

from langgraph_main import app as langgraph_app, config
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

# # 🧠 Load ML model once
# classifier = EmotionClassifier()

# 📩 Request format from frontend
class ChatRequest(BaseModel):
    message: str
    chat_id: int | None = None


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
    chat_id = req.chat_id

    result = langgraph_app.invoke(
    {
        "messages": [HumanMessage(content=text)]
    },
    config=config
)

    reply = result["messages"][-1].content

    # create new chat session
    if chat_id is None:
        session = ChatSession(
            user_id=1,
            title=text[:30]
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        chat_id = session.id

    # save user message
    user_message = ChatMessage(
        session_id=chat_id,
        sender="user",
        content=text
    )

    # save bot reply
    bot_message = ChatMessage(
        session_id=chat_id,
        sender="bot",
        content=reply
    )

    db.add(user_message)
    db.add(bot_message)
    db.commit()

    return {
        "chat_id": chat_id,
        "emotion": emotion,
        "reply": reply
    }

@app.get("/history/{user_id}")
def get_history(user_id: int, db: Session = Depends(get_db)):
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .all()
    )

    result = []

    for s in sessions:
        messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == s.id)
            .all()
        )

        result.append({
            "date": "Today",
            "exercise": s.title,
            "duration": len(messages)
        })

    return {
        "totalSessions": len(result),
        "totalMinutes": sum(r["duration"] for r in result),
        "streak": len(result),
        "sessions": result
    }


@app.get("/api/get_chats")
def get_chats(db: Session = Depends(get_db)):
    chats = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == 1)
        .order_by(ChatSession.created_at.desc())
        .all()
    )

    return [
        {
            "id": c.id,
            "title": c.title
        }
        for c in chats
    ]

@app.get("/api/get_messages/{chat_id}")
def get_messages(chat_id: int, db: Session = Depends(get_db)):
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == chat_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    return {
        "chat_id": chat_id,
        "messages": [
            {
                "sender": m.sender,
                "text": m.content
            }
            for m in messages
        ]
    }

class DeleteChatRequest(BaseModel):
    chat_id: int


@app.post("/api/delete_chat")
def delete_chat(req: DeleteChatRequest, db: Session = Depends(get_db)):
    chat = db.query(ChatSession).filter(
        ChatSession.id == req.chat_id
    ).first()

    if not chat:
        return {"success": False}

    db.query(ChatMessage).filter(
    ChatMessage.session_id == req.chat_id
).delete()

    db.delete(chat)
    db.commit()

    return {"success": True}


class RenameChatRequest(BaseModel):
    chat_id: int
    title: str



@app.post("/api/rename_chat")
def rename_chat(req: RenameChatRequest, db: Session = Depends(get_db)):
    chat = db.query(ChatSession).filter(
        ChatSession.id == req.chat_id
    ).first()

    if not chat:
        return {"success": False}

    chat.title = req.title
    db.commit()

    return {"success": True}




# 🟢 Test route
@app.get("/")
def home():
    return {"status": "Backend is running 🚀"}