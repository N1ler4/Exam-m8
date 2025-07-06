from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class MenuItem(Base):
    __tablename__ = "menu_items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(JSON)  # {"uz": "title", "ru": "title", "en": "title"}
    url = Column(String)
    icon = Column(String)
    order = Column(Integer, default=0)
    parent_id = Column(Integer, ForeignKey("menu_items.id"), nullable=True)
    permissions = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Self-referential relationship
    children = relationship("MenuItem", backref="parent", remote_side=[id])