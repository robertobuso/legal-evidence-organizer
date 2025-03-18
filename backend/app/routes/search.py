from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.database import get_db
from app.models import Email, ChatLog, PDFDocument
from app.utils.logger import app_logger

router = APIRouter()

class SearchResult(BaseModel):
    id: int
    type: str
    date: Optional[str] = None
    title: str
    snippet: str
    source: str

@router.get("/search", summary="Search across all data sources", response_model=List[SearchResult])
async def search_data(
    query: str = Query(..., description="Search query term"),
    source_type: Optional[str] = Query(None, description="Filter by source type (email, chat, pdf)"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    person: Optional[str] = Query(None, description="Filter by person name"),
    skip: int = Query(0, description="Number of items to skip"),
    limit: int = Query(50, description="Maximum number of items to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Search across emails, chat logs, and PDFs for the specified query term.
    
    Results can be filtered by source type, date range, and person name.
    """
    try:
        search_results = []
        
        # Parse dates if provided
        start_date_obj = None
        end_date_obj = None
        
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
                
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
        
        # Search emails
        if not source_type or source_type.lower() == "email":
            email_query = select(Email)
            
            # Apply search filters
            email_filters = []
            
            # Text search
            if query:
                email_filters.append(
                    or_(
                        Email.subject.ilike(f"%{query}%"),
                        Email.body.ilike(f"%{query}%")
                    )
                )
            
            # Date filter
            if start_date_obj:
                email_filters.append(Email.date >= start_date_obj)
            if end_date_obj:
                email_filters.append(Email.date <= end_date_obj)
            
            # Person filter
            if person:
                email_filters.append(
                    or_(
                        Email.sender.ilike(f"%{person}%"),
                        Email.recipients.ilike(f"%{person}%")
                    )
                )
            
            # Apply all filters
            if email_filters:
                email_query = email_query.filter(and_(*email_filters))
            
            # Execute query
            email_result = await db.execute(email_query)
            emails = email_result.scalars().all()
            
            # Format results
            for email in emails:
                search_results.append(
                    SearchResult(
                        id=email.id,
                        type="email",
                        date=email.date.isoformat() if email.date else None,
                        title=email.subject or "(No Subject)",
                        snippet=email.body[:200] + "..." if len(email.body) > 200 else email.body,
                        source=f"From: {email.sender}"
                    )
                )
        
        # Search chat logs
        if not source_type or source_type.lower() == "chat":
            chat_query = select(ChatLog)
            
            # Apply search filters
            chat_filters = []
            
            # Text search
            if query:
                chat_filters.append(ChatLog.message.ilike(f"%{query}%"))
            
            # Date filter
            if start_date_obj:
                chat_filters.append(ChatLog.date_time >= start_date_obj)
            if end_date_obj:
                chat_filters.append(ChatLog.date_time <= end_date_obj)
            
            # Person filter
            if person:
                chat_filters.append(ChatLog.sender.ilike(f"%{person}%"))
            
            # Apply all filters
            if chat_filters:
                chat_query = chat_query.filter(and_(*chat_filters))
            
            # Execute query
            chat_result = await db.execute(chat_query)
            chats = chat_result.scalars().all()
            
            # Format results
            for chat in chats:
                search_results.append(
                    SearchResult(
                        id=chat.id,
                        type="chat",
                        date=chat.date_time.isoformat() if chat.date_time else None,
                        title=f"Chat message from {chat.sender}",
                        snippet=chat.message[:200] + "..." if len(chat.message) > 200 else chat.message,
                        source=f"WhatsApp: {os.path.basename(chat.file_path) if chat.file_path else 'Unknown'}"
                    )
                )
        
        # Search PDFs
        if not source_type or source_type.lower() == "pdf":
            pdf_query = select(PDFDocument)
            
            # Apply search filters
            pdf_filters = []
            
            # Text search
            if query:
                pdf_filters.append(
                    or_(
                        PDFDocument.file_name.ilike(f"%{query}%"),
                        PDFDocument.extracted_text.ilike(f"%{query}%")
                    )
                )
            
            # Person filter (search in text)
            if person:
                pdf_filters.append(PDFDocument.extracted_text.ilike(f"%{person}%"))
            
            # Apply all filters
            if pdf_filters:
                pdf_query = pdf_query.filter(and_(*pdf_filters))
            
            # Execute query
            pdf_result = await db.execute(pdf_query)
            pdfs = pdf_result.scalars().all()
            
            # Format results
            for pdf in pdfs:
                search_results.append(
                    SearchResult(
                        id=pdf.id,
                        type="pdf",
                        date=None,  # PDFs don't have a date field
                        title=pdf.file_name or "Unnamed PDF",
                        snippet=pdf.extracted_text[:200] + "..." if len(pdf.extracted_text) > 200 else pdf.extracted_text,
                        source=f"PDF: {pdf.file_name}"
                    )
                )
        
        # Sort by date if available, otherwise by ID
        search_results.sort(
            key=lambda x: (
                datetime.fromisoformat(x.date) if x.date else datetime.min, 
                x.id
            ),
            reverse=True  # Most recent first
        )
        
        # Apply pagination
        paginated_results = search_results[skip:skip+limit]
        
        return paginated_results
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error searching data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))