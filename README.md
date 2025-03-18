# Legal Evidence Organizer

A comprehensive application for organizing and analyzing legal evidence related to contract disputes. This application ingests data from various sources, including Gmail emails, WhatsApp chat logs, and PDF invoices, and leverages LLMs to generate timelines and recommend evidence.

## Features

- Upload and process WhatsApp chat logs (.txt) and PDF invoices (.pdf)
- Fetch emails from Gmail using the Gmail API
- Search across all data sources with filtering options
- Generate timelines of events using Google Gemini API
- Analyze and recommend evidence using OpenAI GPT-4
- Generate comprehensive legal reports
- User-friendly interface built with Next.js and Tailwind CSS

## System Architecture

- **Frontend**: Next.js with Tailwind CSS
- **Backend**: FastAPI with Python
- **Database**: SQLite for local data storage
- **LLM Integration**: Google Gemini API and OpenAI API
- **Integration Tools**: LangChain for LLM API interactions

## Setup and Installation

### Prerequisites

- Python 3.9+
- Node.js 16+
- OpenAI API Key
- Google API Key with access to Gemini API
- Gmail API credentials

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key
```

For Gmail API integration, you'll need to place `credentials.json` in the backend directory.

### Using Docker (Recommended)

1. Build and start the containers:

```bash
docker-compose up -d
```

2. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/docs

### Manual Setup

#### Backend

1. Navigate to the backend directory:

```bash
cd backend
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the FastAPI server:

```bash
uvicorn app.main:app --reload
```

#### Frontend

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Run the development server:

```bash
npm run dev
```

## Usage Guide

### 1. Upload Data

- **WhatsApp Chat Logs**: Export a WhatsApp chat and upload the .txt file
- **PDF Invoices**: Upload PDF invoices related to the contract
- **Gmail Emails**: Enter email addresses and date range to fetch emails

### 2. Search Evidence

Use the search functionality to find specific information across all data sources.

### 3. Generate Timeline

Generate a timeline of events to visualize the chronology of the contract dispute.

### 4. Analyze Evidence

Run the evidence analysis to get AI-powered recommendations on the strongest pieces of evidence for your case.

### 5. Generate Report

Create a comprehensive legal report that combines the timeline and evidence analysis.

## API Documentation

The backend API documentation is available at http://localhost:8000/docs when the server is running.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [Next.js](https://nextjs.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [LangChain](https://www.langchain.com/)
- [OpenAI API](https://openai.com/api/)
- [Google Gemini API](https://ai.google.dev/)
