from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional

class MenuItemBase(BaseModel):
    title: Dict[str, str]
    url: str
    icon: str = ""
    order: int = 0
    parent_id: Optional[int] = None
    permissions: List[str] = ["read"]

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemResponse(MenuItemBase):
    id: int
    is_active: bool
    created_at: datetime
    children: List['MenuItemResponse'] = []
    
    class Config:
        from_attributes = True

# Update forward reference
MenuItemResponse.model_rebuild()
