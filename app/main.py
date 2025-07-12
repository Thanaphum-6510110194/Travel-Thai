from fastapi import FastAPI
from app.routers import users, campaign
from app import db_models
from app.database import engine

# สร้างตารางทั้งหมดในฐานข้อมูล
db_models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Thai Travel Campaign API",
    version="1.0.0",
)

app.include_router(users.router)
app.include_router(campaign.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Thai Travel Campaign API"}