from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.database import get_db
from app.models import Report, Timeline, Evidence
from app.services.openai_service import OpenAIService
from app.utils.logger import app_logger

router = APIRouter()
openai_service = OpenAIService()

class ReportResponse(BaseModel):
    id: int
    title: str
    content: str
    timeline_id: Optional[int] = None
    created_at: str

@router.post("/report/generate", summary="Generate comprehensive report")
async def generate_report(
    background_tasks: BackgroundTasks,
    timeline_id: int,
    title: str = "Legal Report: Contract Dispute Analysis",
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a comprehensive legal report based on timeline and evidence analysis.
    
    The report will be generated asynchronously in the background and saved to the database.
    """
    try:
        # Check if timeline exists
        timeline_query = select(Timeline).where(Timeline.id == timeline_id)
        timeline_result = await db.execute(timeline_query)
        timeline = timeline_result.scalars().first()
        
        if not timeline:
            raise HTTPException(status_code=404, detail=f"Timeline with ID {timeline_id} not found")
        
        # Create report record
        new_report = Report(
            title=title,
            content="Generating report... This may take a few minutes.",
            timeline_id=timeline_id
        )
        db.add(new_report)
        await db.commit()
        await db.refresh(new_report)
        
        report_id = new_report.id
        app_logger.info(f"Created report with ID {report_id}")
        
        # Start background task to generate report
        async def generate_report_task():
            try:
                # Get timeline data
                timeline_query = select(Timeline).where(Timeline.id == timeline_id)
                timeline_result = await db.execute(timeline_query)
                timeline = timeline_result.scalars().first()
                
                # Get timeline events
                from app.models import TimelineEvent
                events_query = select(TimelineEvent).where(TimelineEvent.timeline_id == timeline_id).order_by(TimelineEvent.date)
                events_result = await db.execute(events_query)
                events = events_result.scalars().all()
                
                # Format timeline data
                timeline_data = {
                    "title": timeline.title,
                    "overview": timeline.description,
                    "events": [
                        {
                            "date": event.date.isoformat() if event.date else None,
                            "title": event.title,
                            "description": event.description,
                            "source": f"{event.source_type}:{event.source_id}"
                        }
                        for event in events
                    ]
                }
                
                # Get evidence data
                evidence_query = select(Evidence)
                evidence_result = await db.execute(evidence_query)
                evidence_list = evidence_result.scalars().all()
                
                # Format evidence data
                evidence_data = {
                    "recommended_evidence": [
                        {
                            "source_type": evidence.source_type,
                            "source_id": evidence.source_id,
                            "title": evidence.title,
                            "description": evidence.description,
                            "relevance": evidence.relevance,
                            "importance": "High"  # Default to high importance
                        }
                        for evidence in evidence_list
                    ]
                }
                
                # Generate report using OpenAI
                report_data = await openai_service.generate_report(timeline_data, evidence_data)
                
                # Update report with generated content
                async with AsyncSession(bind=db.get_bind()) as session:
                    report = await session.get(Report, report_id)
                    if report:
                        # Format report content
                        content = []
                        
                        if "title" in report_data:
                            content.append(f"# {report_data['title']}\n\n")
                        
                        if "executive_summary" in report_data:
                            content.append(f"## Executive Summary\n\n{report_data['executive_summary']}\n\n")
                            
                        if "background" in report_data:
                            content.append(f"## Background and Context\n\n{report_data['background']}\n\n")
                            
                        if "timeline" in report_data:
                            content.append("## Timeline of Key Events\n\n")
                            for event in report_data["timeline"]:
                                date = event.get("date", "Unknown date")
                                event_title = event.get("event", "Untitled event")
                                significance = event.get("significance", "")
                                content.append(f"### {date}: {event_title}\n\n{significance}\n\n")
                                
                        if "key_issues" in report_data:
                            content.append("## Analysis of Key Issues\n\n")
                            for issue in report_data["key_issues"]:
                                issue_title = issue.get("issue", "Untitled issue")
                                analysis = issue.get("analysis", "")
                                content.append(f"### {issue_title}\n\n{analysis}\n\n")
                                
                                if "supporting_evidence" in issue:
                                    content.append("**Supporting Evidence:**\n\n")
                                    for evidence_id in issue["supporting_evidence"]:
                                        content.append(f"- Evidence ID: {evidence_id}\n")
                                    content.append("\n")
                                    
                        if "evidence_evaluation" in report_data:
                            content.append(f"## Evaluation of Evidence\n\n{report_data['evidence_evaluation']}\n\n")
                            
                        if "legal_implications" in report_data:
                            content.append(f"## Legal Implications\n\n{report_data['legal_implications']}\n\n")
                            
                        if "recommendations" in report_data:
                            content.append("## Recommendations\n\n")
                            for recommendation in report_data["recommendations"]:
                                content.append(f"- {recommendation}\n")
                            content.append("\n")
                            
                        if "conclusion" in report_data:
                            content.append(f"## Conclusion\n\n{report_data['conclusion']}\n\n")
                            
                        if "appendix" in report_data and "recommended_evidence_details" in report_data["appendix"]:
                            content.append("## Appendix: Recommended Evidence Details\n\n")
                            for evidence in report_data["appendix"]["recommended_evidence_details"]:
                                evidence_id = evidence.get("id", "Unknown")
                                evidence_type = evidence.get("type", "Unknown")
                                description = evidence.get("description", "")
                                relevance = evidence.get("relevance", "")
                                content.append(f"### Evidence {evidence_id} ({evidence_type})\n\n**Description:** {description}\n\n**Relevance:** {relevance}\n\n")
                        
                        # Update report content
                        report.content = "".join(content)
                        await session.commit()
                        app_logger.info(f"Report generation completed for report ID {report_id}")
                
            except Exception as e:
                app_logger.error(f"Error generating report: {str(e)}")
                # Update report with error message
                async with AsyncSession(bind=db.get_bind()) as session:
                    report = await session.get(Report, report_id)
                    if report:
                        report.content = f"Error generating report: {str(e)}"
                        await session.commit()
        
        background_tasks.add_task(generate_report_task)
        
        return {
            "id": report_id,
            "status": "processing",
            "message": "Report generation started. This may take a few minutes."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error initiating report generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/report/{report_id}", summary="Get report by ID", response_model=ReportResponse)
async def get_report(report_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get a specific report by its ID.
    """
    try:
        query = select(Report).where(Report.id == report_id)
        result = await db.execute(query)
        report = result.scalars().first()
        
        if not report:
            raise HTTPException(status_code=404, detail=f"Report with ID {report_id} not found")
        
        return ReportResponse(
            id=report.id,
            title=report.title,
            content=report.content,
            timeline_id=report.timeline_id,
            created_at=report.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error retrieving report {report_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports", summary="Get all reports")
async def get_reports(db: AsyncSession = Depends(get_db)):
    """
    Get all reports.
    """
    try:
        query = select(Report).order_by(Report.created_at.desc())
        result = await db.execute(query)
        reports = result.scalars().all()
        
        return [
            {
                "id": report.id,
                "title": report.title,
                "timeline_id": report.timeline_id,
                "created_at": report.created_at.isoformat()
            }
            for report in reports
        ]
        
    except Exception as e:
        app_logger.error(f"Error retrieving reports: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/report/{report_id}", summary="Delete report")
async def delete_report(report_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a specific report.
    """
    try:
        # Check if report exists
        report = await db.get(Report, report_id)
        if not report:
            raise HTTPException(status_code=404, detail=f"Report with ID {report_id} not found")
        
        # Delete report
        await db.delete(report)
        await db.commit()
        
        return {"message": f"Report with ID {report_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error deleting report {report_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))