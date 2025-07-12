from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.auth.security import get_current_user
from app.models.campaign import CampaignRegistration, ProvinceTaxInfo
from app.services import province_service

router = APIRouter(prefix="/campaign", tags=["Campaign"])


# Register and show registration info + tax deduction for all provinces
@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
def register_for_campaign(
    registration_data: CampaignRegistration,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if registration_data.target_province not in province_service.PROVINCES_DB:
        raise HTTPException(status_code=404, detail="Province not found")

    user = crud.get_user_by_username(db, username=current_user["username"])
    reg = crud.create_campaign_registration(db=db, registration=registration_data, user_id=user.id)
    provinces = province_service.get_all_provinces_info()
    return {
        "registration_info": {
            "full_name": reg.full_name,
            "id_card_number": reg.id_card_number,
            "target_province": reg.target_province,
            "username": user.username,
            "email": user.email,
        },
        "tax_deductions": provinces,
        "highlight": [p for p in provinces if p["province_type"] == "เมืองรอง"]
    }

@router.get("/provinces", response_model=List[ProvinceTaxInfo])
def get_all_province_tax_info():
    return province_service.get_all_provinces_info()


@router.get("/provinces/{province_key}", response_model=ProvinceTaxInfo)
def get_province_tax_info(province_key: str):
    info = province_service.get_province_info_by_name(province_key)
    province_name = province_key
    if not info:
        eng_map = {
            "ChiangRai": "เชียงราย",
            "Nan": "น่าน",
            "Lamphun": "ลำพูน",
            "Trat": "ตราด",
            "Satun": "สตูล",
            "Bangkok": "กรุงเทพมหานคร",
            "ChiangMai": "เชียงใหม่",
            "Phuket": "ภูเก็ต",
            "Songkhla": "สงขลา"
        }
        thai_name = eng_map.get(province_key)
        if thai_name:
            info = province_service.get_province_info_by_name(thai_name)
            province_name = thai_name()
    if not info:
        province_list = list(province_service.PROVINCES_DB.items())
        try:
            idx = int(province_key)
            if 0 <= idx < len(province_list):
                province_name, info = province_list[idx]
        except:
            pass
    if not info:
        raise HTTPException(status_code=404, detail="Province not found")
    return ProvinceTaxInfo(
        province_name=province_name,
        tax_reduction_percentage=info["tax_reduction"],
        province_type=info["type"]
    )