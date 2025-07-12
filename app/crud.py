from sqlalchemy.orm import Session
from . import db_models
from .auth import security
from .models import user as user_models
from .models import campaign as campaign_models

# --- User CRUD ---

def get_user_by_username(db: Session, username: str):
    return db.query(db_models.User).filter(db_models.User.username == username).first()

def create_user(db: Session, user: user_models.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = db_models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Campaign CRUD ---

def create_campaign_registration(db: Session, registration: campaign_models.CampaignRegistration, user_id: int):
    db_registration = db_models.CampaignRegistration(
        **registration.model_dump(),
        owner_id=user_id
    )
    db.add(db_registration)
    db.commit()
    db.refresh(db_registration)
    return db_registration