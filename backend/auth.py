import traceback
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt

from database import SessionLocal
from models import User
from schemas import UserCreate, UserLogin

router = APIRouter()

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

SECRET_KEY = "mysecretkey123"
ALGORITHM = "HS256"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- SIGNUP ----------------
@router.post("/auth/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    try:
        existing = db.query(User).filter(User.email == user.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="User already exists")

        # ✅ FIX: limit password length
        safe_password = user.password[:72]

        hashed_password = pwd_context.hash(safe_password)

        new_user = User(
            name=user.name,
            email=user.email,
            password=hashed_password
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {"message": "User created successfully"}

    except Exception as e:
        print("ERROR:", e)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- LOGIN ----------------
@router.post("/auth/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.email == user.email).first()

    # ✅ FIX: same truncation during verify
    if not db_user or not pwd_context.verify(user.password[:72], db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt.encode(
        {"id": db_user.id, "email": db_user.email},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "access_token": token,
        "user_id": db_user.id,
        "email": db_user.email
    }