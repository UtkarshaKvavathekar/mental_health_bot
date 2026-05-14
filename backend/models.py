from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    email = Column(String(120), unique=True, index=True)
    password = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(150), default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan"
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    sender = Column(String(20))   # user / bot
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")

class MoodEntry(Base):

    __tablename__ = "moods"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer)

    mood = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

class MeditationSession(Base):

    __tablename__ = "meditation_sessions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer)

    exercise = Column(String)

    duration = Column(Integer)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )