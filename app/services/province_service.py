def get_available_provinces_with_type():
    return [
        {
            "province_name": name,
            "province_type": data["type"]
        }
        for name, data in PROVINCES_DB.items()
    ]
PROVINCES_DB = {
    "เชียงราย": {"type": "เมืองรอง", "tax_reduction": 20.0},
    "น่าน": {"type": "เมืองรอง", "tax_reduction": 20.0},
    "ลำพูน": {"type": "เมืองรอง", "tax_reduction": 20.0},
    "ตราด": {"type": "เมืองรอง", "tax_reduction": 20.0},
    "สตูล": {"type": "เมืองรอง", "tax_reduction": 20.0},
    "กรุงเทพมหานคร": {"type": "เมืองหลัก", "tax_reduction": 15.0},
    "เชียงใหม่": {"type": "เมืองหลัก", "tax_reduction": 15.0},
    "ภูเก็ต": {"type": "เมืองหลัก", "tax_reduction": 15.0},
    "สงขลา": {"type": "เมืองหลัก", "tax_reduction": 15.0},
}

def get_all_provinces_info():
    return [
        {
            "province_name": name,
            "tax_reduction_percentage": data["tax_reduction"],
            "province_type": data["type"],
        }
        for name, data in PROVINCES_DB.items()
    ]

def get_province_info_by_name(name: str):
    return PROVINCES_DB.get(name)