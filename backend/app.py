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


from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy import func
from datetime import date

Base.metadata.create_all(bind=engine)

# 🚀 Create FastAPI app
app = FastAPI()

SECRET_KEY = "mysecretkey123"
ALGORITHM = "HS256"

security = HTTPBearer()

from auth import router as auth_router

app.include_router(auth_router)

# 🌍 Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="http://(localhost|127\\.0\\.0\\.1)(:[0-9]+)?",
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


# =========================================
# AUTH DEPENDENCY
# =========================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    token = credentials.credentials

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("id")

        if not user_id:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

    except JWTError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired or invalid"
        )

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user



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



# =========================================
# PROFILE API
# =========================================

@app.get("/api/profile/me")
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # ======================================
    # USER INFO
    # ======================================
    user = current_user

    # ======================================
    # TOTAL USER MESSAGES
    # ======================================
    total_messages = (

        db.query(func.count(ChatMessage.id))

        .join(
            ChatSession,
            ChatSession.id == ChatMessage.session_id
        )

        .filter(
            ChatSession.user_id == user.id,
            ChatMessage.sender == "user"
        )

        .scalar()
    ) or 0

    # ======================================
    # MEDITATION DATA
    # ======================================
    meditation_sessions = (

        db.query(MeditationSession)

        .filter(
            MeditationSession.user_id == user.id
        )

        .order_by(
            MeditationSession.created_at.desc()
        )

        .all()
    )

    total_meditation_sessions = len(
        meditation_sessions
    )

    total_meditation_minutes = sum(
        s.duration for s in meditation_sessions
    )

    recent_sessions = meditation_sessions[:5]

    recent_sessions_payload = []

    for session in recent_sessions:

        recent_sessions_payload.append({

            "exercise": session.exercise,

            "duration": session.duration,

            "date": session.created_at.strftime(
                "%d %b %Y"
            )
        })

    # ======================================
    # DAILY STREAK
    # ======================================
    meditation_dates = sorted(
        list(
            set(
                s.created_at.date()
                for s in meditation_sessions
            )
        ),
        reverse=True
    )

    streak = 0

    current_day = datetime.utcnow().date()

    while current_day in meditation_dates:

        streak += 1
        current_day -= timedelta(days=1)

    # ======================================
    # MOOD ENTRIES
    # ======================================
    mood_entries = (

        db.query(MoodEntry)

        .filter(
            MoodEntry.user_id == user.id
        )

        .order_by(
            MoodEntry.created_at.asc()
        )

        .all()
    )

    total_mood_entries = len(mood_entries)

    mood_map = {
        "😊": 90,
        "😐": 60,
        "😔": 30,
        "😰": 20,
        "😡": 10
    }

    # ======================================
    # LAST 7 DAYS MOOD DATA
    # ======================================
    mood_by_day = {}

    for entry in mood_entries:

        entry_day = entry.created_at.date()

        if entry_day not in mood_by_day:
            mood_by_day[entry_day] = []

        mood_by_day[entry_day].append(
            mood_map.get(entry.mood, 50)
        )

    last_7_days = []

    for i in range(6, -1, -1):

        day = datetime.utcnow().date() - timedelta(days=i)

        values = mood_by_day.get(day, [])

        avg = round(sum(values) / len(values)) if values else 0

        last_7_days.append({

            "day": day.strftime("%a"),

            "value": avg
        })

    # ======================================
    # DAYS USING APP
    # ======================================
    days_using_app = (
        datetime.utcnow().date()
        - user.created_at.date()
    ).days

    # ======================================
    # FINAL RESPONSE
    # ======================================
    return {

        "user": {

    "id": user.id,

    "name": user.name,

    "email": user.email,

    "created_at": user.created_at,

    "dark_mode": user.dark_mode,

    "notifications": user.notifications,

    "email_reminders": user.email_reminders,

    "privacy_mode": user.privacy_mode,

    "language": user.language
},

        "stats": {

            "messages_sent": total_messages,

            "meditation_sessions":
                total_meditation_sessions,

            "total_meditation_minutes":
                total_meditation_minutes,

            "current_streak":
                streak,

            "mood_entries_logged":
                total_mood_entries,

            "days_using_app":
                max(days_using_app, 1)
        },

        "mood_trends":
            last_7_days,

        "recent_meditations":
            recent_sessions_payload
    }

