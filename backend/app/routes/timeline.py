import os
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.database import get_db
from app.models import Timeline, TimelineEvent, Email, ChatLog, PDFDocument
from app.services.gemini_service import GeminiService
from app.services.langchain_service import LangChainService
from app.utils.logger import app_logger

router = APIRouter()
gemini_service = GeminiService()
langchain_service = LangChainService()

class TimelineEventResponse(BaseModel):
    id: int
    date: str
    title: str
    description: Optional[str] = None
    source_type: str
    source_id: int

class TimelineResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    created_at: str
    events: List[TimelineEventResponse]

@router.post("/timeline/generate", summary="Generate timeline from evidence")
async def generate_timeline(
    background_tasks: BackgroundTasks,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    title: str = "Timeline of Contract Dispute",
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a timeline from emails, chat logs, and PDFs using Google Gemini API.
    
    The timeline will be generated asynchronously in the background and saved to the database.
    """
    try:
        # Create timeline record
        new_timeline = Timeline(
            title=title,
            description="Generating timeline... This may take a few minutes."
        )
        db.add(new_timeline)
        await db.commit()
        await db.refresh(new_timeline)
        
        timeline_id = new_timeline.id
        app_logger.info(f"Created timeline with ID {timeline_id}")
        
        # Start background task to generate timeline
        async def generate_timeline_task():
            try:
                # Parse dates if provided
                start_date_obj = None
                end_date_obj = None
                
                if start_date:
                    try:
                        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                    except ValueError:
                        app_logger.error(f"Invalid start_date format: {start_date}")
                        
                if end_date:
                    try:
                        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                    except ValueError:
                        app_logger.error(f"Invalid end_date format: {end_date}")
                
                # Fetch data from database
                
                # Get emails
                email_query = select(Email)
                if start_date_obj:
                    email_query = email_query.filter(Email.date >= start_date_obj)
                if end_date_obj:
                    email_query = email_query.filter(Email.date <= end_date_obj)
                email_result = await db.execute(email_query)
                emails = email_result.scalars().all()
                
                # Get chat logs
                chat_query = select(ChatLog)
                if start_date_obj:
                    chat_query = chat_query.filter(ChatLog.date_time >= start_date_obj)
                if end_date_obj:
                    chat_query = chat_query.filter(ChatLog.date_time <= end_date_obj)
                chat_result = await db.execute(chat_query)
                chats = chat_result.scalars().all()
                
                # Get PDFs (PDFs don't have dates)
                pdf_query = select(PDFDocument)
                pdf_result = await db.execute(pdf_query)
                pdfs = pdf_result.scalars().all()
                
                # Format data for Gemini
                events = []
                
                # Format emails
                for email in emails:
                    events.append({
                        "date": email.date.isoformat() if email.date else None,
                        "source_type": "email",
                        "source_id": email.id,
                        "sender": email.sender,
                        "recipients": email.recipients,
                        "subject": email.subject,
                        "content": email.body[:500] + "..." if len(email.body) > 500 else email.body
                    })
                
                # Format chat messages
                for chat in chats:
                    events.append({
                        "date": chat.date_time.isoformat() if chat.date_time else None,
                        "source_type": "chat",
                        "source_id": chat.id,
                        "sender": chat.sender,
                        "content": chat.message
                    })
                
                # Format PDFs (assume they're relevant but don't have specific dates)
                for pdf in pdfs:
                    events.append({
                        "date": None,  # No date for PDFs
                        "source_type": "pdf",
                        "source_id": pdf.id,
                        "file_name": pdf.file_name,
                        "content": pdf.extracted_text[:500] + "..." if len(pdf.extracted_text) > 500 else pdf.extracted_text
                    })
                
                # Sort events by date
                dated_events = [e for e in events if e.get("date")]
                undated_events = [e for e in events if not e.get("date")]
                
                dated_events.sort(key=lambda x: x["date"])
                events = dated_events + undated_events
                
                # Generate timeline using Gemini
                timeline_data = await gemini_service.generate_timeline(events)
                
                # Update timeline with overview
                async with AsyncSession(bind=db.get_bind()) as session:
                    timeline = await session.get(Timeline, timeline_id)
                    if timeline:
                        timeline.description = timeline_data.get("overview", "Timeline generated successfully.")
                        await session.commit()
                
                # Save timeline events
                async with AsyncSession(bind=db.get_bind()) as session:
                    timeline = await session.get(Timeline, timeline_id)
                    if timeline and "events" in timeline_data:
                        for event_data in timeline_data["events"]:
                            try:
                                # Parse date
                                date_obj = None
                                if "date" in event_data and event_data["date"]:
                                    try:
                                        date_obj = datetime.fromisoformat(event_data["date"])
                                    except (ValueError, TypeError):
                                        try:
                                            date_obj = datetime.strptime(event_data["date"], "%Y-%m-%d")
                                        except (ValueError, TypeError):
                                            app_logger.warning(f"Could not parse date: {event_data.get('date')}")
                                
                                # Create event
                                new_event = TimelineEvent(
                                    timeline_id=timeline_id,
                                    date=date_obj,
                                    title=event_data.get("title", "Untitled Event"),
                                    description=event_data.get("description", ""),
                                    source_type=event_data.get("source", "unknown").split(":")[0] if ":" in event_data.get("source", "") else "unknown",
                                    source_id=int(event_data.get("source", "").split(":")[-1]) if ":" in event_data.get("source", "") and event_data.get("source", "").split(":")[-1].isdigit() else 0
                                )
                                session.add(new_event)
                            except Exception as e:
                                app_logger.error(f"Error creating timeline event: {str(e)}")
                        
                        await session.commit()
                        app_logger.info(f"Timeline generation completed for timeline ID {timeline_id}")
                
            except Exception as e:
                app_logger.error(f"Error generating timeline: {str(e)}")
                # Update timeline with error message
                async with AsyncSession(bind=db.get_bind()) as session:
                    timeline = await session.get(Timeline, timeline_id)
                    if timeline:
                        timeline.description = f"Error generating timeline: {str(e)}"
                        await session.commit()
        
        background_tasks.add_task(generate_timeline_task)
        
        return {
            "id": timeline_id,
            "status": "processing",
            "message": "Timeline generation started. This may take a few minutes."
        }
        
    except Exception as e:
        app_logger.error(f"Error initiating timeline generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/timeline/{timeline_id}", summary="Get timeline by ID", response_model=TimelineResponse)
async def get_timeline(timeline_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get a specific timeline by its ID.
    """
    try:
        # Get timeline
        timeline_query = select(Timeline).where(Timeline.id == timeline_id)
        timeline_result = await db.execute(timeline_query)
        timeline = timeline_result.scalars().first()
        
        if not timeline:
            raise HTTPException(status_code=404, detail=f"Timeline with ID {timeline_id} not found")
        
        # Get timeline events
        events_query = select(TimelineEvent).where(TimelineEvent.timeline_id == timeline_id).order_by(TimelineEvent.date)
        events_result = await db.execute(events_query)
        events = events_result.scalars().all()
        
        # Format response
        return TimelineResponse(
            id=timeline.id,
            title=timeline.title,
            description=timeline.description,
            created_at=timeline.created_at.isoformat(),
            events=[
                TimelineEventResponse(
                    id=event.id,
                    date=event.date.isoformat() if event.date else None,
                    title=event.title,
                    description=event.description,
                    source_type=event.source_type,
                    source_id=event.source_id
                )
                for event in events
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error retrieving timeline {timeline_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/timelines", summary="Get all timelines")
async def get_timelines(db: AsyncSession = Depends(get_db)):
    """
    Get all timelines.
    """
    try:
        query = select(Timeline).order_by(Timeline.created_at.desc())
        result = await db.execute(query)
        timelines = result.scalars().all()
        
        return [
            {
                "id": timeline.id,
                "title": timeline.title,
                "description": timeline.description,
                "created_at": timeline.created_at.isoformat()
            }
            for timeline in timelines
        ]
        
    except Exception as e:
        app_logger.error(f"Error retrieving timelines: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/timeline/{timeline_id}", summary="Delete timeline")
async def delete_timeline(timeline_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a specific timeline and its events.
    """
    try:
        # Check if timeline exists
        timeline = await db.get(Timeline, timeline_id)
        if not timeline:
            raise HTTPException(status_code=404, detail=f"Timeline with ID {timeline_id} not found")
        
        # Delete timeline (cascade should delete events too)
        await db.delete(timeline)
        await db.commit()
        
        return {"message": f"Timeline with ID {timeline_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error deleting timeline {timeline_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))