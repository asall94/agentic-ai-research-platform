from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    ReflectionWorkflowRequest,
    ReflectionWorkflowResponse,
    ToolResearchWorkflowRequest,
    ToolResearchWorkflowResponse,
    MultiAgentWorkflowRequest,
    MultiAgentWorkflowResponse
)
from app.workflows.simple_reflection import SimpleReflectionWorkflow
from app.workflows.tool_research import ToolResearchWorkflow
from app.workflows.multi_agent import MultiAgentWorkflow
from app.services.cache_service import cache_service
from datetime import datetime
import time
import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/reflection", response_model=ReflectionWorkflowResponse)
async def execute_reflection_workflow(request: ReflectionWorkflowRequest):
    """Execute simple reflection workflow (Q2)"""
    
    workflow_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        logger.info(f"Starting reflection workflow {workflow_id} for topic: {request.topic}")
        
        # Check cache
        cached_result = cache_service.get_cached_result(request.topic, "reflection")
        if cached_result:
            execution_time = time.time() - start_time
            return ReflectionWorkflowResponse(
                workflow_id=workflow_id,
                workflow_type="simple_reflection",
                topic=request.topic,
                status="completed",
                created_at=datetime.now(),
                execution_time=execution_time,
                result=cached_result,
                draft=cached_result["draft"],
                reflection=cached_result["reflection"],
                revised=cached_result["revised"]
            )
        
        workflow = SimpleReflectionWorkflow(
            draft_model=request.draft_model,
            reflection_model=request.reflection_model,
            revision_model=request.revision_model
        )
        
        result = await workflow.execute(request.topic)
        execution_time = time.time() - start_time
        
        # Store in cache
        cache_service.store_result(request.topic, "reflection", result)
        
        return ReflectionWorkflowResponse(
            workflow_id=workflow_id,
            workflow_type="simple_reflection",
            topic=request.topic,
            status="completed",
            created_at=datetime.now(),
            execution_time=execution_time,
            result=result,
            draft=result["draft"],
            reflection=result["reflection"],
            revised=result["revised"]
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Reflection workflow {workflow_id} failed: {e}")
        
        return ReflectionWorkflowResponse(
            workflow_id=workflow_id,
            workflow_type="simple_reflection",
            topic=request.topic,
            status="failed",
            created_at=datetime.now(),
            execution_time=execution_time,
            result={},
            draft="",
            reflection="",
            revised="",
            error=str(e)
        )


@router.post("/tool-research", response_model=ToolResearchWorkflowResponse)
async def execute_tool_research_workflow(request: ToolResearchWorkflowRequest):
    """Execute tool-enhanced research workflow (Q3)"""
    
    workflow_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        logger.info(f"Starting tool research workflow {workflow_id} for topic: {request.topic}")
        
        # Check cache
        cached_result = cache_service.get_cached_result(request.topic, "tool_research")
        if cached_result:
            execution_time = time.time() - start_time
            return ToolResearchWorkflowResponse(
                workflow_id=workflow_id,
                workflow_type="tool_research",
                topic=request.topic,
                status="completed",
                created_at=datetime.now(),
                execution_time=execution_time,
                result=cached_result,
                research_report=cached_result.get("research_report", ""),
                reflection=cached_result.get("reflection"),
                revised_report=cached_result.get("revised_report"),
                html_output=cached_result.get("html_output"),
                sources=cached_result.get("sources", [])
            )
        
        workflow = ToolResearchWorkflow(
            model=request.model,
            tools=request.tools,
            max_results=request.max_results
        )
        
        result = await workflow.execute(request.topic, export_format=request.export_format)
        execution_time = time.time() - start_time
        
        # Store in cache
        cache_service.store_result(request.topic, "tool_research", result)
        
        return ToolResearchWorkflowResponse(
            workflow_id=workflow_id,
            workflow_type="tool_research",
            topic=request.topic,
            status="completed",
            created_at=datetime.now(),
            execution_time=execution_time,
            result=result,
            research_report=result.get("research_report", ""),
            reflection=result.get("reflection"),
            revised_report=result.get("revised_report"),
            html_output=result.get("html_output"),
            sources=result.get("sources", [])
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Tool research workflow {workflow_id} failed: {e}")
        
        return ToolResearchWorkflowResponse(
            workflow_id=workflow_id,
            workflow_type="tool_research",
            topic=request.topic,
            status="failed",
            created_at=datetime.now(),
            execution_time=execution_time,
            result={},
            research_report="",
            error=str(e)
        )


@router.post("/multi-agent", response_model=MultiAgentWorkflowResponse)
async def execute_multi_agent_workflow(request: MultiAgentWorkflowRequest):
    """Execute multi-agent workflow (Q5)"""
    
    workflow_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        logger.info(f"Starting multi-agent workflow {workflow_id} for topic: {request.topic}")
        
        # Check cache
        cached_result = cache_service.get_cached_result(request.topic, "multi_agent")
        if cached_result:
            execution_time = time.time() - start_time
            return MultiAgentWorkflowResponse(
                workflow_id=workflow_id,
                workflow_type="multi_agent",
                topic=request.topic,
                status="completed",
                created_at=datetime.now(),
                execution_time=execution_time,
                result=cached_result,
                plan=cached_result.get("plan", []),
                execution_history=cached_result.get("history", []),
                final_report=cached_result.get("final_report", "")
            )
        
        workflow = MultiAgentWorkflow(
            model=request.model,
            max_steps=request.max_steps,
            limit_steps=request.limit_steps
        )
        
        result = await workflow.execute(request.topic)
        execution_time = time.time() - start_time
        
        # Store in cache
        cache_service.store_result(request.topic, "multi_agent", result)
        
        return MultiAgentWorkflowResponse(
            workflow_id=workflow_id,
            workflow_type="multi_agent",
            topic=request.topic,
            status="completed",
            created_at=datetime.now(),
            execution_time=execution_time,
            result=result,
            plan=result.get("plan", []),
            execution_history=result.get("history", []),
            final_report=result.get("final_report", "")
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Multi-agent workflow {workflow_id} failed: {e}")
        
        return MultiAgentWorkflowResponse(
            workflow_id=workflow_id,
            workflow_type="multi_agent",
            topic=request.topic,
            status="failed",
            created_at=datetime.now(),
            execution_time=execution_time,
            result={},
            plan=[],
            execution_history=[],
            final_report="",
            error=str(e)
        )
