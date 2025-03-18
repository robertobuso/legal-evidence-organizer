import os
import shutil
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.services.chat_service import ChatService
from app.services.pdf_service import PDFService
from app.config import CHAT_UPLOAD_DIR, PDF_UPLOAD_DIR
from app.utils.logger import app_logger

router = APIRouter()
chat_service = ChatService()
pdf_service = PDFService()

@router.post("/upload/chat", summary="Upload WhatsApp chat log")
async def upload_chat_log(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a WhatsApp chat log file (.txt) and process it.
    
    The file will be stored and its contents will be parsed and saved to the database.
    """
    try:
        # Validate file extension
        if not file.filename.endswith('.txt'):
            raise HTTPException(status_code=400, detail="Only .txt files are accepted for chat logs")
        
        # Create unique filename
        filename = f"{os.path.splitext(file.filename)[0]}_{os.urandom(4).hex()}.txt"
        file_path = os.path.join(CHAT_UPLOAD_DIR, filename)
        
        # Save uploaded file
        with open(file_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        app_logger.info(f"Uploaded chat log: {filename}")
        
        # Process file in background
        async def process_chat_file():
            try:
                chat_messages = await chat_service.process_chat_file(file_path)
                await chat_service.save_chat_messages(db, chat_messages)
                app_logger.info(f"Successfully processed chat log: {filename}")
            except Exception as e:
                app_logger.error(f"Error processing chat log {filename}: {str(e)}")
        
        background_tasks.add_task(process_chat_file)
        
        return {
            "filename": filename,
            "status": "processing",
            "message": "Chat log uploaded successfully and is being processed"
        }
        
    except Exception as e:
        app_logger.error(f"Error uploading chat log: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload/pdf", summary="Upload PDF invoice")
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a PDF invoice file (.pdf) and process it.
    
    The file will be stored and its contents will be extracted and saved to the database.
    """
    try:
        # Validate file extension
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only .pdf files are accepted for invoices")
        
        # Create unique filename
        filename = f"{os.path.splitext(file.filename)[0]}_{os.urandom(4).hex()}.pdf"
        file_path = os.path.join(PDF_UPLOAD_DIR, filename)
        
        # Save uploaded file
        with open(file_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        app_logger.info(f"Uploaded PDF invoice: {filename}")
        
        # Process file in background
        async def process_pdf_file():
            try:
                pdf_data = await pdf_service.process_pdf_file(file_path)
                if pdf_data:
                    await pdf_service.save_pdf_document(db, pdf_data)
                    app_logger.info(f"Successfully processed PDF: {filename}")
                else:
                    app_logger.error(f"Failed to process PDF: {filename}")
            except Exception as e:
                app_logger.error(f"Error processing PDF {filename}: {str(e)}")
        
        background_tasks.add_task(process_pdf_file)
        
        return {
            "filename": filename,
            "status": "processing",
            "message": "PDF uploaded successfully and is being processed"
        }
        
    except Exception as e:
        app_logger.error(f"Error uploading PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/upload/status/{filename}", summary="Check upload processing status")
async def check_upload_status(filename: str, db: AsyncSession = Depends(get_db)):
    """
    Check the processing status of an uploaded file.
    
    This endpoint returns information about whether the file has been fully processed.
    """
    try:
        # Check if it's a chat log
        if filename.endswith('.txt'):
            # Query database to see if entries exist for this file
            result = await chat_service.get_chat_messages(
                db, 
                filters={"file_path": os.path.join(CHAT_UPLOAD_DIR, filename)}
            )
            
            if result:
                return {
                    "filename": filename,
                    "status": "completed",
                    "message": f"Chat log processed with {len(result)} messages extracted",
                    "count": len(result)
                }
            else:
                return {
                    "filename": filename,
                    "status": "processing",
                    "message": "File is still being processed or no data was extracted"
                }
                
        # Check if it's a PDF
        elif filename.endswith('.pdf'):
            # Query database to see if entries exist for this file
            result = await pdf_service.get_pdf_documents(
                db, 
                filters={"file_path": os.path.join(PDF_UPLOAD_DIR, filename)}
            )
            
            if result:
                return {
                    "filename": filename,
                    "status": "completed",
                    "message": "PDF processed successfully"
                }
            else:
                return {
                    "filename": filename,
                    "status": "processing",
                    "message": "File is still being processed or no data was extracted"
                }
                
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
            
    except Exception as e:
        app_logger.error(f"Error checking upload status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))