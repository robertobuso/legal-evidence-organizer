import os
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import PyPDF2

from app.models import PDFDocument
from app.config import PDF_UPLOAD_DIR
from app.utils.logger import app_logger

class PDFService:
    def __init__(self):
        pass

    async def process_pdf_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Extract text from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted text and file info or None if processing fails
        """
        try:
            file_name = os.path.basename(file_path)
            
            # Extract text from PDF
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                
                # Extract text from each page
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text += page.extract_text() + "\n\n"
            
            pdf_data = {
                'file_name': file_name,
                'extracted_text': text,
                'file_path': file_path
            }
            
            app_logger.info(f"Successfully processed PDF: {file_name}")
            return pdf_data
            
        except Exception as e:
            app_logger.error(f"Error processing PDF file: {str(e)}")
            return None

    async def save_pdf_document(self, db: AsyncSession, pdf_data: Dict[str, Any]) -> Optional[PDFDocument]:
        """
        Save PDF document info to database.
        
        Args:
            db: Database session
            pdf_data: Dictionary containing PDF data
            
        Returns:
            Saved PDFDocument object or None if save fails
        """
        try:
            # Check if PDF already exists in DB
            stmt = select(PDFDocument).where(PDFDocument.file_path == pdf_data['file_path'])
            result = await db.execute(stmt)
            existing_pdf = result.scalars().first()
            
            if existing_pdf:
                app_logger.info(f"PDF {pdf_data['file_name']} already exists in database")
                return existing_pdf
            
            # Create new PDF document record
            new_pdf = PDFDocument(
                file_name=pdf_data['file_name'],
                extracted_text=pdf_data['extracted_text'],
                file_path=pdf_data['file_path']
            )
            
            db.add(new_pdf)
            await db.commit()
            await db.refresh(new_pdf)
            
            app_logger.info(f"Saved PDF document to database: {pdf_data['file_name']}")
            return new_pdf
            
        except Exception as e:
            await db.rollback()
            app_logger.error(f"Error saving PDF document: {str(e)}")
            return None

    async def get_pdf_documents(self, db: AsyncSession, filters: Dict[str, Any] = None) -> List[PDFDocument]:
        """
        Get PDF documents from database with optional filters.
        
        Args:
            db: Database session
            filters: Dictionary of filter parameters
            
        Returns:
            List of PDFDocument objects
        """
        query = select(PDFDocument)
        
        if filters:
            if 'file_name' in filters and filters['file_name']:
                query = query.where(PDFDocument.file_name.ilike(f"%{filters['file_name']}%"))
            
            if 'content' in filters and filters['content']:
                query = query.where(PDFDocument.extracted_text.ilike(f"%{filters['content']}%"))
        
        result = await db.execute(query)
        documents = result.scalars().all()
        
        return list(documents)