from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

# =========================================
# UPDATE PROFILE
# =========================================

class UpdateProfileRequest(BaseModel):

    name: str
    email: str


@app.put("/api/profile/update")
def update_profile(
    req: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    existing_email = db.query(User).filter(
        User.email == req.email,
        User.id != current_user.id
    ).first()

    if existing_email:

        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    current_user.name = req.name
    current_user.email = req.email

    db.commit()

    return {
        "success": True,
        "message": "Profile updated successfully"
    }


# =========================================
# UPDATE SETTINGS
# =========================================

class SettingsRequest(BaseModel):

    dark_mode: bool
    notifications: bool
    email_reminders: bool
    privacy_mode: bool
    language: str


@app.put("/api/profile/settings")
def update_settings(
    req: SettingsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    current_user.dark_mode = req.dark_mode

    current_user.notifications = req.notifications

    current_user.email_reminders = req.email_reminders

    current_user.privacy_mode = req.privacy_mode

    current_user.language = req.language

    db.commit()

    return {
        "success": True
    }


# =========================================
# CHANGE PASSWORD
# =========================================

class PasswordRequest(BaseModel):

    old_password: str
    new_password: str


@app.put("/api/profile/change-password")
def change_password(
    req: PasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    valid = pwd_context.verify(
        req.old_password[:72],
        current_user.password
    )

    if not valid:

        raise HTTPException(
            status_code=400,
            detail="Old password incorrect"
        )

    current_user.password = pwd_context.hash(
        req.new_password[:72]
    )

    db.commit()

    return {
        "success": True,
        "message": "Password updated"
    }


# =========================================
# EXPORT USER DATA
# =========================================

@app.get("/api/profile/export")
def export_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    meditations = db.query(
        MeditationSession
    ).filter(
        MeditationSession.user_id == current_user.id
    ).all()

    moods = db.query(
        MoodEntry
    ).filter(
        MoodEntry.user_id == current_user.id
    ).all()

    return {

        "user": {
            "name": current_user.name,
            "email": current_user.email,
        },

        "meditations": [

            {
                "exercise": m.exercise,
                "duration": m.duration,
                "created_at": m.created_at
            }

            for m in meditations
        ],

        "moods": [

            {
                "mood": mood.mood,
                "created_at": mood.created_at
            }

            for mood in moods
        ]
    }


# =========================================
# DELETE ACCOUNT
# =========================================

@app.delete("/api/profile/delete")
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    db.query(ChatMessage).filter(
        ChatMessage.session_id.in_(

            db.query(ChatSession.id).filter(
                ChatSession.user_id == current_user.id
            )
        )
    ).delete(synchronize_session=False)

    db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).delete()

    db.query(MoodEntry).filter(
        MoodEntry.user_id == current_user.id
    ).delete()

    db.query(MeditationSession).filter(
        MeditationSession.user_id == current_user.id
    ).delete()

    db.delete(current_user)

    db.commit()

    return {
        "success": True,
        "message": "Account deleted"
    }



# =========================================
# UPDATE PROFILE API
# =========================================

class UpdateProfileRequest(BaseModel):

    name: str
    email: str


@app.put("/api/profile/update")
def update_profile(
    req: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # check email already exists
    existing_email = db.query(User).filter(
        User.email == req.email,
        User.id != current_user.id
    ).first()

    if existing_email:

        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    # check username already exists
    existing_name = db.query(User).filter(
        User.name == req.name,
        User.id != current_user.id
    ).first()

    if existing_name:

        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    current_user.name = req.name
    current_user.email = req.email

    db.commit()

    return {
        "success": True,
        "message": "Profile updated successfully"
    }



# 🟢 Test route
@app.get("/")
def home():
    return {"status": "Backend is running 🚀"}