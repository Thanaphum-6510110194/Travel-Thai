from datetime import timedelta
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.security import (ACCESS_TOKEN_EXPIRE_MINUTES,
                               create_access_token, get_current_user,
                               get_password_hash, verify_password)
from app.models.user import Token, UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["Users"])

# In-memory user database for demonstration
fake_users_db: Dict[str, Dict[str, str]] = {}

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    if user.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    hashed_password = get_password_hash(user.password)
    fake_users_db[user.username] = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
    }
    return UserRead(username=user.username, email=user.email)

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    user_data = fake_users_db.get(current_user["username"])
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead(username=user_data["username"], email=user_data["email"])