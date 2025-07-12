# app/models/campaign.py
from pydantic import BaseModel, Field

class CampaignRegistration(BaseModel):
    full_name: str
    id_card_number: str = Field(..., pattern=r"^\d{13}$")
    target_province: str

class ProvinceTaxInfo(BaseModel):
    province_name: str
    tax_reduction_percentage: float
    province_type: str