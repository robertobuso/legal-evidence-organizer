import os
import re
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import ChatLog
from app.config import CHAT_UPLOAD_DIR
from app.utils.logger import app_logger

class ChatService:
    def __init__(self):
        pass

    async def process_chat_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Process a WhatsApp chat log file and extract structured data.
        
        Args:
            file_path: Path to the WhatsApp chat log file
            
        Returns:
            List of dictionaries containing structured chat messages
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                chat_text = file.read()
            
            # Regular expression to match WhatsApp message format
            # Format: [date, time] sender: message
            pattern = r'\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{1,2}(?::\d{1,2})?\s*(?:AM|PM)?)\]\s*([^:]+):\s*(.*?)(?=\n\[\d{1,2}/\d{1,2}/\d{2,4}|$)'
            
            matches = re.findall(pattern, chat_text, re.DOTALL)
            
            chat_messages = []
            for match in matches:
                date_str, time_str, sender, message = match
                
                # Parse date and time
                try:
                    # Handle different date formats (m/d/y or d/m/y)
                    # First try m/d/y
                    try:
                        date_obj = datetime.strptime(f"{date_str} {time_str}", "%m/%d/%y %H:%M")
                    except ValueError:
                        # Then try d/m/y
                        try:
                            date_obj = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%y %H:%M")
                        except ValueError:
                            # Try with seconds
                            try:
                                date_obj = datetime.strptime(f"{date_str} {time_str}", "%m/%d/%y %H:%M:%S")
                            except ValueError:
                                date_obj = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%y %H:%M:%S")
                except ValueError:
                    app_logger.warning(f"Could not parse date: {date_str} {time_str}, using current time")
                    date_obj = datetime.utcnow()
                
                chat_messages.append({
                    'date_time': date_obj,
                    'sender': sender.strip(),
                    'message': message.strip(),
                    'file_path': file_path
                })
            
            app_logger.info(f"Processed {len(chat_messages)} messages from chat log")
            return chat_messages
            
        except Exception as e:
            app_logger.error(f"Error processing chat file: {str(e)}")
            return []

    async def save_chat_messages(self, db: AsyncSession, chat_messages: List[Dict[str, Any]]) -> List[ChatLog]:
        """
        Save chat messages to database.
        
        Args:
            db: Database session
            chat_messages: List of chat message dictionaries
            
        Returns:
            List of saved ChatLog objects
        """
        saved_messages = []
        
        for message in chat_messages:
            new_message = ChatLog(
                date_time=message['date_time'],
                sender=message['sender'],
                message=message['message'],
                file_path=message['file_path']
            )
            
            db.add(new_message)
            saved_messages.append(new_message)
        
        await db.commit()
        app_logger.info(f"Saved {len(saved_messages)} chat messages to database")
        return saved_messages

    async def get_chat_messages(self, db: AsyncSession, filters: Dict[str, Any] = None) -> List[ChatLog]:
        """
        Get chat messages from database with optional filters.
        
        Args:
            db: Database session
            filters: Dictionary of filter parameters
            
        Returns:
            List of ChatLog objects
        """
        query = select(ChatLog)
        
        if filters:
            if 'sender' in filters and filters['sender']:
                query = query.where(ChatLog.sender.ilike(f"%{filters['sender']}%"))
            
            if 'start_date' in filters and filters['start_date']:
                query = query.where(ChatLog.date_time >= filters['start_date'])
            
            if 'end_date' in filters and filters['end_date']:
                query = query.where(ChatLog.date_time <= filters['end_date'])
            
            if 'content' in filters and filters['content']:
                query = query.where(ChatLog.message.ilike(f"%{filters['content']}%"))
        
        # Order by date
        query = query.order_by(ChatLog.date_time)
        
        result = await db.execute(query)
        messages = result.scalars().all()
        
        return list(messages)