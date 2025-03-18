import os
import base64
import pickle
from datetime import datetime
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import email
from email.utils import parseaddr, parsedate_to_datetime
from typing import List, Dict, Any, Optional

from app.config import GMAIL_CREDENTIALS_FILE, GMAIL_TOKEN_FILE, GMAIL_SCOPES
from app.models import Email
from app.utils.logger import app_logger

class EmailService:
    def __init__(self):
        self.creds = None
        self.service = None

    async def authenticate(self):
        """Authenticate with Gmail API."""
        try:
            # Check if token file exists
            if os.path.exists(GMAIL_TOKEN_FILE):
                with open(GMAIL_TOKEN_FILE, 'rb') as token:
                    self.creds = pickle.load(token)

            # If credentials don't exist or are invalid, get new ones
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        GMAIL_CREDENTIALS_FILE, GMAIL_SCOPES)
                    self.creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(GMAIL_TOKEN_FILE, 'wb') as token:
                    pickle.dump(self.creds, token)

            self.service = build('gmail', 'v1', credentials=self.creds)
            app_logger.info("Successfully authenticated with Gmail API")
            return True
        except Exception as e:
            app_logger.error(f"Gmail authentication error: {str(e)}")
            return False

    async def fetch_emails(self, email_addresses: List[str], start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch emails from specified addresses within date range."""
        if not self.service:
            success = await self.authenticate()
            if not success:
                app_logger.error("Failed to authenticate with Gmail API")
                return []

        try:
            # Create query for Gmail API
            query_parts = []
            
            # Add email addresses to query
            address_query = []
            for email_addr in email_addresses:
                address_query.append(f"from:{email_addr}")
                address_query.append(f"to:{email_addr}")
                address_query.append(f"cc:{email_addr}")
                address_query.append(f"bcc:{email_addr}")
            
            query_parts.append(f"({' OR '.join(address_query)})")
            
            # Add date range to query
            if start_date:
                query_parts.append(f"after:{start_date}")
            if end_date:
                query_parts.append(f"before:{end_date}")
            
            query = " ".join(query_parts)
            app_logger.info(f"Gmail API query: {query}")
            
            # Execute query
            results = self.service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])
            
            # Fetch full email details for each message
            emails = []
            for message in messages:
                msg = self.service.users().messages().get(userId='me', id=message['id']).execute()
                email_data = self._parse_message(msg)
                emails.append(email_data)
            
            app_logger.info(f"Fetched {len(emails)} emails from Gmail")
            return emails
        except Exception as e:
            app_logger.error(f"Error fetching emails: {str(e)}")
            return []

    def _parse_message(self, msg: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Gmail message into structured data."""
        email_data = {
            'email_id': msg['id'],
            'sender': '',
            'recipients': '',
            'subject': '',
            'date': None,
            'body': ''
        }
        
        # Process headers
        headers = msg['payload']['headers']
        for header in headers:
            name = header['name'].lower()
            if name == 'from':
                email_data['sender'] = header['value']
            elif name == 'to':
                email_data['recipients'] = header['value']
            elif name == 'subject':
                email_data['subject'] = header['value']
            elif name == 'date':
                try:
                    email_data['date'] = parsedate_to_datetime(header['value'])
                except:
                    # Handle parsing errors
                    email_data['date'] = datetime.utcnow()
        
        # Extract body
        if 'parts' in msg['payload']:
            for part in msg['payload']['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    body_data = part['body']['data']
                    body_text = base64.urlsafe_b64decode(body_data).decode('utf-8')
                    email_data['body'] = body_text
                    break
        elif 'body' in msg['payload'] and 'data' in msg['payload']['body']:
            body_data = msg['payload']['body']['data']
            body_text = base64.urlsafe_b64decode(body_data).decode('utf-8')
            email_data['body'] = body_text
        
        return email_data

    async def save_emails(self, db: AsyncSession, emails: List[Dict[str, Any]]) -> List[Email]:
        """Save fetched emails to database."""
        saved_emails = []
        
        for email_data in emails:
            # Check if email already exists in DB
            stmt = select(Email).where(Email.email_id == email_data['email_id'])
            result = await db.execute(stmt)
            existing_email = result.scalars().first()
            
            if existing_email:
                app_logger.info(f"Email {email_data['email_id']} already exists in database")
                saved_emails.append(existing_email)
                continue
            
            # Create new email record
            new_email = Email(
                email_id=email_data['email_id'],
                sender=email_data['sender'],
                recipients=email_data['recipients'],
                subject=email_data['subject'],
                date=email_data['date'],
                body=email_data['body']
            )
            
            db.add(new_email)
            saved_emails.append(new_email)
        
        await db.commit()
        app_logger.info(f"Saved {len(saved_emails)} emails to database")
        return saved_emails