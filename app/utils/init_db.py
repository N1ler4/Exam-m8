from sqlalchemy.orm import Session
from ..models.user import User
from ..models.menu import MenuItem
from ..core.security import get_password_hash
from ..database import SessionLocal

def init_db():
    db = SessionLocal()
    
    if not db.query(User).filter(User.username == "admin").first():
        admin_user = User(
            username="admin",
            email="admin@tmsiti.uz",
            hashed_password=get_password_hash("admin123"),
            permissions=["read", "write", "delete", "manage_users"]
        )
        db.add(admin_user)
    
    if not db.query(User).filter(User.username == "editor").first():
        editor_user = User(
            username="editor",
            email="editor@tmsiti.uz",
            hashed_password=get_password_hash("editor123"),
            permissions=["read", "write"]
        )
        db.add(editor_user)
    
    if not db.query(MenuItem).first():
        menu_items = [
            MenuItem(
                title={"uz": "Institut", "ru": "Институт", "en": "Institute"},
                url="/institut",
                icon="building",
                order=1,
                permissions=["read"]
            ),
            MenuItem(
                title={"uz": "Me'yoriy hujjatlar", "ru": "Нормативные документы", "en": "Regulatory Documents"},
                url="/documents",
                icon="file-text",
                order=2,
                permissions=["read"]
            ),
            MenuItem(
                title={"uz": "Faoliyat", "ru": "Деятельность", "en": "Activities"},
                url="/activities",
                icon="briefcase",
                order=3,
                permissions=["read"]
            ),
            MenuItem(
                title={"uz": "Xabarlar", "ru": "Новости", "en": "News"},
                url="/news",
                icon="newspaper",
                order=4,
                permissions=["read"]
            ),
            MenuItem(
                title={"uz": "Bog'lanish", "ru": "Контакты", "en": "Contacts"},
                url="/contacts",
                icon="phone",
                order=5,
                permissions=["read"]
            )
        ]
        
        for item in menu_items:
            db.add(item)
            
        db.commit()
        
        institut_id = db.query(MenuItem).filter(MenuItem.url == "/institut").first().id
        documents_id = db.query(MenuItem).filter(MenuItem.url == "/documents").first().id
        
        submenus = [
            MenuItem(
                title={"uz": "Institut haqida", "ru": "Об институте", "en": "About Institute"},
                url="/institut/about",
                icon="info",
                order=1,
                parent_id=institut_id,
                permissions=["read"]
            ),
            MenuItem(
                title={"uz": "Rahbariyat", "ru": "Руководство", "en": "Leadership"},
                url="/institut/leadership",
                icon="users",
                order=2,
                parent_id=institut_id,
                permissions=["read"]
            ),
            MenuItem(
                title={"uz": "Tashkiliy tuzilma", "ru": "Организационная структура", "en": "Organizational Structure"},
                url="/institut/structure",
                icon="sitemap",
                order=3,
                parent_id=institut_id,
                permissions=["read"]
            ),
            MenuItem(
                title={"uz": "Qonun, qaror va farmonlar", "ru": "Законы, постановления и указы", "en": "Laws, Resolutions and Decrees"},
                url="/documents/laws",
                icon="gavel",
                order=1,
                parent_id=documents_id,
                permissions=["read"]
            ),
            MenuItem(
                title={"uz": "Shaharsozlik normalari va qoidalari", "ru": "Градостроительные нормы и правила", "en": "Urban Planning Standards"},
                url="/documents/urban-planning",
                icon="city",
                order=2,
                parent_id=documents_id,
                permissions=["read"]
            ),
            MenuItem(
                title={"uz": "Standartlar", "ru": "Стандарты", "en": "Standards"},
                url="/documents/standards",
                icon="check-circle",
                order=3,
                parent_id=documents_id,
                permissions=["read"]
            )
        ]
        
        for item in submenus:
            db.add(item)
    
    db.commit()
    db.close()