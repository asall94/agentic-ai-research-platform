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
from app.services.metrics_service import metrics_service
from app.core.logging_config import StructuredLogger
from app.core.app_insights import track_workflow
from app.api.routes.streaming import stream_workflow_progress
from fastapi.responses import StreamingResponse
from datetime import datetime
import time
import uuid
import json

router = APIRouter()
logger = StructuredLogger(__name__)


@router.post("/reflection", response_model=ReflectionWorkflowResponse)
async def execute_reflection_workflow(request: ReflectionWorkflowRequest):
    """Execute simple reflection workflow (Q2)"""
    
    workflow_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        logger.info(
            "Starting reflection workflow",
            workflow_id=workflow_id,
            workflow_type="simple_reflection",
            topic=request.topic
        )
        
        # Check cache
        cached_result = cache_service.get_cached_result(request.topic, "reflection")
        if cached_result:
            execution_time = time.time() - start_time
            
            # Track cache hit in Application Insights
            track_workflow("simple_reflection", execution_time, cache_hit=True)
            
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
        
        # Track metrics
        metrics_service.track_workflow(
            workflow_type="simple_reflection",
            topic=request.topic,
            execution_time=execution_time,
            cache_hit=False,
            steps_count=3,
            agents_used=["draft", "reflection", "revision"]
        )
        
        # Track in Application Insights
        track_workflow("simple_reflection", execution_time, cache_hit=False)
        
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


@router.get("/reflection/stream")
async def stream_reflection_workflow(topic: str, draft_model: str = None, reflection_model: str = None, revision_model: str = None):
    """Stream reflection workflow with real-time progress events"""
    
    # Validate topic
    topic = topic.strip()
    if not topic:
        async def error_stream():
            yield "data: " + json.dumps({"type": "error", "message": "Topic cannot be empty"}) + "\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")
    if len(topic) > 500:
        async def error_stream():
            yield "data: " + json.dumps({"type": "error", "message": "Topic must be 500 characters or less"}) + "\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")
    
    workflow = SimpleReflectionWorkflow(
        draft_model=draft_model,
        reflection_model=reflection_model,
        revision_model=revision_model
    )
    
    return StreamingResponse(
        stream_workflow_progress("simple_reflection", topic, workflow, cache_service),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/tool-research/stream")
async def stream_tool_research_workflow(topic: str, tools: str = "arxiv,wikipedia,tavily", model: str = None, max_results: int = 3):
    """Stream tool research workflow with real-time progress events"""
    
    # Validate topic
    topic = topic.strip()
    if not topic:
        async def error_stream():
            yield "data: " + json.dumps({"type": "error", "message": "Topic cannot be empty"}) + "\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")
    if len(topic) > 500:
        async def error_stream():
            yield "data: " + json.dumps({"type": "error", "message": "Topic must be 500 characters or less"}) + "\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")
    
    tools_list = [t.strip() for t in tools.split(",")]
    
    workflow = ToolResearchWorkflow(
        model=model,
        tools=tools_list,
        max_results=max_results
    )
    
    return StreamingResponse(
        stream_workflow_progress("tool_research", topic, workflow, cache_service, tools=tools_list),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/multi-agent/stream")
async def stream_multi_agent_workflow(topic: str, max_steps: int = 4, model: str = None):
    """Stream multi-agent workflow with real-time progress events"""
    
    # Validate topic
    topic = topic.strip()
    if not topic:
        async def error_stream():
            yield "data: " + json.dumps({"type": "error", "message": "Topic cannot be empty"}) + "\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")
    if len(topic) > 500:
        async def error_stream():
            yield "data: " + json.dumps({"type": "error", "message": "Topic must be 500 characters or less"}) + "\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")
    
    workflow = MultiAgentWorkflow(
        model=model,
        max_steps=max_steps,
        limit_steps=True
    )
    
    return StreamingResponse(
        stream_workflow_progress("multi_agent", topic, workflow, cache_service, max_steps=max_steps),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
