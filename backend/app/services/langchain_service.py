from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import OPENAI_API_KEY, GOOGLE_API_KEY
from app.utils.logger import app_logger

class LangChainService:
    def __init__(self):
        self.openai_llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.2,
            openai_api_key=OPENAI_API_KEY
        )
        
        self.gemini_llm = ChatGoogleGenerativeAI(
            model="gemini-1.0-pro",
            temperature=0.2,
            google_api_key=GOOGLE_API_KEY
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,
            chunk_overlap=200
        )

    def _create_documents_from_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Document]:
        """
        Split text into documents for processing with LangChain.
        
        Args:
            text: Text to split
            metadata: Optional metadata to attach to documents
            
        Returns:
            List of Document objects
        """
        if metadata is None:
            metadata = {}
            
        texts = self.text_splitter.split_text(text)
        return [Document(page_content=t, metadata=metadata) for t in texts]

    def _create_documents_from_data(self, data_list: List[Dict[str, Any]], content_key: str, 
                                   date_key: Optional[str] = None) -> List[Document]:
        """
        Create documents from a list of data dictionaries.
        
        Args:
            data_list: List of data dictionaries
            content_key: Key for the content field in each dictionary
            date_key: Optional key for date field for sorting
            
        Returns:
            List of Document objects sorted by date if date_key is provided
        """
        # Sort by date if date_key is provided
        if date_key:
            sorted_data = sorted(
                data_list, 
                key=lambda x: x.get(date_key, datetime.min) if x.get(date_key) else datetime.min
            )
        else:
            sorted_data = data_list
            
        documents = []
        for item in sorted_data:
            content = item.get(content_key, "")
            # Create a copy of the item dict for metadata
            metadata = {k: v for k, v in item.items() if k != content_key}
            documents.append(Document(page_content=content, metadata=metadata))
            
        return documents

    async def summarize_documents(self, documents: List[Document], use_openai: bool = True, 
                                 prompt_template: str = None) -> str:
        """
        Summarize a list of documents.
        
        Args:
            documents: List of Document objects
            use_openai: Whether to use OpenAI (True) or Gemini (False)
            prompt_template: Optional custom prompt template
            
        Returns:
            Summary text
        """
        try:
            llm = self.openai_llm if use_openai else self.gemini_llm
            
            if prompt_template:
                prompt = PromptTemplate.from_template(prompt_template)
                chain = load_summarize_chain(
                    llm=llm,
                    chain_type="map_reduce",
                    map_prompt=prompt,
                    combine_prompt=prompt
                )
            else:
                chain = load_summarize_chain(
                    llm=llm,
                    chain_type="map_reduce"
                )
                
            summary = await chain.arun(documents)
            return summary
            
        except Exception as e:
            app_logger.error(f"Error summarizing documents: {str(e)}")
            return f"Error generating summary: {str(e)}"

    async def extract_entities(self, text: str, entity_types: List[str]) -> Dict[str, List[str]]:
        """
        Extract entities of specified types from text.
        
        Args:
            text: Text to extract entities from
            entity_types: List of entity types to extract (e.g., ["people", "organizations", "dates"])
            
        Returns:
            Dictionary mapping entity types to lists of extracted entities
        """
        try:
            prompt_template = """Extract all {entity_type} mentioned in the following text:
            
            Text: {text}
            
            Provide a simple list of {entity_type}, one per line. If none are found, return "None found."
            """
            
            results = {}
            
            for entity_type in entity_types:
                prompt = PromptTemplate.from_template(prompt_template)
                chain = LLMChain(llm=self.gemini_llm, prompt=prompt)
                
                response = await chain.arun(text=text, entity_type=entity_type)
                
                # Process response into a list
                entities = [
                    entity.strip() for entity in response.split('\n')
                    if entity.strip() and entity.strip().lower() != "none found."
                ]
                
                results[entity_type] = entities
                
            return results
            
        except Exception as e:
            app_logger.error(f"Error extracting entities: {str(e)}")
            return {entity_type: [f"Error: {str(e)}"] for entity_type in entity_types}

    async def analyze_temporal_data(self, documents: List[Document]) -> Dict[str, Any]:
        """
        Analyze temporal patterns in document data.
        
        Args:
            documents: List of Document objects with date metadata
            
        Returns:
            Dictionary with temporal analysis
        """
        try:
            # Sort documents by date
            sorted_docs = sorted(
                [doc for doc in documents if doc.metadata.get("date")],
                key=lambda x: x.metadata.get("date", datetime.min)
            )
            
            if not sorted_docs:
                return {"error": "No documents with date metadata found"}
            
            # Create a timeline summary
            date_content_pairs = [
                f"Date: {doc.metadata.get('date').strftime('%Y-%m-%d')} - Content: {doc.page_content[:100]}..."
                for doc in sorted_docs
            ]
            
            timeline_text = "\n\n".join(date_content_pairs)
            
            prompt_template = """Analyze the following timeline of events related to a potential contract dispute.
            Identify patterns, key turning points, and any suspicious or notable changes in communication or behavior.
            
            Timeline:
            {text}
            
            Provide your analysis in the following format:
            
            Key Patterns:
            1. [Pattern 1]
            2. [Pattern 2]
            
            Turning Points:
            1. [Date] - [Description of turning point]
            2. [Date] - [Description of turning point]
            
            Notable Changes:
            1. [Description of change]
            2. [Description of change]
            """
            
            prompt = PromptTemplate.from_template(prompt_template)
            chain = LLMChain(llm=self.openai_llm, prompt=prompt)
            
            analysis = await chain.arun(text=timeline_text)
            
            return {
                "timeline_summary": analysis,
                "document_count": len(sorted_docs),
                "date_range": {
                    "start": sorted_docs[0].metadata.get("date").strftime("%Y-%m-%d"),
                    "end": sorted_docs[-1].metadata.get("date").strftime("%Y-%m-%d")
                }
            }
            
        except Exception as e:
            app_logger.error(f"Error analyzing temporal data: {str(e)}")
            return {"error": f"Error analyzing temporal data: {str(e)}"}

    async def detect_contradictions(self, documents: List[Document]) -> List[Dict[str, Any]]:
        """
        Detect potential contradictions in documents.
        
        Args:
            documents: List of Document objects
            
        Returns:
            List of potential contradictions
        """
        try:
            if len(documents) < 2:
                return []
                
            # Combine documents into a single text
            combined_text = "\n\n---\n\n".join([
                f"Source: {doc.metadata.get('source', 'Unknown')}\n"
                f"Date: {doc.metadata.get('date', 'Unknown')}\n"
                f"Content: {doc.page_content}"
                for doc in documents
            ])
            
            prompt_template = """Carefully review the following documents related to a contract dispute.
            Identify any contradictions, inconsistencies, or statements that conflict with each other.
            
            Documents:
            {text}
            
            List each potential contradiction you find in the following format:
            
            Contradiction 1:
            - Statement A: [quote the first statement]
            - Source A: [source of first statement]
            - Statement B: [quote the contradicting statement]
            - Source B: [source of contradicting statement]
            - Explanation: [explain why these statements contradict each other]
            
            Contradiction 2:
            ...
            
            If you don't find any contradictions, just write "No contradictions found."
            """
            
            prompt = PromptTemplate.from_template(prompt_template)
            chain = LLMChain(llm=self.openai_llm, prompt=prompt)
            
            response = await chain.arun(text=combined_text)
            
            # Parse the response
            if "No contradictions found" in response:
                return []
                
            # Simple parsing of the response
            contradictions = []
            current_contradiction = {}
            
            for line in response.split('\n'):
                line = line.strip()
                
                if line.startswith("Contradiction"):
                    if current_contradiction and "statement_a" in current_contradiction:
                        contradictions.append(current_contradiction)
                    current_contradiction = {"id": len(contradictions) + 1}
                    
                elif line.startswith("- Statement A:"):
                    current_contradiction["statement_a"] = line.replace("- Statement A:", "").strip()
                elif line.startswith("- Source A:"):
                    current_contradiction["source_a"] = line.replace("- Source A:", "").strip()
                elif line.startswith("- Statement B:"):
                    current_contradiction["statement_b"] = line.replace("- Statement B:", "").strip()
                elif line.startswith("- Source B:"):
                    current_contradiction["source_b"] = line.replace("- Source B:", "").strip()
                elif line.startswith("- Explanation:"):
                    current_contradiction["explanation"] = line.replace("- Explanation:", "").strip()
            
            # Add the last contradiction if it exists
            if current_contradiction and "statement_a" in current_contradiction:
                contradictions.append(current_contradiction)
                
            return contradictions
            
        except Exception as e:
            app_logger.error(f"Error detecting contradictions: {str(e)}")
            return [{"error": f"Error detecting contradictions: {str(e)}"}]