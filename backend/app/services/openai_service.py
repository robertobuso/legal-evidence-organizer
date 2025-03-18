import json
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from app.config import OPENAI_API_KEY
from app.utils.logger import app_logger

class OpenAIService:
    def __init__(self):
        self.model_name = "gpt-4"
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=0.2,
            openai_api_key=OPENAI_API_KEY
        )

    async def analyze_evidence(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze evidence data to identify potential legal issues and recommend evidence.
        
        Args:
            data: Dictionary containing emails, chat logs, PDFs data
            
        Returns:
            Dictionary containing evidence analysis
        """
        try:
            # Format data for the model
            formatted_data = {
                "emails": [
                    {
                        "id": email.id,
                        "sender": email.sender,
                        "recipients": email.recipients,
                        "subject": email.subject,
                        "date": email.date.isoformat() if email.date else None,
                        "snippet": email.body[:500] + "..." if len(email.body) > 500 else email.body
                    } for email in data.get("emails", [])
                ],
                "chat_logs": [
                    {
                        "id": chat.id,
                        "sender": chat.sender,
                        "date_time": chat.date_time.isoformat() if chat.date_time else None,
                        "message": chat.message
                    } for chat in data.get("chat_logs", [])
                ],
                "pdfs": [
                    {
                        "id": pdf.id,
                        "file_name": pdf.file_name,
                        "snippet": pdf.extracted_text[:500] + "..." if len(pdf.extracted_text) > 500 else pdf.extracted_text
                    } for pdf in data.get("pdfs", [])
                ]
            }
            
            data_json = json.dumps(formatted_data, default=str)
            
            # Create analysis prompt
            system_template = """You are a legal expert specializing in contract disputes. Your task is to analyze evidence 
            from various sources to identify potential legal issues and recommend the strongest evidence to build a case."""
            system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
            
            human_template = """I'm preparing for a contract dispute case. I need you to analyze the following evidence 
            from emails, chat logs, and PDF documents to:

            1. Identify potential contract violations, breaches, or other legal issues
            2. Recommend the strongest pieces of evidence to support my case
            3. Explain the relevance and importance of each piece of evidence
            4. Suggest any gaps in evidence or additional information needed

            Here's the evidence data:
            {data_json}

            Present your analysis as a structured JSON with the following format:
            {{
                "summary": "Overall summary of the case based on available evidence",
                "key_issues": [
                    {{
                        "issue": "Description of legal issue",
                        "relevant_evidence": [
                            {{
                                "source_type": "email/chat/pdf",
                                "source_id": 123,
                                "description": "Brief description of the evidence",
                                "relevance": "Why this evidence is important"
                            }}
                        ],
                        "strength": "Assessment of evidence strength for this issue (Strong/Medium/Weak)"
                    }}
                ],
                "recommended_evidence": [
                    {{
                        "source_type": "email/chat/pdf",
                        "source_id": 123,
                        "title": "Short title for this evidence",
                        "description": "Description of the evidence",
                        "relevance": "Detailed explanation of relevance",
                        "importance": "High/Medium/Low"
                    }}
                ],
                "evidence_gaps": ["List of missing evidence or information needed"]
            }}
            """
            human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
            
            chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
            
            # Create and run the chain
            chain = LLMChain(llm=self.llm, prompt=chat_prompt)
            response = await chain.arun(data_json=data_json)
            
            # Parse JSON response
            try:
                analysis = json.loads(response)
                app_logger.info("Successfully analyzed evidence with OpenAI")
                return analysis
            except json.JSONDecodeError:
                app_logger.error("Failed to parse JSON response from OpenAI")
                # Return a basic structure with the raw response
                return {
                    "summary": "Error parsing structured data",
                    "raw_response": response,
                    "key_issues": [],
                    "recommended_evidence": []
                }
            
        except Exception as e:
            app_logger.error(f"Error analyzing evidence with OpenAI: {str(e)}")
            return {
                "summary": f"Error analyzing evidence: {str(e)}",
                "key_issues": [],
                "recommended_evidence": []
            }

    async def generate_report(self, timeline_data: Dict[str, Any], evidence_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive legal report based on timeline and evidence analysis.
        
        Args:
            timeline_data: Timeline data generated by Gemini
            evidence_data: Evidence analysis data generated by OpenAI
            
        Returns:
            Dictionary containing the report
        """
        try:
            # Format input data
            input_data = {
                "timeline": timeline_data,
                "evidence": evidence_data
            }
            
            input_json = json.dumps(input_data, default=str)
            
            # Create report prompt
            system_template = """You are a legal expert specializing in contract disputes. Your task is to generate 
            a comprehensive legal report based on timeline and evidence analysis."""
            system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
            
            human_template = """Please generate a comprehensive legal report for a contract dispute case based on 
            the provided timeline and evidence analysis. The report should be suitable for presentation to legal counsel 
            and should highlight the strengths and weaknesses of the case.

            Timeline and evidence data:
            {input_json}

            Your report should include:
            1. Executive Summary
            2. Background and Context
            3. Timeline of Key Events
            4. Analysis of Key Issues
            5. Evaluation of Evidence
            6. Legal Implications
            7. Recommendations
            8. Conclusion

            Present your report in a structured format with clear section headings. For the Timeline section, 
            organize events chronologically with dates. For the Evidence section, group related items and explain 
            their relevance to specific legal issues.

            Your response should be structured JSON with the following format:
            {{
                "title": "Legal Report: [Appropriate Title]",
                "executive_summary": "Concise summary of the case and key findings",
                "background": "Background information and context",
                "timeline": [
                    {{
                        "date": "YYYY-MM-DD",
                        "event": "Description of event",
                        "significance": "Legal significance"
                    }}
                ],
                "key_issues": [
                    {{
                        "issue": "Description of legal issue",
                        "analysis": "Legal analysis",
                        "supporting_evidence": ["List of evidence IDs that support this issue"]
                    }}
                ],
                "evidence_evaluation": "Evaluation of the overall evidence",
                "legal_implications": "Analysis of legal implications",
                "recommendations": ["List of recommendations"],
                "conclusion": "Concluding remarks",
                "appendix": {{
                    "recommended_evidence_details": [
                        {{
                            "id": "Source ID",
                            "type": "email/chat/pdf",
                            "description": "Evidence description",
                            "relevance": "Relevance explanation"
                        }}
                    ]
                }}
            }}
            """
            human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
            
            chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
            
            # Create and run the chain
            chain = LLMChain(llm=self.llm, prompt=chat_prompt)
            response = await chain.arun(input_json=input_json)
            
            # Parse JSON response
            try:
                report = json.loads(response)
                app_logger.info("Successfully generated legal report with OpenAI")
                return report
            except json.JSONDecodeError:
                app_logger.error("Failed to parse JSON response from OpenAI")
                # Return a basic structure with the raw response
                return {
                    "title": "Legal Report",
                    "executive_summary": "Error parsing structured data",
                    "raw_response": response
                }
            
        except Exception as e:
            app_logger.error(f"Error generating report with OpenAI: {str(e)}")
            return {
                "title": "Legal Report",
                "executive_summary": f"Error generating report: {str(e)}"
            }