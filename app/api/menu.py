from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List
from ..core.deps import get_db, get_current_user
from ..models.menu import MenuItem
from ..schemas.menu import MenuItemCreate, MenuItemResponse
from ..core.security import check_permission

router = APIRouter()

@router.get("", response_model=List[MenuItemResponse])
async def get_menu(lang: str = "uz", db: Session = Depends(get_db)):
    menu_items = db.query(MenuItem).filter(
        MenuItem.parent_id == None,
        MenuItem.is_active == True
    ).order_by(MenuItem.order).all()
    return menu_items

@router.get("/{menu_id}", response_model=MenuItemResponse)
async def get_menu_item(menu_id: int, db: Session = Depends(get_db)):
    menu_item = db.query(MenuItem).filter(MenuItem.id == menu_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return menu_item

@router.post("", response_model=MenuItemResponse)
async def create_menu_item(
    menu_item: MenuItemCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not check_permission(current_user, "write"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db_menu_item = MenuItem(**menu_item.dict())
    db.add(db_menu_item)
    db.commit()
    db.refresh(db_menu_item)
    return db_menu_item

@router.put("/{menu_id}", response_model=MenuItemResponse)
async def update_menu_item(
    menu_id: int,
    menu_item: MenuItemCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not check_permission(current_user, "write"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db_menu_item = db.query(MenuItem).filter(MenuItem.id == menu_id).first()
    if not db_menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    for key, value in menu_item.dict().items():
        setattr(db_menu_item, key, value)
    db.commit()
    db.refresh(db_menu_item)
    return db_menu_item

@router.delete("/{menu_id}")
async def delete_menu_item(
    menu_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not check_permission(current_user, "delete"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db_menu_item = db.query(MenuItem).filter(MenuItem.id == menu_id).first()
    if not db_menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    db.delete(db_menu_item)
    db.commit()
    return {"message": "Menu item deleted successfully"}