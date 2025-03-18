from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.database import get_db
from app.models import Evidence, Email, ChatLog, PDFDocument
from app.services.openai_service import OpenAIService
from app.utils.logger import app_logger

router = APIRouter()
openai_service = OpenAIService()

class EvidenceResponse(BaseModel):
    id: int
    title: str
    description: str
    relevance: str
    source_type: str
    source_id: int
    created_at: str

@router.post("/evidence/analyze", summary="Analyze and recommend evidence")
async def analyze_evidence(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze all available data and recommend evidence using OpenAI GPT-4.
    
    This will process emails, chat logs, and PDFs to identify potential evidence for a contract dispute.
    The analysis will run asynchronously in the background.
    """
    try:
        # Start background task to analyze evidence
        async def analyze_evidence_task():
            try:
                # Fetch data from database
                
                # Get emails
                email_query = select(Email)
                email_result = await db.execute(email_query)
                emails = email_result.scalars().all()
                
                # Get chat logs
                chat_query = select(ChatLog)
                chat_result = await db.execute(chat_query)
                chats = chat_result.scalars().all()
                
                # Get PDFs
                pdf_query = select(PDFDocument)
                pdf_result = await db.execute(pdf_query)
                pdfs = pdf_result.scalars().all()
                
                # Prepare data for analysis
                data = {
                    "emails": emails,
                    "chat_logs": chats,
                    "pdfs": pdfs
                }
                
                # Analyze evidence using OpenAI
                analysis = await openai_service.analyze_evidence(data)
                
                # Save recommended evidence to database
                if "recommended_evidence" in analysis:
                    async with AsyncSession(bind=db.get_bind()) as session:
                        for evidence_data in analysis["recommended_evidence"]:
                            try:
                                # Create evidence record
                                new_evidence = Evidence(
                                    title=evidence_data.get("title", "Untitled Evidence"),
                                    description=evidence_data.get("description", ""),
                                    relevance=evidence_data.get("relevance", ""),
                                    source_type=evidence_data.get("source_type", "unknown"),
                                    source_id=evidence_data.get("source_id", 0)
                                )
                                session.add(new_evidence)
                            except Exception as e:
                                app_logger.error(f"Error creating evidence record: {str(e)}")
                        
                        await session.commit()
                        app_logger.info(f"Evidence analysis completed with {len(analysis.get('recommended_evidence', []))} recommendations")
                
            except Exception as e:
                app_logger.error(f"Error analyzing evidence: {str(e)}")
        
        background_tasks.add_task(analyze_evidence_task)
        
        return {
            "status": "processing",
            "message": "Evidence analysis started. This may take several minutes."
        }
        
    except Exception as e:
        app_logger.error(f"Error initiating evidence analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/evidence", summary="Get all evidence recommendations", response_model=List[EvidenceResponse])
async def get_evidence(db: AsyncSession = Depends(get_db)):
    """
    Get all evidence recommendations from the database.
    """
    try:
        query = select(Evidence).order_by(Evidence.created_at.desc())
        result = await db.execute(query)
        evidence_list = result.scalars().all()
        
        return [
            EvidenceResponse(
                id=evidence.id,
                title=evidence.title,
                description=evidence.description,
                relevance=evidence.relevance,
                source_type=evidence.source_type,
                source_id=evidence.source_id,
                created_at=evidence.created_at.isoformat()
            )
            for evidence in evidence_list
        ]
        
    except Exception as e:
        app_logger.error(f"Error retrieving evidence: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/evidence/{evidence_id}", summary="Get evidence by ID", response_model=EvidenceResponse)
async def get_evidence_by_id(evidence_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get a specific evidence recommendation by its ID.
    """
    try:
        query = select(Evidence).where(Evidence.id == evidence_id)
        result = await db.execute(query)
        evidence = result.scalars().first()
        
        if not evidence:
            raise HTTPException(status_code=404, detail=f"Evidence with ID {evidence_id} not found")
        
        return EvidenceResponse(
            id=evidence.id,
            title=evidence.title,
            description=evidence.description,
            relevance=evidence.relevance,
            source_type=evidence.source_type,
            source_id=evidence.source_id,
            created_at=evidence.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error retrieving evidence {evidence_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/evidence/source/{source_type}/{source_id}", summary="Get source details for evidence")
async def get_evidence_source(source_type: str, source_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get the source details for a piece of evidence.
    
    This retrieves the original content from the specified source (email, chat, pdf).
    """
    try:
        if source_type == "email":
            query = select(Email).where(Email.id == source_id)
            result = await db.execute(query)
            source = result.scalars().first()
            
            if not source:
                raise HTTPException(status_code=404, detail=f"Email with ID {source_id} not found")
            
            return {
                "source_type": "email",
                "source_id": source_id,
                "data": {
                    "sender": source.sender,
                    "recipients": source.recipients,
                    "subject": source.subject,
                    "date": source.date.isoformat() if source.date else None,
                    "body": source.body
                }
            }
            
        elif source_type == "chat":
            query = select(ChatLog).where(ChatLog.id == source_id)
            result = await db.execute(query)
            source = result.scalars().first()
            
            if not source:
                raise HTTPException(status_code=404, detail=f"Chat message with ID {source_id} not found")
            
            return {
                "source_type": "chat",
                "source_id": source_id,
                "data": {
                    "sender": source.sender,
                    "date_time": source.date_time.isoformat() if source.date_time else None,
                    "message": source.message,
                    "file_path": source.file_path
                }
            }
            
        elif source_type == "pdf":
            query = select(PDFDocument).where(PDFDocument.id == source_id)
            result = await db.execute(query)
            source = result.scalars().first()
            
            if not source:
                raise HTTPException(status_code=404, detail=f"PDF with ID {source_id} not found")
            
            return {
                "source_type": "pdf",
                "source_id": source_id,
                "data": {
                    "file_name": source.file_name,
                    "extracted_text": source.extracted_text,
                    "file_path": source.file_path
                }
            }
            
        else:
            raise HTTPException(status_code=400, detail=f"Invalid source type: {source_type}")
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error retrieving source {source_type}/{source_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/evidence/{evidence_id}", summary="Delete evidence")
async def delete_evidence(evidence_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a specific evidence recommendation.
    """
    try:
        # Check if evidence exists
        evidence = await db.get(Evidence, evidence_id)
        if not evidence:
            raise HTTPException(status_code=404, detail=f"Evidence with ID {evidence_id} not found")
        
        # Delete evidence
        await db.delete(evidence)
        await db.commit()
        
        return {"message": f"Evidence with ID {evidence_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error deleting evidence {evidence_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))