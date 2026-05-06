import os
import shutil
import uuid

from fastapi import FastAPI, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

from emotion_classifier import EmotionClassifier
from langgraph_main import app as langgraph_app
from langchain_core.messages import HumanMessage

from database import Base, engine, SessionLocal
from models import ChatHistory
from auth import router as auth_router


# ================= DB INIT =================
Base.metadata.create_all(bind=engine)

# ================= APP =================
app = FastAPI()
app.include_router(auth_router)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================= MODEL =================
classifier = EmotionClassifier()


# ================= REQUEST MODELS =================
class ChatRequest(BaseModel):
    message: str
    user_id: int
    chat_id: str | None = None


class RenameChatRequest(BaseModel):
    title: str


# ================= DB SESSION =================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ================= CHAT =================
@app.post("/chat")
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    text = req.message.strip()
    user_id = req.user_id

    if not text:
        return {
            "reply": "Please type a message.",
            "chat_id": req.chat_id
        }

    chat_id = req.chat_id or str(uuid.uuid4())

    try:
        result = langgraph_app.invoke(
            {
                "messages": [HumanMessage(content=text)],
            },
            config={
                "configurable": {
                    "thread_id": chat_id
                }
            }
        )

        print("RESULT MESSAGES:", result.get("messages"))
        print("LAST MESSAGE TYPE:", type(result.get("messages", [])[-1]))

        reply = (
            result.get("messages", [])[-1].content
            if result.get("messages")
            else "Sorry, something went wrong."
        )

    except Exception as e:
        print("LangGraph error:", e)
        reply = (
            "I'm receiving too many requests right now. "
            "Please wait a moment and try again."
        )

    chat_entry = ChatHistory(
        user_id=user_id,
        chat_id=chat_id,
        message=text,
        response=reply
    )

    db.add(chat_entry)
    db.commit()

    return {
        "reply": reply,
        "chat_id": chat_id
    }


# ================= GET ALL CHATS =================
@app.get("/chats/{user_id}")
def get_chats(user_id: int, db: Session = Depends(get_db)):
    chats = (
        db.query(ChatHistory)
        .filter(ChatHistory.user_id == user_id)
        .order_by(ChatHistory.id.desc())
        .all()
    )

    grouped = {}

    for chat in chats:
        cid = chat.chat_id

        if cid not in grouped:
            grouped[cid] = {
                "chat_id": cid,
                "title": chat.title or ((chat.message[:25] + "...") if chat.message else "New Chat"),
                "last_message": chat.message,
                "messages": []
            }

        grouped[cid]["messages"].append({
            "message": chat.message,
            "response": chat.response
        })

    return list(grouped.values())


# ================= GET SINGLE CHAT =================
@app.get("/chat/{chat_id}")
def get_chat(chat_id: str, db: Session = Depends(get_db)):
    chats = (
        db.query(ChatHistory)
        .filter(ChatHistory.chat_id == chat_id)
        .order_by(ChatHistory.id.asc())
        .all()
    )

    return {
        "chat_id": chat_id,
        "messages": [
            {
                "message": c.message,
                "response": c.response
            }
            for c in chats
        ]
    }


# ================= RENAME CHAT =================
@app.put("/chat/{chat_id}/rename")
def rename_chat(
    chat_id: str,
    req: RenameChatRequest,
    db: Session = Depends(get_db)
):
    new_title = req.title.strip()

    if not new_title:
        return {"message": "Title cannot be empty"}

    first_chat = (
        db.query(ChatHistory)
        .filter(ChatHistory.chat_id == chat_id)
        .order_by(ChatHistory.id.asc())
        .first()
    )

    if not first_chat:
        return {"message": "Chat not found"}

    first_chat.title = new_title
    db.commit()

    return {
        "message": "Chat renamed successfully",
        "chat_id": chat_id,
        "title": new_title
    }


# ================= DELETE CHAT =================
@app.delete("/chat/{chat_id}")
def delete_chat(chat_id: str, db: Session = Depends(get_db)):
    db.query(ChatHistory).filter(
        ChatHistory.chat_id == chat_id
    ).delete()

    db.commit()

    return {
        "message": "Chat deleted successfully"
    }


# ================= HISTORY =================
@app.get("/history/{user_id}")
def get_history(user_id: int, db: Session = Depends(get_db)):
    chats = (
        db.query(ChatHistory)
        .filter(ChatHistory.user_id == user_id)
        .all()
    )

    sessions = []

    for chat in chats:
        sessions.append({
            "date": "Today",
            "exercise": chat.message[:30],
            "duration": max(1, len(chat.response or "") // 50)
        })

    return {
        "totalSessions": len(sessions),
        "totalMinutes": sum(s["duration"] for s in sessions),
        "streak": len(sessions),
        "sessions": sessions
    }


# ================= FILE UPLOAD =================
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1]
    unique_name = f"{uuid.uuid4()}.{ext}"

    filepath = os.path.join(UPLOAD_DIR, unique_name)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": unique_name,
        "original_name": file.filename,
        "url": f"http://127.0.0.1:8000/uploads/{unique_name}"
    }


# ================= HEALTH =================
@app.get("/")
def home():
    return {
        "status": "Backend is running 🚀"
    }