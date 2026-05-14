from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# from emotion_classifier import EmotionClassifier
# from rag import retrieve_context
from datetime import datetime, timedelta
from database import Base, engine, SessionLocal
from models import User, ChatSession, ChatMessage, MoodEntry
from fastapi import Depends
from sqlalchemy.orm import Session

from langgraph_main import app as langgraph_app, config
from langchain_core.messages import HumanMessage
from collections import defaultdict
from models import MeditationSession


Base.metadata.create_all(bind=engine)

# 🚀 Create FastAPI app
app = FastAPI()

from auth import router as auth_router

app.include_router(auth_router)

# 🌍 Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
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

    user_id: int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/chat")
def chat(req: ChatRequest, db: Session = Depends(get_db)):

    text = req.message
    chat_id = req.chat_id
    

    existing_chat = None

    if chat_id is not None:

        existing_chat = db.query(ChatSession).filter(

        ChatSession.id == chat_id,

        ChatSession.user_id == req.user_id

    ).first()

    if not existing_chat:

        chat_id = None

    try:

        result = langgraph_app.invoke(
            {
                "messages": [HumanMessage(content=text)]
            },
            config=config
        )

        reply = result["messages"][-1].content

    except Exception as e:

        print("CHAT ERROR:", e)

        return {
            "reply": f"Backend Error: {str(e)}"
        }

    # create new chat session
    if chat_id is None:

        session = ChatSession(

            user_id=req.user_id,

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
        "reply": reply
    }


@app.get("/api/get_chats/{user_id}")
def get_chats(
    user_id: int,
    db: Session = Depends(get_db)
):

    chats = (

        db.query(ChatSession)

        .filter(
            ChatSession.user_id == user_id
        )

        .order_by(
            ChatSession.created_at.desc()
        )

        .all()
    )

    return [
        {
            "id": c.id,
            "title": c.title
        }

        for c in chats
    ]

@app.get("/api/get_messages/{chat_id}/{user_id}")
def get_messages(
    chat_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):

    chat = db.query(ChatSession).filter(

        ChatSession.id == chat_id,

        ChatSession.user_id == user_id

    ).first()

    if not chat:

        return {
            "messages": []
        }

    messages = (

        db.query(ChatMessage)

        .filter(
            ChatMessage.session_id == chat_id
        )

        .order_by(
            ChatMessage.created_at.asc()
        )

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

@app.get("/dashboard/{user_id}")
def get_dashboard(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(
    User.id == user_id
).first()

    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .all()
    )

    total_sessions = len(sessions)

    total_messages = 0

    for s in sessions:

        count = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == s.id)
            .count()
        )

        total_messages += count

    moods = (
    db.query(MoodEntry)
    .filter(MoodEntry.user_id == user_id)
    .all()
)

    mood_map = {
    "😊": 90,
    "😐": 60,
    "😔": 30,
    "😰": 20,
    "😡": 10
}

    days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

    mood_history = []

    


    daily_moods = defaultdict(list)


# Group moods by date
    for mood in moods:

        mood_date = mood.created_at.date()

        mood_value = mood_map.get(mood.mood, 50)

        daily_moods[mood_date].append(mood_value)


# Create averaged mood history
    mood_history = []

    sorted_dates = sorted(daily_moods.keys())[-7:]


    for i, date in enumerate(sorted_dates):

        values = daily_moods[date]

        avg_value = sum(values) / len(values)

        mood_history.append({

            "day": date.strftime("%a"),

            "value": round(avg_value)

    })
    
    # Calculate average mood
    if mood_history:

        avg_mood = sum(
            item["value"] for item in mood_history
        ) / len(mood_history)

    else:

        avg_mood = 50
    
    # Calculate average mood
    if mood_history:

        avg_mood = sum(
            item["value"] for item in mood_history
        ) / len(mood_history)

    else:

        avg_mood = 50


# Dynamic insight generation
    if avg_mood >= 80:

        insight = (
        "You’ve been feeling emotionally positive this week 🌿"
        )

    elif avg_mood >= 60:

        insight = (
        "Your emotional balance looks stable and improving."
    )

    elif avg_mood >= 40:

        insight = (
        "You may have experienced some emotional ups and downs recently."
    )

    else:

        insight = (
        "You seem emotionally overwhelmed lately. Consider taking mindful breaks 💙"
    )
        
    active_dates = set()

    for session in sessions:
        active_dates.add(session.created_at.date())

    streak = 0

    today = datetime.utcnow().date()

    while today in active_dates:

        streak += 1

        today = today - timedelta(days=1)

    return {

        "name": user.name if user else "User",

        "meditationMinutes": total_sessions * 5,

        "chatMessages": total_messages,

        "streak": streak,

        "todayFocus": "Take mindful pauses while working 🌿",

        "focusTip": "Try 5 minutes of breathing between coding sessions.",

        "insight": insight,

        "moodHistory": mood_history
    }

class MoodRequest(BaseModel):
    user_id: int
    mood: str

@app.get("/history/{user_id}")
def get_history(user_id: int,
                db: Session = Depends(get_db)):

    sessions = (

        db.query(MeditationSession)

        .filter(
            MeditationSession.user_id == user_id
        )

        .order_by(
            MeditationSession.created_at.desc()
        )

        .all()
    )

    result = []
    exercise_names = {

    "breathing": "🌬 Breathing Exercise",

    "grounding": "🌱 Grounding Exercise",

    "bodyscan": "🧘 Body Scan",

    "affirmations": "✨ Positive Affirmations",

    "sleep": "🌙 Sleep Relaxation",

    "reframe": "💭 Thought Reframing"
}

    for s in sessions:

        result.append({

            "date":
                s.created_at.strftime("%d %b %Y"),

            "exercise": exercise_names.get(
                s.exercise,
                s.exercise
            ),
            "duration":
                s.duration
        })

    return {

        "totalSessions": len(result),

        "totalMinutes":
            sum(r["duration"] for r in result),

        "streak": len(result),

        "sessions": result
    }

@app.delete("/history/{user_id}")
def clear_history(
    user_id: int,
    db: Session = Depends(get_db)
):

    db.query(MeditationSession).filter(
        MeditationSession.user_id == user_id
    ).delete()

    db.commit()

    return {
        "success": True
    }
@app.post("/mood")
def save_mood(req: MoodRequest, db: Session = Depends(get_db)):

    mood = MoodEntry(
        user_id=req.user_id,
        mood=req.mood
    )

    db.add(mood)
    db.commit()

    return {"success": True}

class MeditationRequest(BaseModel):

    user_id: int
    exercise: str
    duration: int

@app.post("/meditation/save")
def save_meditation(
    req: MeditationRequest,
    db: Session = Depends(get_db)
):

    session = MeditationSession(

        user_id=req.user_id,

        exercise=req.exercise,

        duration=req.duration
    )

    db.add(session)

    db.commit()

    return {"success": True}




# 🟢 Test route
@app.get("/")
def home():
    return {"status": "Backend is running 🚀"}