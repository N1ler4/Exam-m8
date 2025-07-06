from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from ..core.deps import get_db, get_current_user
from ..models.document import Document
from ..schemas.document import DocumentCreate, DocumentResponse
from ..core.security import check_permission

router = APIRouter()

@router.get("", response_model=List[DocumentResponse])
async def get_documents(category: str = None, lang: str = "uz", db: Session = Depends(get_db)):
    query = db.query(Document).filter(Document.is_active == True)
    if category:
        query = query.filter(Document.category == category)
    documents = query.order_by(Document.created_at).all()
    return documents

@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.post("", response_model=DocumentResponse)
async def create_document(
    document: DocumentCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not check_permission(current_user, "write"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db_document = Document(**document.dict())
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

@router.put("/{doc_id}", response_model=DocumentResponse)
async def update_document(
    doc_id: int,
    document: DocumentCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not check_permission(current_user, "write"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db_document = db.query(Document).filter(Document.id == doc_id).first()
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    for key, value in document.dict().items():
        setattr(db_document, key, value)
    db.commit()
    db.refresh(db_document)
    return db_document

@router.delete("/{doc_id}")
async def delete_document(
    doc_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not check_permission(current_user, "delete"):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db_document = db.query(Document).filter(Document.id == doc_id).first()
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(db_document)
    db.commit()
    return {"message": "Document deleted successfully"}