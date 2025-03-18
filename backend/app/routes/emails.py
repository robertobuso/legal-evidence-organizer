from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from pydantic import BaseModel, Field

from app.database import get_db
from app.models import Email
from app.services.email_service import EmailService
from app.config import EMAIL_START_DATE, EMAIL_END_DATE
from app.utils.logger import app_logger

router = APIRouter()
email_service = EmailService()

class EmailAddress(BaseModel):
    address: str = Field(..., description="Email address to fetch")

class EmailFetchRequest(BaseModel):
    addresses: List[EmailAddress] = Field(..., description="List of email addresses to fetch data from/to")
    start_date: Optional[str] = Field(EMAIL_START_DATE, description="Start date for email range (YYYY-MM-DD)")
    end_date: Optional[str] = Field(EMAIL_END_DATE, description="End date for email range (YYYY-MM-DD)")

class EmailResponse(BaseModel):
    id: int
    sender: str
    recipients: str
    subject: str
    date: str
    snippet: str

@router.post("/emails/fetch", summary="Fetch emails from Gmail")
async def fetch_emails(
    background_tasks: BackgroundTasks,
    request: EmailFetchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch emails from Gmail API for the specified addresses and date range.
    
    Emails will be fetched asynchronously in the background and saved to the database.
    """
    try:
        # Extract email addresses
        email_addresses = [item.address for item in request.addresses]
        
        if not email_addresses:
            raise HTTPException(status_code=400, detail="At least one email address is required")
        
        # Start background task to fetch emails
        async def fetch_and_save_emails():
            try:
                # Authenticate and fetch emails
                emails = await email_service.fetch_emails(
                    email_addresses=email_addresses,
                    start_date=request.start_date,
                    end_date=request.end_date
                )
                
                if emails:
                    # Save emails to database
                    saved_emails = await email_service.save_emails(db, emails)
                    app_logger.info(f"Successfully fetched and saved {len(saved_emails)} emails")
                else:
                    app_logger.warning("No emails fetched from Gmail API")
            except Exception as e:
                app_logger.error(f"Error in background email fetch: {str(e)}")
        
        background_tasks.add_task(fetch_and_save_emails)
        
        return {
            "status": "processing",
            "message": f"Fetching emails for {len(email_addresses)} address(es) in the background",
            "addresses": email_addresses,
            "date_range": f"{request.start_date} to {request.end_date}"
        }
        
    except Exception as e:
        app_logger.error(f"Error initiating email fetch: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/emails", summary="Get emails from database", response_model=List[EmailResponse])
async def get_emails(
    skip: int = 0,
    limit: int = 100,
    sender: Optional[str] = None,
    recipient: Optional[str] = None,
    subject: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get emails from the database with optional filtering.
    """
    try:
        query = select(Email)
        
        # Apply filters
        if sender:
            query = query.filter(Email.sender.ilike(f"%{sender}%"))
        if recipient:
            query = query.filter(Email.recipients.ilike(f"%{recipient}%"))
        if subject:
            query = query.filter(Email.subject.ilike(f"%{subject}%"))
        if start_date:
            query = query.filter(Email.date >= start_date)
        if end_date:
            query = query.filter(Email.date <= end_date)
        
        # Apply pagination
        query = query.order_by(Email.date.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        emails = result.scalars().all()
        
        # Format response
        return [
            EmailResponse(
                id=email.id,
                sender=email.sender,
                recipients=email.recipients,
                subject=email.subject,
                date=email.date.isoformat() if email.date else None,
                snippet=email.body[:200] + "..." if len(email.body) > 200 else email.body
            )
            for email in emails
        ]
        
    except Exception as e:
        app_logger.error(f"Error retrieving emails: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/emails/{email_id}", summary="Get email by ID")
async def get_email_by_id(email_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get a specific email by its ID.
    """
    try:
        query = select(Email).where(Email.id == email_id)
        result = await db.execute(query)
        email = result.scalars().first()
        
        if not email:
            raise HTTPException(status_code=404, detail=f"Email with ID {email_id} not found")
        
        return {
            "id": email.id,
            "sender": email.sender,
            "recipients": email.recipients,
            "subject": email.subject,
            "date": email.date.isoformat() if email.date else None,
            "body": email.body,
            "email_id": email.email_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error retrieving email {email_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/emails/status", summary="Get email fetch status")
async def get_email_status(db: AsyncSession = Depends(get_db)):
    """
    Get status of email fetching process.
    """
    try:
        # Count total emails in database
        query = select(Email)
        result = await db.execute(query)
        emails = result.scalars().all()
        
        return {
            "status": "completed",
            "total_emails": len(emails),
            "message": f"Found {len(emails)} emails in the database"
        }
        
    except Exception as e:
        app_logger.error(f"Error checking email status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))