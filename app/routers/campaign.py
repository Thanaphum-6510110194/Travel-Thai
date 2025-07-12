from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.security import get_current_user
from app.models.campaign import CampaignRegistration, ProvinceTaxInfo
from app.services import province_service

router = APIRouter(prefix="/campaign", tags=["Campaign"])

# In-memory registration database
campaign_registrations: List[dict] = []

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_for_campaign(
    registration_data: CampaignRegistration,
    current_user: dict = Depends(get_current_user),
):
    if registration_data.target_province not in province_service.PROVINCES_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Province not found in the campaign list.",
        )
    
    registration_info = registration_data.model_dump()
    registration_info["username"] = current_user["username"]
    campaign_registrations.append(registration_info)

    return {
        "message": f"User '{current_user['username']}' successfully registered for travel to '{registration_data.target_province}'."
    }

@router.get("/provinces", response_model=List[ProvinceTaxInfo])
async def get_all_province_tax_info():
    provinces = province_service.get_all_provinces_info()
    return [ProvinceTaxInfo(**p) for p in provinces]

@router.get("/provinces/{province_name}", response_model=ProvinceTaxInfo)
async def get_province_tax_info(province_name: str):
    info = province_service.get_province_info_by_name(province_name)
    if not info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Province not found"
        )
    return ProvinceTaxInfo(
        province_name=province_name,
        tax_reduction_percentage=info["tax_reduction"],
        province_type=info["type"],
    )