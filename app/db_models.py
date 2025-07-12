from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    registrations = relationship("CampaignRegistration", back_populates="owner")


class CampaignRegistration(Base):
    __tablename__ = "campaign_registrations"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    id_card_number = Column(String)
    target_province = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="registrations")