import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pwdlib import PasswordHash

from app.database import get_db
from models.user import User
from schemas.user import UserCreate, UserResponse, UserLogin


router = APIRouter(prefix="/auth", tags=["Authentication"])

password_hash = PasswordHash.recommended()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


@router.post("/register", response_model=UserResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):

    # Check if email already exists
    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Hash the password
    hashed_password = password_hash.hash(user_data.password)

    # Create new user
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hashed_password,
        role=user_data.role,
        phone=user_data.phone,
        address=user_data.address
    )

    # Save user to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/login")
def login_user(user_data: UserLogin, db: Session = Depends(get_db)):

    # Find user by email
    user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    # Check if user exists
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Verify password
    if not password_hash.verify(user_data.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Set token expiration time
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # Create JWT token
    token_data = {
        "sub": str(user.id),
        "exp": expire
    }

    access_token = jwt.encode(
        token_data,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer"
    }