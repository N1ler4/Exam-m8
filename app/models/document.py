from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(JSON)  # {"uz": "title", "ru": "title", "en": "title"}
    description = Column(JSON)  # {"uz": "description", "ru": "description", "en": "description"}
    content = Column(Text)  # Full document content
    document_type = Column(String)  # "law", "standard", "regulation", "shnq", "reference"
    category = Column(String)  # Category within document type
    document_number = Column(String)  # Official document number (like "O'zMSt 103:2024")
    file_path = Column(String)  # Path to uploaded file
    file_size = Column(Integer)  # File size in bytes
    file_type = Column(String)  # MIME type of file
    download_count = Column(Integer, default=0)
    author = Column(String)  # Document author/issuer
    issue_date = Column(DateTime)  # When document was issued
    effective_date = Column(DateTime)  # When document becomes effective
    tags = Column(JSON)  # List of tags for search
    document_metadata = Column(JSON)
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    creator = relationship("User", back_populates="created_documents")


class DocumentCategory(Base):
    __tablename__ = "document_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(JSON)  # {"uz": "name", "ru": "name", "en": "name"}
    description = Column(JSON)  # {"uz": "description", "ru": "description", "en": "description"}
    document_type = Column(String)  # "law", "standard", "regulation", "shnq", "reference"
    parent_id = Column(Integer, ForeignKey("document_categories.id"), nullable=True)
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Self-referential relationship
    children = relationship("DocumentCategory", backref="parent", remote_side=[id])


class DownloadLog(Base):
    __tablename__ = "download_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    ip_address = Column(String)
    user_agent = Column(String)
    downloaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document")
    user = relationship("User")