
from app.services import province_service
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud
from app.auth import security
from app.database import get_db
from app.models.user import Token, UserCreate, UserRead
from fastapi import Body

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(
    user: UserCreate = Body(...),
    target_provinces: list = Body(...),
    db: Session = Depends(get_db)
):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    # Store target provinces in user record (assumes db_models.User has a field for this)
    user_dict = user.dict()
    user_dict["target_provinces"] = target_provinces
    return crud.create_user(db=db, user=user_dict)

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserRead)
def read_users_me(current_user: dict = Depends(security.get_current_user), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=current_user["username"])
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/provinces", response_model=list)
def get_available_provinces():
    return province_service.get_available_provinces_with_type()

@router.get("/registrations", response_model=list)
def get_registered_users(db: Session = Depends(get_db)):
    users = db.query(crud.db_models.User).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email
        } for u in users
    ]

@router.get("/tax-info")
def get_tax_info():
    primary = []
    secondary = []
    for province, info in province_service.PROVINCES_DB.items():
        entry = {
            "province": province,
            "type": info["type"],
            "tax_reduction": info["tax_reduction"]
        }
        if info["type"] == "เมืองหลัก":
            primary.append(entry)
        elif info["type"] == "เมืองรอง":
            secondary.append(entry)
    return {
        "primary_cities": primary,
        "secondary_cities": secondary
    }