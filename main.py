from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr
import os
from dotenv import load_dotenv

load_dotenv()

# FastAPI app
app = FastAPI(
    title="TMSITI Backend API",
    description="API для сайта Научно-исследовательского института технического нормирования и стандартизации",
    version="1.0.0"
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "https://tmsiti.uz")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted hosts
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["tmsiti.uz", "*.tmsiti.uz", "localhost", "127.0.0.1"]
)

# Database configuration
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tmsiti.db")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security
security = HTTPBearer()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="viewer")
    permissions = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
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

# Pydantic models
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str = "viewer"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    permissions: List[str]
    
    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

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
        orm_mode = True

# Update forward reference
MenuItemResponse.update_forward_refs()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user(db, username=username)
    if user is None:
        raise credentials_exception
    return user

def check_permission(user: User, required_permission: str):
    if not user.permissions:
        return False
    return required_permission in user.permissions

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize default data
def init_db():
    db = SessionLocal()
    
    # Create default users if they don't exist
    if not db.query(User).filter(User.username == "admin").first():
        admin_user = User(
            username="admin",
            email="admin@tmsiti.uz",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            permissions=["read", "write", "delete", "manage_users"]
        )
        db.add(admin_user)
    
    if not db.query(User).filter(User.username == "editor").first():
        editor_user = User(
            username="editor",
            email="editor@tmsiti.uz",
            hashed_password=get_password_hash("editor123"),
            role="editor",
            permissions=["read", "write"]
        )
        db.add(editor_user)
    
    # Create default menu items
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
        
        # Add submenu items
        institut_id = db.query(MenuItem).filter(MenuItem.url == "/institut").first().id
        documents_id = db.query(MenuItem).filter(MenuItem.url == "/documents").first().id
        
        submenus = [
            # Institut submenus
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
            # Documents submenus
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

# Initialize database on startup
init_db()

# API Routes

# Authentication routes
@app.post("/api/auth/login", response_model=Token)
@limiter.limit("5/minute")
async def login(request: Request, user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.post("/api/auth/register", response_model=UserResponse)
@limiter.limit("3/minute")
async def register(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = get_user(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        permissions=["read"]  # Default permissions
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# Menu routes
@app.get("/api/menu", response_model=List[MenuItemResponse])
@limiter.limit("60/minute")
async def get_menu(request: Request, lang: str = "uz", db: Session = Depends(get_db)):
    menu_items = db.query(MenuItem).filter(
        MenuItem.parent_id == None,
        MenuItem.is_active == True
    ).order_by(MenuItem.order).all()
    
    return menu_items

@app.get("/api/menu/{menu_id}", response_model=MenuItemResponse)
@limiter.limit("60/minute")
async def get_menu_item(request: Request, menu_id: int, db: Session = Depends(get_db)):
    menu_item = db.query(MenuItem).filter(MenuItem.id == menu_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return menu_item

@app.post("/api/menu", response_model=MenuItemResponse)
@limiter.limit("10/minute")
async def create_menu_item(
    request: Request,
    menu_item: MenuItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not check_permission(current_user, "write"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db_menu_item = MenuItem(**menu_item.dict())
    db.add(db_menu_item)
    db.commit()
    db.refresh(db_menu_item)
    
    return db_menu_item

@app.put("/api/menu/{menu_id}", response_model=MenuItemResponse)
@limiter.limit("10/minute")
async def update_menu_item(
    request: Request,
    menu_id: int,
    menu_item: MenuItemCreate,
    current_user: User = Depends(get_current_user),
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

@app.delete("/api/menu/{menu_id}")
@limiter.limit("10/minute")
async def delete_menu_item(
    request: Request,
    menu_id: int,
    current_user: User = Depends(get_current_user),
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

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)