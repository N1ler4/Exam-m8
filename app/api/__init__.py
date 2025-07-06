from .auth import router as auth_router
from .menu import router as menu_router
from .documents import router as documents_router

__all__ = ["auth_router", "menu_router", "documents_router"]