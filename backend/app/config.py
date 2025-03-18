import os
from dotenv import load_dotenv

load_dotenv()

# Application settings
APP_NAME = "Legal Evidence Organizer"
APP_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Database settings
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./legal_evidence.db")

# File storage settings
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
PDF_UPLOAD_DIR = os.path.join(UPLOAD_DIR, "pdfs")
CHAT_UPLOAD_DIR = os.path.join(UPLOAD_DIR, "chats")

# API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Gmail API settings
GMAIL_CREDENTIALS_FILE = os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json")
GMAIL_TOKEN_FILE = os.getenv("GMAIL_TOKEN_FILE", "token.json")
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Date range for email fetching
EMAIL_START_DATE = "2023-01-01"
EMAIL_END_DATE = "2025-03-18"

# Create upload directories if they don't exist
os.makedirs(PDF_UPLOAD_DIR, exist_ok=True)
os.makedirs(CHAT_UPLOAD_DIR, exist_ok=True)