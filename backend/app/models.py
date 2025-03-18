from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

class Email(Base):
    """Model for storing extracted email data."""
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String, index=True)
    recipients = Column(String)
    subject = Column(String, index=True)
    date = Column(DateTime, index=True)
    body = Column(Text)
    email_id = Column(String, unique=True)  # Gmail message ID
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ChatLog(Base):
    """Model for storing extracted WhatsApp chat log data."""
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    date_time = Column(DateTime, index=True)
    sender = Column(String, index=True)
    message = Column(Text)
    file_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PDFDocument(Base):
    """Model for storing extracted PDF invoice data."""
    __tablename__ = "pdfs"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, index=True)
    extracted_text = Column(Text)
    file_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Timeline(Base):
    """Model for storing generated timelines."""
    __tablename__ = "timelines"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    events = relationship("TimelineEvent", back_populates="timeline", cascade="all, delete-orphan")

class TimelineEvent(Base):
    """Model for storing timeline events."""
    __tablename__ = "timeline_events"

    id = Column(Integer, primary_key=True, index=True)
    timeline_id = Column(Integer, ForeignKey("timelines.id"))
    date = Column(DateTime, index=True)
    title = Column(String)
    description = Column(Text, nullable=True)
    source_type = Column(String)  # "email", "chat", "pdf"
    source_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    timeline = relationship("Timeline", back_populates="events")

class Evidence(Base):
    """Model for storing evidence recommendations."""
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    relevance = Column(Text)
    source_type = Column(String)  # "email", "chat", "pdf"
    source_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class Report(Base):
    """Model for storing generated reports."""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(Text)
    timeline_id = Column(Integer, ForeignKey("timelines.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)