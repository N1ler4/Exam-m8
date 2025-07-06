from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class DocumentBase(BaseModel):
    title: Dict[str, str] = Field(..., description="Title in multiple languages")
    description: Dict[str, str] = Field(..., description="Description in multiple languages")
    document_type: str = Field(..., description="Type of document (law, standard, regulation, shnq, reference)")
    category: Optional[str] = Field(None, description="Category within document type")
    document_number: Optional[str] = Field(None, description="Official document number")
    author: Optional[str] = Field(None, description="Document author/issuer")
    issue_date: Optional[datetime] = Field(None, description="When document was issued")
    effective_date: Optional[datetime] = Field(None, description="When document becomes effective")
    tags: Optional[List[str]] = Field([], description="List of tags for search")
    document_metadata : Optional[Dict[str, Any]] = Field({}, description="ional metadata")
    is_featured: bool = Field(False, description="Whether document is featured")


class DocumentCreate(DocumentBase):
    content: Optional[str] = Field(None, description="Full document content")


class DocumentUpdate(BaseModel):
    title: Optional[Dict[str, str]] = None
    description: Optional[Dict[str, str]] = None
    content: Optional[str] = None
    document_type: Optional[str] = None
    category: Optional[str] = None
    document_number: Optional[str] = None
    author: Optional[str] = None
    issue_date: Optional[datetime] = None
    effective_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    document_metadata : Optional[Dict[str, Any]] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None


class DocumentResponse(DocumentBase):
    id: int
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    download_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    
    class Config:
        orm_mode = True


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int
    page: int
    per_page: int
    pages: int


class DocumentCategoryBase(BaseModel):
    name: Dict[str, str] = Field(..., description="Category name in multiple languages")
    description: Dict[str, str] = Field(..., description="Category description in multiple languages")
    document_type: str = Field(..., description="Type of document this category belongs to")
    parent_id: Optional[int] = Field(None, description="Parent category ID")
    order: int = Field(0, description="Display order")


class DocumentCategoryCreate(DocumentCategoryBase):
    pass


class DocumentCategoryResponse(DocumentCategoryBase):
    id: int
    is_active: bool
    created_at: datetime
    children: List['DocumentCategoryResponse'] = []
    
    class Config:
        orm_mode = True


# Update forward reference
DocumentCategoryResponse.update_forward_refs()


class DocumentSearchRequest(BaseModel):
    query: Optional[str] = Field(None, description="Search query")
    document_type: Optional[str] = Field(None, description="Filter by document type")
    category: Optional[str] = Field(None, description="Filter by category")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    date_from: Optional[datetime] = Field(None, description="Filter by date from")
    date_to: Optional[datetime] = Field(None, description="Filter by date to")
    is_featured: Optional[bool] = Field(None, description="Filter by featured status")
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")


class DownloadLogResponse(BaseModel):
    id: int
    document_id: int
    user_id: Optional[int] = None
    ip_address: str
    downloaded_at: datetime
    
    class Config:
        orm_mode = True