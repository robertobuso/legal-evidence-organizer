import json
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from app.config import GOOGLE_API_KEY
from app.utils.logger import app_logger

class GeminiService:
    def __init__(self):
        # Configure the API
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model_name = "gemini-1.0-pro"  # Use the latest available model
        self.llm = ChatGoogleGenerativeAI(model=self.model_name, 
                                          temperature=0.2,
                                          google_api_key=GOOGLE_API_KEY)

    async def generate_summary(self, text: str, max_tokens: int = 250) -> str:
        """
        Generate a concise summary of the provided text using Gemini.
        
        Args:
            text: Text to summarize
            max_tokens: Maximum tokens for the summary
            
        Returns:
            Generated summary
        """
        try:
            # Create summary prompt
            system_template = "You are a helpful assistant that specializes in creating concise summaries of legal documents."
            system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
            
            human_template = """Please provide a concise summary of the following text, focusing on key points relevant 
            to potential legal evidence in a contract dispute. Keep your response under {max_tokens} tokens.
            
            Text to summarize:
            {text}
            """
            human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
            
            chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
            
            # Create and run the chain
            chain = LLMChain(llm=self.llm, prompt=chat_prompt)
            response = await chain.arun(text=text, max_tokens=max_tokens)
            
            app_logger.info("Successfully generated summary with Gemini")
            return response.strip()
            
        except Exception as e:
            app_logger.error(f"Error generating summary with Gemini: {str(e)}")
            return f"Error generating summary: {str(e)}"

    async def generate_timeline(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a timeline of events using Gemini.
        
        Args:
            events: List of event dictionaries containing date, description, and source
            
        Returns:
            Dictionary containing timeline data
        """
        try:
            # Format events data for the model
            events_json = json.dumps(events, default=str)
            
            # Create timeline prompt
            system_template = """You are a legal assistant specializing in organizing evidence for contract disputes.
            Your task is to analyze events and create a well-structured timeline."""
            system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
            
            human_template = """Based on the following events related to a contract dispute, please create a coherent timeline.
            Identify key turning points, important communications, and potential evidence of contract violations.
            
            For each significant event, include:
            1. The date
            2. A clear title for the event
            3. A brief description of what happened
            4. The relevance to the potential legal case
            
            Events data (JSON format):
            {events_json}
            
            Present your response as a structured timeline in JSON format with the following structure:
            {{
                "title": "Timeline of Contract Dispute",
                "overview": "Brief overview of the timeline and key patterns",
                "events": [
                    {{
                        "date": "YYYY-MM-DD",
                        "title": "Event title",
                        "description": "Event description",
                        "relevance": "Legal relevance",
                        "source": "Source information"
                    }},
                    ...
                ]
            }}
            """
            human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
            
            chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
            
            # Create and run the chain
            chain = LLMChain(llm=self.llm, prompt=chat_prompt)
            response = await chain.arun(events_json=events_json)
            
            # Parse JSON response
            try:
                timeline_data = json.loads(response)
                app_logger.info("Successfully generated timeline with Gemini")
                return timeline_data
            except json.JSONDecodeError:
                app_logger.error("Failed to parse JSON response from Gemini")
                # Return a basic structure with the raw response
                return {
                    "title": "Timeline of Contract Dispute",
                    "overview": "Error parsing structured data",
                    "raw_response": response,
                    "events": []
                }
            
        except Exception as e:
            app_logger.error(f"Error generating timeline with Gemini: {str(e)}")
            return {
                "title": "Timeline of Contract Dispute",
                "overview": f"Error generating timeline: {str(e)}",
                "events": []
            }

    async def extract_key_info_from_pdf(self, pdf_text: str) -> Dict[str, Any]:
        """
        Extract key information from PDF text using Gemini.
        
        Args:
            pdf_text: Extracted text from PDF
            
        Returns:
            Dictionary containing extracted information
        """
        try:
            system_template = """You are a legal assistant specializing in analyzing invoices and contracts.
            Your task is to extract key information from PDF documents related to a contract dispute."""
            system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
            
            human_template = """Extract key information from the following PDF text that might be relevant to a contract dispute.
            Focus on dates, amounts, parties involved, services/products, payment terms, and any unusual elements.
            
            PDF text:
            {pdf_text}
            
            Present your response as a structured JSON with the following fields:
            {{
                "document_type": "Type of document (invoice, contract, letter, etc.)",
                "parties": ["List of parties mentioned"],
                "dates": ["List of relevant dates with context"],
                "amounts": ["List of monetary amounts with context"],
                "key_terms": ["List of important terms or conditions"],
                "potential_issues": ["List of potential issues or irregularities"],
                "summary": "Brief summary of the document"
            }}
            """
            human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
            
            chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
            
            # Create and run the chain
            chain = LLMChain(llm=self.llm, prompt=chat_prompt)
            response = await chain.arun(pdf_text=pdf_text)
            
            # Parse JSON response
            try:
                extracted_info = json.loads(response)
                app_logger.info("Successfully extracted key info from PDF with Gemini")
                return extracted_info
            except json.JSONDecodeError:
                app_logger.error("Failed to parse JSON response from Gemini")
                # Return a basic structure with the raw response
                return {
                    "document_type": "Unknown",
                    "summary": "Error parsing structured data",
                    "raw_response": response
                }
            
        except Exception as e:
            app_logger.error(f"Error extracting info from PDF with Gemini: {str(e)}")
            return {
                "document_type": "Unknown",
                "summary": f"Error extracting information: {str(e)}"
            }